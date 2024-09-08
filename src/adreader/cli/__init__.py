import json
import os
import platform
import shutil
import time
from glob import glob
from pathlib import Path
from time import sleep

import click
import easyocr
import keyboard
import numpy as np
import pyautogui
from dotenv import load_dotenv
from PIL import Image

from adreader.gui import Box, Point
from adreader.utils import chown, make_tarfile, purge_png
from adreader.utils.cache import Cache
from adreader.utils.renderer import reader_txt

load_dotenv()

UID = 501
GID = 20

THINK = float(os.getenv('THINK', 0.0))

PREFIX = '.tmp'
TARGET = '.books'

PREFIX = Path(PREFIX)
TARGET = Path(TARGET)

SAMPLE = (Path(__file__).parent.parent / 'corners/sample.png').absolute()
BUTTON = (Path(__file__).parent.parent / 'corners/button.png').absolute()

if not TARGET.exists():
    TARGET.mkdir()


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


@click.group()
# @click.option('--count', default=1, help='Number of greetings.')
# @click.option('--name', prompt='Your name',
#               help='The person to greet.')
def cli():
    """Simple program that captures screenshots of an adreader"""


@cli.command()
@click.option(
    '-K', '--key',
    help='Key to press to capture coordinates',
    default=lambda *args, **kwargs: 'control+shift' if os.name in ('nt', 'posix') else
    'command+shift', show_default=True)
@click.option('-B', '--button/--no-button',
              is_flag=True, help='Capture coordinates for next button',
              default=False,
              show_default=True)
def coord(key, button):
    """Get coordinates for first page.
    
    Keybind (-K) defaults to  'control+shift' on Windows' else 'command+shift'
    """
    key = 'command+shift' if platform.system() == 'Darwin' else 'control+shift'
    click.echo(
        f"""Instructions
        1. Go to the first page and move the mouse to the top left corner of the image to capture.
        2. Press "the key in -K parameter {key}"
        3. Repeat for the bottom-right corner"""
    )
    keyboard.wait(key)
    top_left = Point(*pyautogui.position())
    click.echo('Now capture the bottom right corner')
    keyboard.wait(key)
    bottom_right = Point(*pyautogui.position())
    box = Box(top_left, bottom_right)

    if button:
        loc = str(BUTTON)
    else:
        loc = str(SAMPLE)
    im = pyautogui.screenshot(
        imageFilename=loc,
        region=box.area
    )
    im.save(loc)
    click.echo(F'sudo adreader capture {box} in {loc}')
    if button:
        Cache().write(button=box)
    else:
        Cache().write(coord=box)


def capture_text(im: Path):
    start = time.time()
    reader = easyocr.Reader(['en'])  # this needs to run only once to load the model into memory
    result = reader.readtext(im)
    tot = time.time() - start
    print(f'Captured in {tot:2.2} sec')
    return result


@cli.command()
@click.argument('title')
@click.option('--coord', help='Screenshot area top-sx(x,y),bottm-dx(x,y) e.g. 200,100,100,500')
@click.option('-K', '--key', default=None, help='Key to press for next screenshot. Eg. left')
@click.option('-P', '--pages', help='Number of pages to capture', type=click.INT, default=0, show_default=True)
@click.option('-D', '--delay', help='Number of of seconds to wait before starting capture', type=click.INT, default=3,
              show_default=True)
@click.option('--capture/--no-capture', default=False, help='Confirm capture. Otherwise simulate only')
@click.option('-B', '--button/--no-button',
              is_flag=True, help='Use the button for going to next page',
              default=False,
              show_default=True)
def capture(capture, pages, title, delay, button, key, coord=None):
    """Capture the screenshots"""
    cache = Cache().read()
    button = button and cache['button']

    if coord:
        click.echo(f'Storing coordinates {coord} in cache')
        Cache().write(coord=Box(coord))
    else:
        coord = cache.get('coord')

    if coord is None:
        click.secho('ERROR: No cache found and no coord option provided', fg='red', bold=True)
        return

    if (target := TARGET / title).exists():
        click.secho(f'ATTENTION It appears {title} folder already exists.', fg="yellow")
        if click.confirm('Do you want to override it?'):
            shutil.rmtree(target)
        else:
            click.echo("Command aborted upon users's request")
            return

    click.echo(f'Found coord {coord} in cache')
    box = coord
    click.echo(f'Original box to capture: {box}')
    # box = box.scaled
    # click.echo(f'Scaled box to capture: {box}')

    if not (root := Path(PREFIX)).exists():
        os.mkdir(root)

    sleep(delay)

    if not key:
        go_next(box)

    if pages:
        rng = range(pages)
    else:
        rng = range(2000)

    oldim = None

    txt = {}

    files = glob(str(Path(PREFIX)/ '*'))
    for f in files:
        os.remove(f)

    for c in rng:
        loc = f'{PREFIX}/img{c:04}.png'
        text = f'{PREFIX}/{title}.json'
        print(f'Writing {loc}')
        im = box.capture(loc)
        if capture:
            im.save(loc)
        if oldim and len([(x, y) for x, y in zip(oldim.getdata(), im.getdata()) if x != y]) == 0:
            print(f'Found last page {c}')
            # if (p := Path(loc)).exists():
            #     p.unlink()
            c -= 1
            break
        oldim = im

        go_next(box, button, key)

        txt[c] = capture_text(str(Path(loc)))

        if not capture:
            Path(loc).unlink()
        # sleep(0.1)
        # pyautogui.hotkey('command', 'right')

    if capture:
        target = Path(text)
        click.echo(f'Writing to {target}')
        with target.open(mode="wt") as fo:
            fo.write(
                reader_txt(txt)
                # json.dumps(txt, cls=NpEncoder, indent=2)
            )

        images = [
            Image.open(f'{PREFIX}/img{z:04}.png')
            for z in range(pages or c)
        ]
        pdf_path = f'{PREFIX}/{title}.pdf'
        images[0].save(
            pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
        )
        make_tarfile(PREFIX, f'{PREFIX}/{title}.tgz')
        purge_png(PREFIX)

    if os.name != 'nt':
        chown(str(PREFIX), UID, GID)

    Path(PREFIX).rename(target)


def go_next(box, button=None, key=None):
    if key:
        pyautogui.press(key)
    elif button:
        print(f'clicking center {button.center}')
        pyautogui.click(*button.center)
    else:
        middle = int((box.br.y + box.tl.y) / 2)

        pyautogui.click(box.tl.x + 5, middle)
        pyautogui.moveTo(box.tl.x - 20, middle)  # move away

    sleep(THINK)

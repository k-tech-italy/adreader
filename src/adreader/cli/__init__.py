import json
import os
from pathlib import Path
from time import sleep

import click
import keyboard
import pyautogui
from PIL import Image

from adreader.utils import chown
from adreader.utils.cache import Cache
from adreader.gui import Point, Box

DELAY = 3

UID = 501
GID = 20

THINK = 0.0

TITLE = 'ManagementAndAccounting'
PREFIX = '.tmp'
TARGET = '.books'

PREFIX = Path(PREFIX)
TARGET = Path(TARGET)

SAMPLE = (Path(__file__).parent.parent / 'corners/sample.png').absolute()


@click.group()
# @click.option('--count', default=1, help='Number of greetings.')
# @click.option('--name', prompt='Your name',
#               help='The person to greet.')
def cli():
    """Simple program that captures screenshots of an adreader"""


@cli.command()
def coord():
    """Get coordinates for first page"""
    click.echo(
        """Instructions
        1. Go to the first page and move the mouse to the top left corner of the image to capture.
        2. Press "c"
        3. Repeat for the bottom-right corner"""
    )
    keyboard.wait("command+shift")
    top_left = Point(*pyautogui.position())
    click.echo('Now capture the bottom right corner')
    keyboard.wait("command+shift")
    bottom_right = Point(*pyautogui.position())
    box = Box(top_left, bottom_right)
    im = pyautogui.screenshot(
        imageFilename=str(SAMPLE),
        region=box.area
    )
    im.save(SAMPLE)
    click.echo(F'sudo adreader capture {box}')
    Cache().write(coord=box)


@cli.command()
@click.option('--coord', help='Screenshot area top-sx(x,y),bottm-dx(x,y) e.g. 200,100,100,500')
@click.option('-P', '--pages', help='Number of pages to capture', type=click.INT, default=0)
@click.option( '--capture/--no-capture', default=False, help='Number of pages to capture')
def capture(capture, pages, coord=None):
    """Capture the screenshots"""
    cache = Cache().read()

    if coord:
        click.echo(f'Storing coordinates {coord} in cache')
        Cache().write(coord=Box(coord))
    else:
        coord = cache.get('coord')

    if 'coord' is None:
        click.secho('ERROR: No cache found and no coord option provided', fg='red', bold=True)
        return

    click.echo(f'Found coord {coord} in cache')
    box = coord
    click.echo(f'Original box to capture: {box}')
    # box = box.scaled
    # click.echo(f'Scaled box to capture: {box}')

    if not (root := Path(PREFIX)).exists():
        os.mkdir(root)

    sleep(DELAY)

    pyautogui.moveTo(box.tl.x + 5, box.tl.y + 5)
    pyautogui.click()
    pyautogui.moveTo(box.tl.x - 20, box.tl.y - 20)  # move away

    if pages:
        rng = range(pages)
    else:
        rng = range(2000)

    oldim = None

    for c in rng:
        loc = f'{PREFIX}/img{c:03}.png'
        print(f'Writing {loc}')
        if capture:
            im = box.capture(loc)
            if oldim and len([(x, y) for x, y in zip(oldim.getdata(), im.getdata()) if x != y]) == 0:
                print(f'Found last page {c}')
                break
            oldim = im
            im.save(loc)
        # sleep(0.1)
        pyautogui.hotkey('command', 'right')
        pyautogui.click(box.tl.x + 5, box.tl.y + 5)
        pyautogui.moveTo(box.tl.x - 20, box.tl.y - 20)  # move away
        sleep(THINK)

    if capture:
        images = [
            Image.open(f'{PREFIX}/img{z:03}.png')
            for z in range(c)
        ]
        pdf_path = f'{PREFIX}/{TITLE}.pdf'
        images[0].save(
            pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
        )

    chown(str(PREFIX), UID, GID)
    Path(PREFIX).rename(TARGET / TITLE)

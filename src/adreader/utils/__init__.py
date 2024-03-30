import os
import tarfile
from pathlib import Path
import click
from dotenv import load_dotenv

load_dotenv()

RATIO = float(os.getenv('RATIO', 0.5))


def chown(path, id: int, gid: int):
    # Change permissions for the top-level folder
    os.chown(path, id, gid)

    for root, dirs, files in os.walk(path):
        # set perms on sub-directories
        for momo in dirs:
            os.chown(os.path.join(root, momo), id, gid)

        # set perms on files
        for momo in files:
            os.chown(os.path.join(root, momo), id, gid)


def ratio(*args):
    return [int(x * RATIO) for x in args]


def make_tarfile(source_dir: Path, output_filename: str):
    pngs = [x for x in source_dir.glob('*.png')] + [x for x in source_dir.glob('*.json')]
    click.echo(f'Archiving images in {source_dir} to {output_filename}')

    with tarfile.open(output_filename, "w:gz") as tar:
        for p in pngs:
            print(f'adding {p} as {p.name}')
            tar.add(p.absolute(), arcname=str(p.name))


def purge_png(source_dir: Path):
    pngs = [x for x in source_dir.glob('*.png')] + [x for x in source_dir.glob('*.json')]
    for p in pngs:
        p.unlink()

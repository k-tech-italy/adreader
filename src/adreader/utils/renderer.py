from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / 'templates'),
    autoescape=select_autoescape()
)


def render(template, **kwargs):
    template = env.get_template(template)
    return template.render(**kwargs)


def reader_txt(txt):
    return render('scanned.j2', pages=txt)


if __name__ == '__main__':
    ADREADER = Path(__file__).parent.parent.parent.parent
    import json
    txt = json.loads(ADREADER.joinpath('.books/AdobeDigital/AdobeDigital.json').read_text())
    # with Path(__file__).parent.joinpath('scanned.txt').open() as f:
    print(reader_txt(txt))

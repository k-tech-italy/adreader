from pathlib import Path

import pytesseract

from adreader.config import env



def capture_text(im: str) -> str:
    """Capture searchable pdf and text."""

    if cmd := env['TESSERACT_CMD']:
        pytesseract.pytesseract.tesseract_cmd = cmd
        print(f'Using {cmd} for Tesseract')

    pdf = pytesseract.image_to_pdf_or_hocr(im, extension='pdf')
    with open(Path(im).with_suffix('.pdf'), 'w+b') as f:
        f.write(pdf)
        return f.name

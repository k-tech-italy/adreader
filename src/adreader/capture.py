from pathlib import Path

import pytesseract


def capture_text(im: str) -> str:
    """Capture searchable pdf and text."""
    pdf = pytesseract.image_to_pdf_or_hocr(im, extension='pdf')
    with open(Path(im).with_suffix('.pdf'), 'w+b') as f:
        f.write(pdf)
        return f.name

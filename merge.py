#!/usr/bin/env python3
"""
Usage: python MergeAttachements.py <main.pdf> <attachments.zip> [extra1.pdf;extra2.pdf;...]
"""

import sys
import os
import zipfile
import tempfile
from pathlib import Path
from PIL import Image
from pypdf import PdfWriter, PdfReader
import img2pdf

SUPPORTED_IMAGES = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
SUPPORTED_DOCS   = {'.pdf'}

def image_to_pdf_bytes(image_path: Path, tmp_dir: Path) -> Path:
    """Convert an image to a temporary PDF file. Returns path to the temp PDF."""
    tmp_pdf = tmp_dir / (image_path.stem + '_converted.pdf')

    try:
        a4 = (img2pdf.mm_to_pt(210), img2pdf.mm_to_pt(297))
        layout = img2pdf.get_layout_fun(a4)
        pdf_bytes = img2pdf.convert(
            str(image_path),
            layout_fun=layout,
            rotation=img2pdf.Rotation.ifvalid
        )
        tmp_pdf.write_bytes(pdf_bytes)
        return tmp_pdf
    except Exception as e:
        print(f"    [~] img2pdf failed ({e}), falling back to Pillow...")

    with Image.open(image_path) as img:
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        a4_w, a4_h = 1240, 1754
        img.thumbnail((a4_w, a4_h), Image.LANCZOS)
        canvas = Image.new('RGB', (a4_w, a4_h), (255, 255, 255))
        offset = ((a4_w - img.width) // 2, (a4_h - img.height) // 2)
        canvas.paste(img, offset)
        canvas.save(str(tmp_pdf), format='PDF', resolution=150)

    return tmp_pdf


def merge(main_pdf: str, zip_path: str, output_pdf: str, sibling_pdfs: list[str] = []):
    writer = PdfWriter()

    # --- 1. Add main PDF ---
    print(f"[+] Adding main PDF: {main_pdf}")
    with open(main_pdf, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            writer.add_page(page)

    # --- 2. Extract ZIP and sort contents (optional) ---
    if zip_path:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(tmpdir)

            all_files = sorted(
                [p for p in tmpdir.rglob('*') if p.is_file()],
                key=lambda p: str(p.relative_to(tmpdir)).lower()
            )

            print(f"[+] Found {len(all_files)} file(s) in ZIP:")
            for f in all_files:
                print(f"    {f.relative_to(tmpdir)}")

            for file in all_files:
                suffix = file.suffix.lower()

                if suffix in SUPPORTED_DOCS:
                    print(f"[+] Appending PDF: {file.name}")
                    with open(file, 'rb') as fh:
                        reader = PdfReader(fh)
                        for page in reader.pages:
                            writer.add_page(page)

                elif suffix in SUPPORTED_IMAGES:
                    print(f"[+] Converting & appending image: {file.name}")
                    tmp_pdf = image_to_pdf_bytes(file, tmpdir)
                    with open(tmp_pdf, 'rb') as fh:
                        reader = PdfReader(fh)
                        for page in reader.pages:
                            writer.add_page(page)

                else:
                    print(f"[~] Skipping unsupported file: {file.name}")
    else:
        print("[~] No ZIP provided - skipping.")

    # --- 3. Append sibling PDFs (alphabetically sorted by filename) ---
    for sib in sorted(sibling_pdfs, key=lambda p: Path(p).name.lower()):
        print(f"[+] Appending sibling PDF: {Path(sib).name}")
        with open(sib, 'rb') as fh:
            reader = PdfReader(fh)
            for page in reader.pages:
                writer.add_page(page)

    # --- 4. Write output ---
    with open(output_pdf, 'wb') as out:
        writer.write(out)
    print(f"\n[✓] Done! Output saved to: {output_pdf}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python MergeAttachements.py <main.pdf> <attachments.zip> [extra1.pdf;extra2.pdf;...]")
        sys.exit(1)

    main_pdf = sys.argv[1]
    zip_path = sys.argv[2].strip() if len(sys.argv) > 2 else ""
    stem     = Path(sys.argv[1]).stem
    output   = f"{stem}_.pdf"

    sibling_pdfs = []
    if len(sys.argv) > 3 and sys.argv[3].strip():
        sibling_pdfs = [p.strip() for p in sys.argv[3].split(';') if p.strip()]

    if not os.path.exists(main_pdf):
        print(f"Error: Main PDF not found: {main_pdf}")
        sys.exit(1)

    if zip_path and not os.path.exists(zip_path):
        print(f"Error: ZIP file not found: {zip_path}")
        sys.exit(1)

    merge(main_pdf, zip_path, output, sibling_pdfs)

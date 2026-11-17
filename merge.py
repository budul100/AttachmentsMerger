#!/usr/bin/env python3
"""
Usage:
    python merge.py <file1> <file2> [file3 ...]
        Ordered mode: merges exactly the given files in the order of the arguments.
        Supported inputs: PDFs, images and ZIP archives (ZIP contents are sorted
        alphabetically and inserted at the position of the ZIP).

    python merge.py <main.pdf>
        Directory mode: the given PDF is the base, followed by the contents of the
        single ZIP in the same directory (optional), followed by all other PDFs in
        the same directory (sorted alphabetically).

The output is written next to the first file as <first_filename>_.pdf.
"""

import itertools
import sys
import tempfile
import zipfile
from pathlib import Path

import img2pdf
from PIL import Image
from pypdf import PdfReader, PdfWriter

SUPPORTED_IMAGES = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
SUPPORTED_DOCS = {'.pdf'}
SUPPORTED_ARCHIVES = {'.zip'}

_temp_counter = itertools.count(1)


def image_to_pdf_bytes(image_path: Path, tmp_dir: Path) -> Path:
    """Convert an image to a temporary PDF file. Returns path to the temp PDF."""
    tmp_pdf = tmp_dir / f"{next(_temp_counter)}_{image_path.stem}_converted.pdf"

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


def append_pdf(writer: PdfWriter, pdf_path: Path) -> None:
    with open(pdf_path, 'rb') as fh:
        reader = PdfReader(fh)
        for page in reader.pages:
            writer.add_page(page)


def append_image(writer: PdfWriter, image_path: Path, tmp_dir: Path) -> None:
    tmp_pdf = image_to_pdf_bytes(image_path, tmp_dir)
    append_pdf(writer, tmp_pdf)


def append_zip(writer: PdfWriter, zip_path: Path, tmp_dir: Path) -> None:
    """Extract a ZIP and append its PDFs and images, sorted by relative path."""
    extract_dir = tmp_dir / f"zip_{next(_temp_counter)}"
    extract_dir.mkdir()

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_dir)

    all_files = sorted(
        [p for p in extract_dir.rglob('*') if p.is_file()],
        key=lambda p: str(p.relative_to(extract_dir)).lower()
    )

    print(f"[+] Found {len(all_files)} file(s) in {zip_path.name}:")
    for f in all_files:
        print(f"    {f.relative_to(extract_dir)}")

    for file in all_files:
        suffix = file.suffix.lower()

        if suffix in SUPPORTED_DOCS:
            print(f"[+] Appending PDF: {file.name}")
            append_pdf(writer, file)
        elif suffix in SUPPORTED_IMAGES:
            print(f"[+] Converting & appending image: {file.name}")
            append_image(writer, file, extract_dir)
        else:
            print(f"[~] Skipping unsupported file: {file.name}")


def merge(inputs: list[Path], output_pdf: Path) -> None:
    """Merge the inputs into one PDF, strictly in the given order."""
    writer = PdfWriter()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)

        for path in inputs:
            suffix = path.suffix.lower()

            if suffix in SUPPORTED_DOCS:
                print(f"[+] Appending PDF: {path.name}")
                append_pdf(writer, path)
            elif suffix in SUPPORTED_IMAGES:
                print(f"[+] Converting & appending image: {path.name}")
                append_image(writer, path, tmp_dir)
            elif suffix in SUPPORTED_ARCHIVES:
                print(f"[+] Extracting ZIP: {path.name}")
                append_zip(writer, path, tmp_dir)
            else:
                print(f"[~] Skipping unsupported file: {path.name}")

        with open(output_pdf, 'wb') as out:
            writer.write(out)

    print(f"\n[✓] Done! Output saved to: {output_pdf}")


def collect_directory_inputs(main_pdf: Path) -> list[Path]:
    """Directory mode: main PDF, then the single ZIP (if any), then sibling PDFs."""
    directory = main_pdf.parent
    siblings = [p for p in directory.iterdir() if p.is_file()]

    zips = sorted((p for p in siblings if p.suffix.lower() == '.zip'),
                  key=lambda p: p.name.lower())
    if len(zips) > 1:
        raise ValueError("More than one ZIP found - aborting.")

    other_pdfs = sorted(
        (p for p in siblings
         if p.suffix.lower() == '.pdf' and p.name.lower() != main_pdf.name.lower()),
        key=lambda p: p.name.lower()
    )

    inputs = [main_pdf]
    if zips:
        inputs.append(zips[0])
    else:
        print("[~] No ZIP file found - skipping ZIP attachments.")
    inputs.extend(other_pdfs)
    return inputs


def main(args: list[str]) -> int:
    if not args:
        print(__doc__)
        return 1

    paths = [Path(a.strip()).resolve() for a in args if a.strip()]

    missing = [p for p in paths if not p.is_file()]
    if missing:
        for p in missing:
            print(f"Error: File not found: {p}")
        return 1

    if len(paths) == 1:
        main_pdf = paths[0]
        if main_pdf.suffix.lower() != '.pdf':
            print(f"Error: A single input must be a PDF (directory mode): {main_pdf.name}")
            return 1
        try:
            inputs = collect_directory_inputs(main_pdf)
        except ValueError as e:
            print(f"[!] {e}")
            return 1
    else:
        inputs = paths

    first = inputs[0]
    output = first.parent / f"{first.stem}_.pdf"

    print(f"[*] Merge order ({len(inputs)} input(s)):")
    for i, p in enumerate(inputs, 1):
        print(f"    {i}. {p.name}")
    print()

    merge(inputs, output)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

# Document Attachments Merger

Merges a main PDF with additional PDFs from the same directory and/or attachments (PDFs and images) from a ZIP archive into a single output PDF.

## Files

| File | Description |
|---|---|
| `MergeAttachements.bat` | Launcher script — drop a PDF onto this to run |
| `MergeAttachements.py` | Python merge logic |

## Usage

Drag and drop a PDF file onto `MergeAttachements.bat` (or a shortcut/wrapper pointing to it).

The script will automatically:
1. Use the dropped file as the **base PDF**
2. Append all other PDFs found in the **same directory**, sorted alphabetically by filename
3. Append all PDFs and images found inside a **ZIP file** in the same directory (also sorted alphabetically)

## Requirements

- Python 3.10+
- Dependencies are installed automatically on first run: `pypdf`, `Pillow`, `img2pdf`

## Rules

- Exactly **one ZIP file** may be present in the directory. More than one aborts the run.
- A ZIP file is **optional**. If none is found, ZIP processing is skipped.
- Additional PDFs in the directory are **optional**.

## Supported attachment formats

| Type | Formats |
|---|---|
| Documents | `.pdf` |
| Images | `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.tif`, `.webp` |

## Output

The output file is written to the same directory as the base PDF, named `<base_filename>_.pdf`.

Example: `Umzugskosten_HR.pdf` → `Umzugskosten_HR_.pdf`

## Notes

- Images are converted to A4 PDF pages before merging (via `img2pdf`, with Pillow as fallback).
- The script does **not** modify the original files.

# Document Attachments Merger

Merges PDFs, images and ZIP archives into a single output PDF.

## Files

| File | Description |
|---|---|
| `merge.bat` | Launcher script, drop one or more files onto it to run |
| `merge.py` | Python merge logic |

## Usage

### Ordered mode (two or more files dropped)

Drag and drop several files onto `merge.bat`. They are merged **in the order in which they are passed as parameters**.

- The first file determines the output name and location.
- Allowed inputs: `.pdf`, images and `.zip`.
- A ZIP is expanded in place: its PDFs and images are appended (sorted alphabetically by relative path) at the position of the ZIP.
- Nothing else in the directory is picked up.

Command line equivalent:

```
python merge.py cover.pdf invoice.pdf receipts.zip photo.jpg
```

### Directory mode (exactly one PDF dropped)

Behaves as before:
1. The dropped file is the **base PDF**
2. The contents of the **ZIP file** in the same directory are appended (sorted alphabetically)
3. All other PDFs in the same directory are appended, sorted alphabetically by filename

Rules: at most **one ZIP** may be present in the directory (more than one aborts the run). ZIP and additional PDFs are optional.

## Requirements

- Python 3.10+
- Dependencies are installed automatically on first run: `pypdf`, `Pillow`, `img2pdf`

## Supported formats

| Type | Formats |
|---|---|
| Documents | `.pdf` |
| Images | `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.tif`, `.webp` |
| Archives | `.zip` (containing the formats above) |

## Output

The output file is written to the directory of the first file, named `<first_filename>_.pdf`.

Example: `Umzugskosten_HR.pdf` → `Umzugskosten_HR_.pdf`

## Notes

- Images are converted to A4 PDF pages before merging (via `img2pdf`, with Pillow as fallback).
- The original files are not modified.
- When dropping multiple files in Windows Explorer, the order passed to the script is determined by Explorer (usually the sort order of the folder view, not the click order). If the order matters, use the command line or a wrapper that passes the files explicitly.

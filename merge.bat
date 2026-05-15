@echo off
setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0

if "%~1"=="" (
    echo [!] Please drop a PDF file onto this script.
    pause
    exit /b 1
)

cd /d "%~dp1"

echo [*] Checking dependencies...
pip show pypdf >nul 2>&1 || pip install pypdf
pip show pillow >nul 2>&1 || pip install pillow
pip show img2pdf >nul 2>&1 || pip install img2pdf

echo [*] Searching for ZIP and additional PDF files...

set PDF_FILE=%~nx1
set EXTRA_PDFS=
set ZIP_FILE=

for %%f in (*.pdf) do (
    if /i not "%%f"=="%PDF_FILE%" (
        if not defined EXTRA_PDFS (
            set EXTRA_PDFS=%%f
        ) else (
            set EXTRA_PDFS=!EXTRA_PDFS!;%%f
        )
    )
)

for %%f in (*.zip) do (
    if not defined ZIP_FILE (
        set ZIP_FILE=%%f
    ) else (
        echo [!] More than one ZIP found - aborting.
        pause
        exit /b 1
    )
)

if not defined ZIP_FILE (
    echo [~] No ZIP file found - skipping ZIP attachments.
)

echo [+] Base PDF : %PDF_FILE%
if defined EXTRA_PDFS echo [+] Extra PDFs: %EXTRA_PDFS%
if defined ZIP_FILE echo [+] ZIP found : %ZIP_FILE%
echo [*] Running merge...

python "%SCRIPT_DIR%merge.py" "%PDF_FILE%" "%ZIP_FILE%" "%EXTRA_PDFS%"

if %errorlevel% == 0 (
    echo.
    echo [OK] Done! Output: %PDF_FILE:~0,-4%_.pdf
) else (
    echo.
    echo [!] Something went wrong. See output above.
)

pause

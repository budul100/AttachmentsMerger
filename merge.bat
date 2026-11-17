@echo off

if "%~1"=="" (
    echo [!] Please drop one or more files onto this script.
    pause
    exit /b 1
)

echo [*] Checking dependencies...
pip show pypdf >nul 2>&1 || pip install pypdf
pip show pillow >nul 2>&1 || pip install pillow
pip show img2pdf >nul 2>&1 || pip install img2pdf

python "%~dp0merge.py" %*

if errorlevel 1 (
    echo.
    echo [!] Something went wrong. See output above.
) else (
    echo.
    echo [OK] Done!
)

pause

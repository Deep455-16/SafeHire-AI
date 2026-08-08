@echo off
echo ==================================================
echo       SafeHire AI - Installation Script
echo ==================================================

echo.
echo [1/3] Creating virtual environment (if not exists)...
if not exist "venv" (
    python -m venv venv
)

echo.
echo [2/3] Installing Python dependencies...
call venv\Scripts\activate
pip install -r requirements.txt

echo.
echo [3/3] Checking for Tesseract OCR...
where tesseract >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    if not exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
        echo Tesseract OCR not found in PATH or standard installation directory.
        echo Attempting to install Tesseract OCR using winget...
        winget install -e --id UB-Mannheim.TesseractOCR --accept-package-agreements --accept-source-agreements
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to install Tesseract OCR via winget. 
            echo Please install it manually from: https://github.com/UB-Mannheim/tesseract/wiki
            echo Note: You may need to restart your terminal or computer after installation.
        ) else (
            echo Tesseract OCR installed successfully!
        )
    ) else (
        echo Tesseract OCR found in C:\Program Files\Tesseract-OCR\tesseract.exe
    )
) else (
    echo Tesseract OCR is installed and in PATH.
)

echo.
echo ==================================================
echo Installation Complete! 
echo You can now run the application using start_app.bat
echo ==================================================
pause

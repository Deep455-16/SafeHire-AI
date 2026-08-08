@echo off
echo ==================================================
echo         SafeHire AI - Application Server
echo ==================================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Starting the SafeHire AI API server...
echo The application will automatically open in your default browser.
echo If it does not, manually navigate to http://127.0.0.1:8000
echo.

start http://127.0.0.1:8000
uvicorn api:app --reload

pause

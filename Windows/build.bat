@echo off
echo ========================================
echo   Building Auto Clicker MSI
echo ========================================
echo.
echo Installing PyInstaller...
pip install pyinstaller
if errorlevel 1 (
    echo Failed to install PyInstaller.
    pause
    exit /b 1
)
echo.
echo Building MSI (includes Python and dependencies)...
pyinstaller --onedir --msi main.py
if errorlevel 1 (
    echo Failed to build MSI.
    pause
    exit /b 1
)
echo.
echo Build complete! Check dist/ folder for AutoClicker.msi
pause
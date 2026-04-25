@echo off
:: ============================================================
:: TokenForge — Windows one-click launcher
:: Double-click this file or run it from any terminal.
:: ============================================================

setlocal EnableDelayedExpansion

:: Resolve the project root (parent of the scripts\ folder)
set "SCRIPT_DIR=%~dp0"
set "ROOT=%SCRIPT_DIR%.."

:: Change to project root so relative paths inside launch.py work
cd /d "%ROOT%"

:: Verify Python is available
where python >nul 2>&1
if errorlevel 1 (
    echo.
    echo  [ERROR] 'python' not found on PATH.
    echo  Install Python 3.10+ from https://www.python.org/downloads/
    echo  and make sure to tick "Add Python to PATH" during setup.
    echo.
    pause
    exit /b 1
)

:: Run the launcher
python launcher\launch.py
set EXIT_CODE=%errorlevel%

if %EXIT_CODE% neq 0 (
    echo.
    echo  [ERROR] TokenForge exited with code %EXIT_CODE%.
    echo  Review the output above for details.
    echo.
    pause
    exit /b %EXIT_CODE%
)

exit /b 0

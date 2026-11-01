@echo off
REM ==============================================================================
REM play.bat - One-click launcher for Git Workshop Day 2 Games (Windows)
REM Zero external packages required.
REM ==============================================================================

cd /d "%~dp0"

REM Try python first, then py launcher, then python3
where python >nul 2>nul
if %errorlevel% equ 0 (
    python game.py %*
    goto end
)

where py >nul 2>nul
if %errorlevel% equ 0 (
    py -3 game.py %*
    goto end
)

where python3 >nul 2>nul
if %errorlevel% equ 0 (
    python3 game.py %*
    goto end
)

echo.
echo [ERROR] Python 3 was not found on your system PATH.
echo Please install Python 3 or ensure 'Add python.exe to PATH' is checked.
echo.
pause

:end

@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo   SexyUI Editor - Nuitka Build Script
echo ========================================
echo.

cd /d "%~dp0"

set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo Using MSVC from Visual Studio 2022
echo.

python -m nuitka ^
    --standalone ^
    --msvc=latest ^
    --jobs=4 ^
    --output-filename=SexyUIEditor.exe ^
    --output-dir=dist ^
    --company-name=StackAndPointer ^
    --product-name=SexyUIEditor ^
    --file-description="SexyUI&PVZUIEditor" ^
    --copyright="Copyright (C) 2026 StackAndPointer" ^
    --file-version=1.0.0.0 ^
    --product-version=1.0.0.0 ^
    --windows-icon-from-ico=resources\icons\icon.ico ^
    --windows-console-mode=disable ^
    --enable-plugin=pyqt6 ^
    --include-package=core ^
    --include-package=ui ^
    --include-data-dir=i18n=i18n ^
    --include-data-dir=resources=resources ^
    --include-data-dir=SexyUIExtensions=SexyUIExtensions ^
    --nofollow-import-to=tkinter ^
    --nofollow-import-to=unittest ^
    --nofollow-import-to=test ^
    --nofollow-import-to=tests ^
    --nofollow-import-to=numpy ^
    --nofollow-import-to=pandas ^
    --nofollow-import-to=scipy ^
    --nofollow-import-to=matplotlib ^
    --nofollow-import-to=PIL ^
    --nofollow-import-to=cv2 ^
    --nofollow-import-to=venv ^
    --assume-yes-for-downloads ^
    --show-progress ^
    --show-memory ^
    main.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   Build completed successfully!
    echo   Output: dist\main.dist\SexyUIEditor.exe
    echo.
    echo   Note: Please manually copy 'pak' and 'Content' 
    echo         folders to dist\main.dist\ directory.
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   Build failed with error code: %errorlevel%
    echo ========================================
)

pause

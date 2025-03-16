@echo off
setlocal enabledelayedexpansion

echo Setting up BugHunter environment...

:: Check for Python in multiple locations
set PYTHON_CMD=
set LOCATIONS_TO_CHECK=^
    python^
    py^
    %LOCALAPPDATA%\Programs\Python\Python311\python.exe^
    %LOCALAPPDATA%\Programs\Python\Python310\python.exe^
    %LOCALAPPDATA%\Programs\Python\Python39\python.exe^
    %LOCALAPPDATA%\Programs\Python\Python38\python.exe^
    C:\Python311\python.exe^
    C:\Python310\python.exe^
    C:\Python39\python.exe^
    C:\Python38\python.exe

for %%i in (%LOCATIONS_TO_CHECK%) do (
    %%i --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=%%i
        goto :found_python
    )
)

:python_not_found
echo Python 3.8 or later is not found in common locations.
echo Please ensure Python is installed and added to PATH.
echo.
echo You can download Python from: https://www.python.org/downloads/
echo After installation, run this script again.
pause
exit /b 1

:found_python
echo Found Python: !PYTHON_CMD!
!PYTHON_CMD! --version

:: Check if pip is installed
!PYTHON_CMD! -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Installing pip...
    !PYTHON_CMD! -m ensurepip --default-pip
)

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    !PYTHON_CMD! -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment activation script not found.
    pause
    exit /b 1
)

:: Verify virtual environment activation
where python | findstr /i "venv" >nul
if errorlevel 1 (
    echo Virtual environment activation failed.
    pause
    exit /b 1
)

:: Install/upgrade pip in virtual environment
python -m pip install --upgrade pip

:: Install requirements if they exist
if exist requirements.txt (
    echo Installing requirements...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install requirements.
        pause
        exit /b 1
    )
) else (
    echo No requirements.txt found. Creating basic requirements...
    (
        echo black
        echo flake8
        echo pytest
        echo mypy
        echo pylint
    ) > requirements.txt
    pip install -r requirements.txt
)

:: Create basic project structure if it doesn't exist
if not exist app (
    echo Creating basic project structure...
    mkdir app
    mkdir app\models
    mkdir app\services
    mkdir app\utils
    mkdir tests
    mkdir docs
    mkdir scripts
    mkdir logs
    mkdir database

    :: Create __init__.py files
    type nul > app\__init__.py
    type nul > app\models\__init__.py
    type nul > app\services\__init__.py
    type nul > app\utils\__init__.py
    type nul > tests\__init__.py
)

:: Run the import updater
echo Running import updater...
python Scripts\update_imports.py

echo.
echo Setup completed successfully!
echo.
echo Virtual environment is active and requirements are installed.
echo To deactivate the virtual environment, type 'deactivate'
echo.
echo Project structure:
echo - app/           (Main application code)
echo - tests/         (Test files)
echo - docs/          (Documentation)
echo - scripts/       (Utility scripts)
echo - logs/          (Log files)
echo - database/      (Database files)
echo - requirements.txt
echo.

pause

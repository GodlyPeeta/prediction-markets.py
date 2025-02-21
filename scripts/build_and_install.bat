@echo off
echo Building the Python package using py -m build...

REM Build the package using py -m build
py -m build

if %errorlevel% neq 0 (
    echo Error building the package.  Please check the output above.
    exit /b %errorlevel%
)

echo Installing the package with pip...

REM Find the .whl file in the dist directory
for %%a in (dist\*.whl) do (
    set "WHEEL_FILE=%%a"
)

REM Check if a .whl file was found
if not defined WHEEL_FILE (
    echo Error: No .whl file found in the dist directory.
    exit /b 1
)

REM Install the package using pip with the specific .whl file
pip install --force-reinstall "%WHEEL_FILE%"

if %errorlevel% neq 0 (
    echo Error installing the package.  Please check the output above.
    exit /b %errorlevel%
)

echo Package built and installed successfully!
pause

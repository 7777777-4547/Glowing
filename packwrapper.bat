@echo off
setlocal enableextensions

:parse_args
if "%~1" == "" goto :show_usage1
if "%~1" == "-h" (
    goto :show_usage2
)
if "%~1" == "--help" (
    goto :show_usage2
)

if "%~1" == "requirementsGenerate" (
    pip install pipreqs
    pipreqs . --encoding=utf8 --force
    exit /b 0
)
if "%~1" == "requirementsInstall" (
    pip install -r requirements.txt
    exit /b 0
)

if "%~1" == "reqGen" (
    pip install pipreqs
    pipreqs . --encoding=utf8 --force
    exit /b 0
)
if "%~1" == "reqInstl" (
    pip install -r requirements.txt
    exit /b 0
)

if "%~1" == "build" (
    python PackWrapperLauncher.py
    exit /b 0
)
if "%~1" == "init" (
    python PackWrapperDownloader.py
    exit /b 0
)
if "%~1" == "download" (
    python PackWrapperDownloader.py
    exit /b 0
)
if "%~1" == "downl" (
    python PackWrapperDownloader.py
    exit /b 0
)

:show_usage1
echo No/Wrong arguments provided, please use one of the following:
echo. 
goto :show_usage2

:show_usage2
echo Tasks:
echo   requirementsGenerate, reqGen
echo   requirementsInstall, reqInstl
echo   build
echo   init, download, downl
echo.
echo Options:
echo   -h, --help    Show this help message

:: RUN THIS AFTER CLONING
:: This is so you can just clone the repo and run this to get everything you need to start developing
@echo off
setlocal
set "NODE_URL=https://nodejs.org/dist/v20.11.1/node-v20.11.1-x64.msi"
set "NODE_INSTALLER=node-installer.msi"

where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    powershell -Command "Invoke-WebRequest -Uri %NODE_URL% -OutFile %NODE_INSTALLER"
    msiexec /i %NODE_INSTALLER% /quiet /norestart
    del %NODE_INSTALLER%
    timeout /t 10
)

if not exist package.json (
    echo package.json was not found, This must be run in project root.
    pause
    exit /b
)

echo Installing dependencies...
echo Installing node...
npm install 

where electron >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Installing electron...
    npm install electron --save-dev 
)

echo.
echo Setup complete, would you like to run the current build?
choice /M "[Y/N]"
if errorlevel 2 (
    echo Closing installer...
    exit
)
echo running build
if exist "%~dp0run.bat" ( 
    call "%~dp0run.bat"
    echo Success, closing now...
    timeout /t 5
    exit
) else (
    echo run.bat not found, aborting...
    timeout /t 5
    exit
)
@echo off
setlocal
echo NOTICE: THIS WILL OVERWRITE COMPILES WIT HTHE SAME NAME!
echo Leaving this blank will have it use a default name
set /p APPNAME=App Name?

echo Packaging as "%APPNAME%"...
npx electron-packager . "%APPNAME%" --platform=win32 --arch=x64 --out=dist --overwrite

echo.
echo Packaging complete!
pause
endlocal
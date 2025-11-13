@echo off
echo ==================================
echo   JARVIS WinUI 3 App Launcher
echo ==================================
echo.

cd JarvisApp

echo [1/3] Kompiliere Projekt...
dotnet clean --nologo
dotnet build -c Release /p:Platform=x64 --nologo

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Fehler beim Kompilieren!
    pause
    exit /b 1
)

echo.
echo [2/3] Starte App...
echo.

start "" "bin\x64\Release\net8.0-windows10.0.19041.0\JarvisApp.exe"

echo.
echo App wurde gestartet!
echo.

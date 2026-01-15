@echo off
echo ==================================
echo   JARVIS WinUI 3 App Launcher
echo ==================================
echo.

cd JarvisApp

echo [1/4] Pruefe Ollama...
where ollama >nul 2>nul

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Ollama wurde nicht gefunden.
    echo Bitte installiere Ollama und stelle sicher, dass es im PATH ist.
    echo Danach: ollama serve
    echo.
) else (
    tasklist /FI "IMAGENAME eq ollama.exe" | find /I "ollama.exe" >nul
    if %ERRORLEVEL% NEQ 0 (
        echo Starte Ollama Server...
        start "" /min ollama serve
    ) else (
        echo Ollama Server laeuft bereits.
    )
)

echo.
echo [1.5/4] Beende laufende JarvisApp...
taskkill /IM JarvisApp.exe /F >nul 2>nul

echo.
echo [2/4] Kompiliere Projekt...
dotnet clean --nologo
dotnet build -c Release /p:Platform=x64 --nologo

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Fehler beim Kompilieren!
    pause
    exit /b 1
)

echo.
echo [3/4] Starte App...
echo.

start "" "bin\x64\Release\net8.0-windows10.0.19041.0\JarvisApp.exe"

echo.
echo App wurde gestartet!
echo.

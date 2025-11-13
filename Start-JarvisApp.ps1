# JARVIS WinUI 3 App Starter
# Dieses Skript kompiliert und startet die WinUI 3 App

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  JARVIS WinUI 3 App Launcher    " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Wechsle ins Projektverzeichnis
$projectPath = Join-Path $PSScriptRoot "JarvisApp"
Set-Location $projectPath

Write-Host "[1/3] Kompiliere Projekt..." -ForegroundColor Yellow
dotnet clean --nologo
dotnet build -c Release /p:Platform=x64 --nologo

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build fehlgeschlagen!" -ForegroundColor Red
    Read-Host "Drücke Enter zum Beenden"
    exit 1
}

Write-Host "✅ Build erfolgreich!" -ForegroundColor Green
Write-Host ""

Write-Host "[2/3] Suche ausführbare Datei..." -ForegroundColor Yellow
$exePath = Join-Path $projectPath "bin\x64\Release\net8.0-windows10.0.19041.0\JarvisApp.exe"

if (-not (Test-Path $exePath)) {
    Write-Host "❌ JarvisApp.exe nicht gefunden!" -ForegroundColor Red
    Write-Host "Erwarteter Pfad: $exePath" -ForegroundColor Gray
    Read-Host "Drücke Enter zum Beenden"
    exit 1
}

Write-Host "✅ Gefunden: JarvisApp.exe" -ForegroundColor Green
Write-Host ""

Write-Host "[3/3] Starte JARVIS App..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 Die App wird geöffnet..." -ForegroundColor Cyan
Write-Host ""

# Starte die App
Start-Process $exePath

Write-Host "✅ App gestartet!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tipp: Um die App neu zu kompilieren und zu starten, führe dieses Skript erneut aus." -ForegroundColor Gray
Write-Host ""

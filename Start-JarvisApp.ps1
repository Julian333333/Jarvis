# JARVIS WinUI 3 App Starter
# Dieses Skript kompiliert und startet die WinUI 3 App

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  JARVIS WinUI 3 App Launcher    " -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Wechsle ins Projektverzeichnis
$projectPath = Join-Path $PSScriptRoot "JarvisApp"
Set-Location $projectPath

Write-Host "[1/4] Pruefe Ollama..." -ForegroundColor Yellow
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue

if (-not $ollamaCmd) {
    Write-Host "❌ Ollama wurde nicht gefunden." -ForegroundColor Red
    Write-Host "Bitte installiere Ollama und stelle sicher, dass es im PATH ist." -ForegroundColor Gray
    Write-Host "Danach: ollama serve" -ForegroundColor Gray
    Write-Host ""
} else {
    $ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
    if (-not $ollamaProcess) {
        Write-Host "Starte Ollama Server..." -ForegroundColor Yellow
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Minimized
    } else {
        Write-Host "Ollama Server laeuft bereits." -ForegroundColor Green
    }
    Write-Host ""
}

Write-Host "[1.5/4] Beende laufende JarvisApp..." -ForegroundColor Yellow
Get-Process -Name "JarvisApp" -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "" 

Write-Host "[2/4] Kompiliere Projekt..." -ForegroundColor Yellow
dotnet clean --nologo
dotnet build -c Release /p:Platform=x64 --nologo

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build fehlgeschlagen!" -ForegroundColor Red
    Read-Host "Drücke Enter zum Beenden"
    exit 1
}

Write-Host "✅ Build erfolgreich!" -ForegroundColor Green
Write-Host ""

Write-Host "[3/4] Suche ausführbare Datei..." -ForegroundColor Yellow
$exePath = Join-Path $projectPath "bin\x64\Release\net8.0-windows10.0.19041.0\JarvisApp.exe"

if (-not (Test-Path $exePath)) {
    Write-Host "❌ JarvisApp.exe nicht gefunden!" -ForegroundColor Red
    Write-Host "Erwarteter Pfad: $exePath" -ForegroundColor Gray
    Read-Host "Drücke Enter zum Beenden"
    exit 1
}

Write-Host "✅ Gefunden: JarvisApp.exe" -ForegroundColor Green
Write-Host ""

Write-Host "[4/4] Starte JARVIS App..." -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 Die App wird geöffnet..." -ForegroundColor Cyan
Write-Host ""

# Starte die App
Start-Process $exePath

Write-Host "✅ App gestartet!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Tipp: Um die App neu zu kompilieren und zu starten, führe dieses Skript erneut aus." -ForegroundColor Gray
Write-Host ""

# PowerShell Skript zur Überprüfung und Installation deutscher TTS-Stimmen
# Für JARVIS Sprachausgabe

Write-Host "🔍 Überprüfe verfügbare Text-zu-Sprache Stimmen..." -ForegroundColor Cyan

# Lade Speech Synthese Assembly
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer

Write-Host "`n📋 Verfügbare TTS-Stimmen:" -ForegroundColor Yellow

$germanVoices = @()
$allVoices = $synth.GetInstalledVoices()

foreach ($voice in $allVoices) {
    $voiceInfo = $voice.VoiceInfo
    $culture = $voiceInfo.Culture.Name
    $name = $voiceInfo.Name
    $gender = $voiceInfo.Gender
    
    Write-Host "  - Name: $name" -ForegroundColor White
    Write-Host "    Kultur: $culture, Geschlecht: $gender" -ForegroundColor Gray
    
    # Prüfe auf deutsche Stimmen
    if ($culture -like "de-*" -or $name -like "*German*" -or $name -like "*Deutsch*") {
        $germanVoices += $voiceInfo
        Write-Host "    ✅ DEUTSCHE STIMME GEFUNDEN!" -ForegroundColor Green
    }
    Write-Host ""
}

if ($germanVoices.Count -gt 0) {
    Write-Host "🎉 $($germanVoices.Count) deutsche Stimme(n) gefunden!" -ForegroundColor Green
    
    # Teste die erste deutsche Stimme
    $synth.SelectVoice($germanVoices[0].Name)
    Write-Host "`n🧪 Teste deutsche Stimme: $($germanVoices[0].Name)" -ForegroundColor Cyan
    
    # Test mit deutschem Text
    $testText = "Hallo! Ich bin JARVIS. Deutsche Sprachausgabe funktioniert einwandfrei."
    Write-Host "Test-Text: '$testText'" -ForegroundColor Gray
    
    try {
        $synth.Speak($testText)
        Write-Host "✅ Deutsche Sprachausgabe erfolgreich getestet!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Fehler beim Testen der Sprachausgabe: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Keine deutschen Stimmen gefunden!" -ForegroundColor Red
    Write-Host "`n📥 So installieren Sie deutsche Stimmen:" -ForegroundColor Yellow
    Write-Host "1. Windows Einstellungen → Zeit und Sprache → Sprache" -ForegroundColor White
    Write-Host "2. Deutsch hinzufügen (falls nicht vorhanden)" -ForegroundColor White
    Write-Host "3. Deutsch auswählen → Optionen" -ForegroundColor White
    Write-Host "4. Sprachpakete herunterladen" -ForegroundColor White
    Write-Host "5. Text-zu-Sprache → Stimme herunterladen" -ForegroundColor White
    Write-Host "`nEmpfohlene deutsche Stimmen:" -ForegroundColor Yellow
    Write-Host "- Microsoft Hedda Desktop (Deutsch)" -ForegroundColor White
    Write-Host "- Microsoft Katja Desktop (Deutsch)" -ForegroundColor White
    Write-Host "- Microsoft Stefan Desktop (Deutsch)" -ForegroundColor White
}

$synth.Dispose()
Write-Host "`n✨ Überprüfung abgeschlossen!" -ForegroundColor Cyan
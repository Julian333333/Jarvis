# Schnellstart-Anleitung

## ✅ Schritt 1: Visual Studio 2022 installieren

```powershell
# Mit winget installieren
winget install Microsoft.VisualStudio.2022.Community
```

**Oder manuell herunterladen:**
https://visualstudio.microsoft.com/de/downloads/

### Erforderliche Workloads:
- ✅ .NET Desktop-Entwicklung
- ✅ Entwicklung für die universelle Windows-Plattform
- ✅ Windows App SDK C# Vorlagen

## ✅ Schritt 2: Projekt öffnen

```powershell
# Solution in Visual Studio öffnen
cd "C:\Users\julia\OneDrive\Dokumente\GitHub\Jarvis"
start JarvisApp.sln
```

## ✅ Schritt 3: Build-Konfiguration

In Visual Studio:
1. Toolbar oben: Wähle **Debug** aus dem Dropdown
2. Platform: Wähle **x64**
3. Klicke auf ▶️ **JarvisApp** oder drücke **F5**

## ✅ Schritt 4: Erste Ausführung

Die App sollte nun:
- ✅ Kompilieren (kann 30-60 Sekunden dauern)
- ✅ Ein Fenster öffnen mit dem Titel "JARVIS AI Assistant"
- ✅ Eine moderne Windows 11 UI mit Fluent Design zeigen

## 🎯 Schnelltests

### Test 1: Eingabe senden
1. Gib "Hello JARVIS" im Textfeld ein
2. Klicke auf "Send"
3. ✅ Eine Demo-Antwort sollte erscheinen

### Test 2: Responsive Design
1. Ändere die Fenstergröße
2. ✅ UI sollte sich anpassen

### Test 3: Dark/Light Mode
1. Windows Einstellungen → Personalisierung → Farben
2. Wechsle zwischen Hell/Dunkel
3. ✅ App sollte Theme übernehmen

## 🐛 Probleme?

### "Solution failed to load"
```powershell
# NuGet-Pakete wiederherstellen
dotnet restore JarvisApp.sln
```

### "Platform x64 not found"
- Build → Configuration Manager
- Active Solution Platform → x64 auswählen

### "Windows App SDK missing"
```powershell
# NuGet-Cache leeren und neu installieren
dotnet nuget locals all --clear
dotnet restore JarvisApp.sln
```

### Immer noch Probleme?
1. Schließe Visual Studio
2. Lösche `JarvisApp\bin` und `JarvisApp\obj` Ordner
3. Öffne Visual Studio erneut
4. Build → Rebuild Solution

## 📞 Weitere Hilfe

Siehe vollständige Dokumentation in `README.md`

using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading.Tasks;

namespace JarvisApp.Services
{
    public class CommandService
    {
        private readonly AutomationService _automation;

        public CommandService()
        {
            _automation = new AutomationService();
        }

        // Windows API für Lautstärke
        [DllImport("user32.dll")]
        private static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);

        private const byte VK_VOLUME_UP = 0xAF;
        private const byte VK_VOLUME_DOWN = 0xAE;
        private const byte VK_VOLUME_MUTE = 0xAD;
        private const uint KEYEVENTF_KEYUP = 0x0002;

        /// <summary>
        /// Verarbeitet einen Command und gibt zurück, ob er ausgeführt wurde
        /// </summary>
        public async Task<CommandResult> ProcessCommandAsync(string input)
        {
            var lowerInput = input.ToLower().Trim();

            // Lautstärke-Commands
            if (lowerInput.Contains("lautstärke") || lowerInput.Contains("lautstarke") || lowerInput.Contains("volume"))
            {
                if (lowerInput.Contains("erhöh") || lowerInput.Contains("erhoh") || lowerInput.Contains("lauter") || lowerInput.Contains("hoch"))
                {
                    VolumeUp();
                    return new CommandResult { Success = true, Message = "🔊 Lautstärke erhöht" };
                }
                if (lowerInput.Contains("leiser") || lowerInput.Contains("runter") || lowerInput.Contains("reduzier"))
                {
                    VolumeDown();
                    return new CommandResult { Success = true, Message = "🔉 Lautstärke verringert" };
                }
                if (lowerInput.Contains("stumm") || lowerInput.Contains("mute") || lowerInput.Contains("aus"))
                {
                    VolumeMute();
                    return new CommandResult { Success = true, Message = "🔇 Ton stummgeschaltet" };
                }
            }

            // Programme öffnen
            if (lowerInput.Contains("öffne") || lowerInput.Contains("offne") || lowerInput.Contains("starte") || lowerInput.Contains("öffnen"))
            {
                if (lowerInput.Contains("browser") || lowerInput.Contains("edge"))
                {
                    OpenProgram("microsoft-edge:");
                    return new CommandResult { Success = true, Message = "🌐 Browser geöffnet" };
                }
                if (lowerInput.Contains("notepad") || lowerInput.Contains("editor"))
                {
                    OpenProgram("notepad.exe");
                    return new CommandResult { Success = true, Message = "📝 Notepad geöffnet" };
                }
                if (lowerInput.Contains("rechner") || lowerInput.Contains("calculator") || lowerInput.Contains("taschenrechner"))
                {
                    OpenProgram("calc.exe");
                    return new CommandResult { Success = true, Message = "🔢 Rechner geöffnet" };
                }
                if (lowerInput.Contains("explorer") || lowerInput.Contains("datei"))
                {
                    OpenProgram("explorer.exe");
                    return new CommandResult { Success = true, Message = "📁 Explorer geöffnet" };
                }
                if (lowerInput.Contains("einstellungen") || lowerInput.Contains("settings"))
                {
                    OpenProgram("ms-settings:");
                    return new CommandResult { Success = true, Message = "⚙️ Einstellungen geöffnet" };
                }
                if (lowerInput.Contains("paint"))
                {
                    OpenProgram("mspaint.exe");
                    return new CommandResult { Success = true, Message = "🎨 Paint geöffnet" };
                }
                if (lowerInput.Contains("cmd") || lowerInput.Contains("terminal") || lowerInput.Contains("konsole"))
                {
                    OpenProgram("cmd.exe");
                    return new CommandResult { Success = true, Message = "💻 Terminal geöffnet" };
                }
                if (lowerInput.Contains("powershell"))
                {
                    OpenProgram("powershell.exe");
                    return new CommandResult { Success = true, Message = "💻 PowerShell geöffnet" };
                }
            }

            // Websites öffnen
            if (lowerInput.Contains("gehe zu") || lowerInput.Contains("öffne") || lowerInput.Contains("website"))
            {
                if (lowerInput.Contains("youtube"))
                {
                    OpenUrl("https://www.youtube.com");
                    return new CommandResult { Success = true, Message = "📺 YouTube geöffnet" };
                }
                if (lowerInput.Contains("google"))
                {
                    OpenUrl("https://www.google.com");
                    return new CommandResult { Success = true, Message = "🔍 Google geöffnet" };
                }
                if (lowerInput.Contains("github"))
                {
                    OpenUrl("https://www.github.com");
                    return new CommandResult { Success = true, Message = "💻 GitHub geöffnet" };
                }
            }

            // System-Commands
            if (lowerInput.Contains("herunterfahren") || lowerInput.Contains("shutdown") || lowerInput.Contains("ausschalten"))
            {
                return new CommandResult 
                { 
                    Success = true, 
                    Message = "⚠️ Herunterfahren-Befehl erkannt.\n\nAus Sicherheitsgründen wurde dieser Command nicht ausgeführt.\nBitte verwende den Windows-Startmenü, um das System herunterzufahren.",
                    IsWarning = true
                };
            }

            if (lowerInput.Contains("neustart") || lowerInput.Contains("restart") || lowerInput.Contains("reboot"))
            {
                return new CommandResult 
                { 
                    Success = true, 
                    Message = "⚠️ Neustart-Befehl erkannt.\n\nAus Sicherheitsgründen wurde dieser Command nicht ausgeführt.\nBitte verwende den Windows-Startmenü, um das System neu zu starten.",
                    IsWarning = true
                };
            }

            // Text schreiben
            if (lowerInput.Contains("schreibe") || lowerInput.Contains("tippe") || lowerInput.Contains("gib ein"))
            {
                var textToType = ExtractTextAfterKeyword(input, new[] { "schreibe", "tippe", "gib ein" });
                if (!string.IsNullOrEmpty(textToType))
                {
                    await _automation.TypeTextAsync(textToType, 30);
                    return new CommandResult { Success = true, Message = $"⌨️ Text eingegeben: {textToType}" };
                }
            }

            // Tastenkombinationen
            if (lowerInput.Contains("drücke") || lowerInput.Contains("drucke") || lowerInput.Contains("taste"))
            {
                if (lowerInput.Contains("enter"))
                {
                    _automation.PressKey(VirtualKeyCode.RETURN);
                    return new CommandResult { Success = true, Message = "⌨️ Enter gedrückt" };
                }
                if (lowerInput.Contains("strg c") || lowerInput.Contains("ctrl c") || lowerInput.Contains("kopieren"))
                {
                    _automation.PressKeyCombination(VirtualKeyCode.CONTROL, VirtualKeyCode.VK_C);
                    return new CommandResult { Success = true, Message = "⌨️ Strg+C (Kopieren)" };
                }
                if (lowerInput.Contains("strg v") || lowerInput.Contains("ctrl v") || lowerInput.Contains("einfügen"))
                {
                    _automation.PressKeyCombination(VirtualKeyCode.CONTROL, VirtualKeyCode.VK_V);
                    return new CommandResult { Success = true, Message = "⌨️ Strg+V (Einfügen)" };
                }
                if (lowerInput.Contains("strg x") || lowerInput.Contains("ctrl x") || lowerInput.Contains("ausschneiden"))
                {
                    _automation.PressKeyCombination(VirtualKeyCode.CONTROL, VirtualKeyCode.VK_X);
                    return new CommandResult { Success = true, Message = "⌨️ Strg+X (Ausschneiden)" };
                }
                if (lowerInput.Contains("strg z") || lowerInput.Contains("ctrl z") || lowerInput.Contains("rückgängig"))
                {
                    _automation.PressKeyCombination(VirtualKeyCode.CONTROL, VirtualKeyCode.VK_Z);
                    return new CommandResult { Success = true, Message = "⌨️ Strg+Z (Rückgängig)" };
                }
                if (lowerInput.Contains("alt f4") || lowerInput.Contains("fenster schließen"))
                {
                    _automation.PressKeyCombination(VirtualKeyCode.ALT, VirtualKeyCode.F4);
                    return new CommandResult { Success = true, Message = "⌨️ Alt+F4 (Fenster schließen)" };
                }
                if (lowerInput.Contains("alt tab"))
                {
                    _automation.PressKeyCombination(VirtualKeyCode.ALT, VirtualKeyCode.TAB);
                    return new CommandResult { Success = true, Message = "⌨️ Alt+Tab (Fenster wechseln)" };
                }
                if (lowerInput.Contains("windows") || lowerInput.Contains("win"))
                {
                    _automation.PressKey(VirtualKeyCode.LWIN);
                    return new CommandResult { Success = true, Message = "⌨️ Windows-Taste gedrückt" };
                }
            }

            // Maus-Steuerung
            if (lowerInput.Contains("klick") || lowerInput.Contains("click"))
            {
                if (lowerInput.Contains("links"))
                {
                    _automation.LeftClick();
                    return new CommandResult { Success = true, Message = "🖱️ Linksklick ausgeführt" };
                }
                if (lowerInput.Contains("rechts"))
                {
                    _automation.RightClick();
                    return new CommandResult { Success = true, Message = "🖱️ Rechtsklick ausgeführt" };
                }
                if (lowerInput.Contains("doppel"))
                {
                    _automation.DoubleClick();
                    return new CommandResult { Success = true, Message = "🖱️ Doppelklick ausgeführt" };
                }
                // Normaler Klick
                _automation.LeftClick();
                return new CommandResult { Success = true, Message = "🖱️ Klick ausgeführt" };
            }

            if (lowerInput.Contains("bewege maus") || lowerInput.Contains("maus position"))
            {
                // Versuche Koordinaten zu extrahieren
                var numbers = System.Text.RegularExpressions.Regex.Matches(input, @"\d+")
                    .Select(m => int.Parse(m.Value)).ToArray();
                
                if (numbers.Length >= 2)
                {
                    _automation.MoveMouse(numbers[0], numbers[1]);
                    return new CommandResult { Success = true, Message = $"🖱️ Maus zu Position ({numbers[0]}, {numbers[1]})" };
                }
                else
                {
                    var pos = _automation.GetMousePosition();
                    return new CommandResult { Success = true, Message = $"🖱️ Aktuelle Position: ({pos.X}, {pos.Y})" };
                }
            }

            // Fenster-Management
            if (lowerInput.Contains("fenster") || lowerInput.Contains("window"))
            {
                if (lowerInput.Contains("liste") || lowerInput.Contains("zeige"))
                {
                    var windows = _automation.GetOpenWindows();
                    if (windows.Count > 0)
                    {
                        var list = string.Join("\n", windows.Take(10).Select((w, i) => $"{i + 1}. {w}"));
                        return new CommandResult { Success = true, Message = $"📋 Offene Fenster:\n{list}" };
                    }
                    return new CommandResult { Success = true, Message = "📋 Keine Fenster gefunden" };
                }
                if (lowerInput.Contains("fokus") || lowerInput.Contains("wechsel"))
                {
                    var windowName = ExtractTextAfterKeyword(input, new[] { "fokus", "wechsel zu", "wechsel" });
                    if (!string.IsNullOrEmpty(windowName))
                    {
                        if (_automation.FocusWindow(windowName))
                        {
                            return new CommandResult { Success = true, Message = $"🪟 Fenster '{windowName}' aktiviert" };
                        }
                        return new CommandResult { Success = false, Message = $"❌ Fenster '{windowName}' nicht gefunden" };
                    }
                }
                if (lowerInput.Contains("maximier"))
                {
                    var windowName = ExtractTextAfterKeyword(input, new[] { "maximiere", "maximier" });
                    if (!string.IsNullOrEmpty(windowName) && _automation.MaximizeWindow(windowName))
                    {
                        return new CommandResult { Success = true, Message = $"🪟 Fenster '{windowName}' maximiert" };
                    }
                }
                if (lowerInput.Contains("minimi"))
                {
                    var windowName = ExtractTextAfterKeyword(input, new[] { "minimiere", "minimi" });
                    if (!string.IsNullOrEmpty(windowName) && _automation.MinimizeWindow(windowName))
                    {
                        return new CommandResult { Success = true, Message = $"🪟 Fenster '{windowName}' minimiert" };
                    }
                }
                if (lowerInput.Contains("schließ") || lowerInput.Contains("schliess"))
                {
                    var windowName = ExtractTextAfterKeyword(input, new[] { "schließe", "schliesse" });
                    if (!string.IsNullOrEmpty(windowName) && _automation.CloseWindow(windowName))
                    {
                        return new CommandResult { Success = true, Message = $"🪟 Fenster '{windowName}' geschlossen" };
                    }
                }
                if (lowerInput.Contains("aktuell"))
                {
                    var title = _automation.GetActiveWindowTitle();
                    return new CommandResult { Success = true, Message = $"🪟 Aktives Fenster: {title}" };
                }
            }

            // Prozess-Management
            if (lowerInput.Contains("prozess") || lowerInput.Contains("process"))
            {
                if (lowerInput.Contains("liste"))
                {
                    var processes = _automation.GetRunningProcesses();
                    var list = string.Join("\n", processes.Take(10).Select((p, i) => $"{i + 1}. {p}"));
                    return new CommandResult { Success = true, Message = $"💻 Laufende Prozesse:\n{list}" };
                }
                if (lowerInput.Contains("beende") || lowerInput.Contains("kill"))
                {
                    var processName = ExtractTextAfterKeyword(input, new[] { "beende", "kill" });
                    if (!string.IsNullOrEmpty(processName) && _automation.KillProcess(processName))
                    {
                        return new CommandResult { Success = true, Message = $"💻 Prozess '{processName}' beendet" };
                    }
                }
            }

            // Bildschirm-Info
            if (lowerInput.Contains("bildschirm") || lowerInput.Contains("auflösung") || lowerInput.Contains("screen"))
            {
                var res = _automation.GetScreenResolution();
                return new CommandResult { Success = true, Message = $"🖥️ Bildschirmauflösung: {res.Width} x {res.Height}" };
            }

            // Zeit und Datum
            if (lowerInput.Contains("wie spät") || lowerInput.Contains("uhrzeit") || lowerInput.Contains("zeit"))
            {
                var time = DateTime.Now.ToString("HH:mm");
                return new CommandResult { Success = true, Message = $"🕐 Es ist {time} Uhr" };
            }

            if (lowerInput.Contains("welches datum") || lowerInput.Contains("welcher tag") || lowerInput.Contains("datum"))
            {
                var date = DateTime.Now.ToString("dddd, dd. MMMM yyyy");
                return new CommandResult { Success = true, Message = $"📅 Heute ist {date}" };
            }

            // Kein Command erkannt
            await Task.CompletedTask;
            return new CommandResult { Success = false };
        }

        private void VolumeUp()
        {
            for (int i = 0; i < 2; i++) // 2x erhöhen
            {
                keybd_event(VK_VOLUME_UP, 0, 0, UIntPtr.Zero);
                keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            }
        }

        private void VolumeDown()
        {
            for (int i = 0; i < 2; i++) // 2x verringern
            {
                keybd_event(VK_VOLUME_DOWN, 0, 0, UIntPtr.Zero);
                keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            }
        }

        private void VolumeMute()
        {
            keybd_event(VK_VOLUME_MUTE, 0, 0, UIntPtr.Zero);
            keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
        }

        private void OpenProgram(string programPath)
        {
            try
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = programPath,
                    UseShellExecute = true
                });
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Fehler beim Öffnen von {programPath}: {ex.Message}");
            }
        }

        private void OpenUrl(string url)
        {
            try
            {
                Process.Start(new ProcessStartInfo
                {
                    FileName = url,
                    UseShellExecute = true
                });
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"Fehler beim Öffnen von {url}: {ex.Message}");
            }
        }

        private string ExtractTextAfterKeyword(string input, string[] keywords)
        {
            var lowerInput = input.ToLower();
            foreach (var keyword in keywords)
            {
                var index = lowerInput.IndexOf(keyword.ToLower());
                if (index >= 0)
                {
                    var startIndex = index + keyword.Length;
                    if (startIndex < input.Length)
                    {
                        return input.Substring(startIndex).Trim();
                    }
                }
            }
            return string.Empty;
        }
    }

    public class CommandResult
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public bool IsWarning { get; set; }
    }
}

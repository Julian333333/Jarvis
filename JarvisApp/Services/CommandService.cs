using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading.Tasks;

namespace JarvisApp.Services
{
    public class CommandService
    {
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
    }

    public class CommandResult
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public bool IsWarning { get; set; }
    }
}

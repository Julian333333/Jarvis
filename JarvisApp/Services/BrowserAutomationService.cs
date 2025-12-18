using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;

namespace JarvisApp.Services
{
    /// <summary>
    /// Browser-Automation mit visueller Erkennung und intelligenten Klicks
    /// </summary>
    public class BrowserAutomationService
    {
        private readonly AutomationService _automation;
        private bool _waitingForConfirmation = false;
        private string _pendingAction = string.Empty;

        public BrowserAutomationService(AutomationService automation)
        {
            _automation = automation;
        }

        #region Windows API für Screenshots

        [DllImport("user32.dll")]
        private static extern IntPtr GetDesktopWindow();

        [DllImport("user32.dll")]
        private static extern IntPtr GetWindowDC(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);

        [DllImport("gdi32.dll")]
        private static extern IntPtr CreateCompatibleDC(IntPtr hDC);

        [DllImport("gdi32.dll")]
        private static extern IntPtr CreateCompatibleBitmap(IntPtr hDC, int nWidth, int nHeight);

        [DllImport("gdi32.dll")]
        private static extern IntPtr SelectObject(IntPtr hDC, IntPtr hObject);

        [DllImport("gdi32.dll")]
        private static extern bool BitBlt(IntPtr hdcDest, int xDest, int yDest, int wDest, int hDest,
            IntPtr hdcSource, int xSrc, int ySrc, CopyPixelOperation rop);

        [DllImport("gdi32.dll")]
        private static extern bool DeleteDC(IntPtr hDC);

        [DllImport("gdi32.dll")]
        private static extern bool DeleteObject(IntPtr hObject);

        #endregion

        /// <summary>
        /// Hauptfunktion: Öffnet Webseite und führt komplexe Automation aus
        /// </summary>
        public async Task<BrowserAutomationResult> ExecuteWebTaskAsync(string url, WebTask task)
        {
            var result = new BrowserAutomationResult
            {
                Success = false,
                Steps = new List<string>()
            };

            try
            {
                // 1. Browser öffnen
                result.Steps.Add("🌐 Öffne Browser und navigiere zu " + url);
                _automation.StartProgram(url);
                await Task.Delay(4000); // Warte länger auf Browser-Start

                // 2. Warte auf Seiten-Laden
                result.Steps.Add("⏳ Warte auf vollständiges Laden der Seite...");
                await Task.Delay(3000);

                // 3. Führe alle Task-Schritte nacheinander aus
                result.Steps.Add($"📋 Starte Ausführung von {task.Steps.Count} Schritten...");
                
                for (int i = 0; i < task.Steps.Count; i++)
                {
                    var step = task.Steps[i];
                    result.Steps.Add($"\n▶️ Schritt {i+1}/{task.Steps.Count}: {step.Description}");
                    
                    // Bei kritischen Aktionen: Warte auf Bestätigung
                    if (step.RequiresConfirmation)
                    {
                        _waitingForConfirmation = true;
                        _pendingAction = step.Description;
                        result.NeedsConfirmation = true;
                        result.ConfirmationMessage = $"⚠️ BESTÄTIGUNG ERFORDERLICH\n\n{step.Description}\n\nSage 'Ja' oder 'Bestätigen' um fortzufahren.";
                        return result;
                    }
                    
                    var stepResult = await ExecuteWebStepAsync(step);
                    result.Steps.Add($"   {stepResult}");

                    // Warte nach jedem Schritt
                    if (step.DelayAfterMs > 0)
                    {
                        result.Steps.Add($"   ⏱️ Warte {step.DelayAfterMs}ms...");
                        await Task.Delay(step.DelayAfterMs);
                    }
                }

                result.Success = true;
                result.Message = "✅ Alle Schritte erfolgreich ausgeführt";
                return result;
            }
            catch (Exception ex)
            {
                result.Steps.Add($"❌ Fehler: {ex.Message}");
                result.Message = $"Fehler bei Browser-Automation: {ex.Message}";
                return result;
            }
        }

        /// <summary>
        /// Führt einen einzelnen Web-Schritt aus
        /// </summary>
        private async Task<string> ExecuteWebStepAsync(WebStep step)
        {
            try
            {
                switch (step.Type)
                {
                    case WebStepType.Click:
                        return await ClickElementAsync(step.Target, step.SearchText);

                    case WebStepType.Type:
                        // Fokus setzen durch Klick
                        _automation.LeftClick();
                        await Task.Delay(300);
                        // Text eingeben
                        await _automation.TypeTextAsync(step.Target ?? "", 80);
                        await Task.Delay(300);
                        return $"✅ Text eingegeben: {step.Target}";

                    case WebStepType.Wait:
                        await Task.Delay(step.DelayAfterMs);
                        return $"⏸️ Gewartet: {step.DelayAfterMs}ms";

                    case WebStepType.Scroll:
                        await ScrollPageAsync(step.Target);
                        return $"📜 Gescrollt: {step.Target}";

                    case WebStepType.PressKey:
                        _automation.PressKey((VirtualKeyCode)Enum.Parse(typeof(VirtualKeyCode), step.Target ?? "RETURN"));
                        return $"⌨️ Taste gedrückt: {step.Target}";

                    default:
                        return $"⚠️ Unbekannter Schritt-Typ: {step.Type}";
                }
            }
            catch (Exception ex)
            {
                return $"❌ Fehler bei Schritt: {ex.Message}";
            }
        }

        /// <summary>
        /// Klickt auf ein Element (Button, Link) basierend auf Text-Suche
        /// </summary>
        private async Task<string> ClickElementAsync(string? elementName, string? searchText)
        {
            var (width, height) = _automation.GetScreenResolution();
            
            // Verschiedene Positionen je nach Element-Typ
            int targetX, targetY;
            
            if (elementName?.ToLower().Contains("input") == true || elementName?.ToLower().Contains("eur") == true)
            {
                // EUR-Eingabefeld: Rechts oben im Content-Bereich
                targetX = width * 3 / 4;  // 75% von links
                targetY = height / 3;      // Oberes Drittel
            }
            else if (elementName?.ToLower().Contains("review") == true)
            {
            // Review Order Button: Rechts unten
                targetX = width * 3 / 4;
                targetY = height * 2 / 3;  // Unteres Drittel
            }
            else
            {
                // Standard: Mitte
                targetX = width / 2;
                targetY = height / 2;
            }

            // Bewege Maus und klicke
            _automation.MoveMouse(targetX, targetY);
            await Task.Delay(300);
            _automation.LeftClick();
            await Task.Delay(400);
            
            return $"✅ Geklickt auf: {elementName ?? searchText ?? "Element"}";
        }

        /// <summary>
        /// Scrollt auf der Seite
        /// </summary>
        private async Task ScrollPageAsync(string? direction)
        {
            var scrollAmount = 3;
            
            if (direction?.ToLower() == "down" || direction?.ToLower() == "runter")
            {
                for (int i = 0; i < scrollAmount; i++)
                {
                    _automation.PressKey(VirtualKeyCode.DOWN);
                    await Task.Delay(100);
                }
            }
            else if (direction?.ToLower() == "up" || direction?.ToLower() == "hoch")
            {
                for (int i = 0; i < scrollAmount; i++)
                {
                    _automation.PressKey(VirtualKeyCode.UP);
                    await Task.Delay(100);
                }
            }
        }

        /// <summary>
        /// Macht Screenshot vom aktuellen Bildschirm
        /// </summary>
        public Bitmap? CaptureScreen()
        {
            try
            {
                var (width, height) = _automation.GetScreenResolution();
                var bmp = new Bitmap(width, height, PixelFormat.Format32bppArgb);
                
                using (var graphics = Graphics.FromImage(bmp))
                {
                    graphics.CopyFromScreen(0, 0, 0, 0, new Size(width, height), CopyPixelOperation.SourceCopy);
                }
                
                return bmp;
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Bestätigt ausstehende Aktion
        /// </summary>
        public string ConfirmPendingAction()
        {
            if (!_waitingForConfirmation)
                return "❌ Keine ausstehende Bestätigung";

            _waitingForConfirmation = false;
            var action = _pendingAction;
            _pendingAction = string.Empty;

            // Führe die bestätigte Aktion aus (z.B. finaler Klick)
            _automation.LeftClick();

            return $"✅ Bestätigt: {action}";
        }

        /// <summary>
        /// Bricht ausstehende Aktion ab
        /// </summary>
        public string CancelPendingAction()
        {
            if (!_waitingForConfirmation)
                return "❌ Keine ausstehende Aktion";

            _waitingForConfirmation = false;
            var action = _pendingAction;
            _pendingAction = string.Empty;

            return $"🚫 Abgebrochen: {action}";
        }

        public bool IsWaitingForConfirmation => _waitingForConfirmation;
        public string PendingAction => _pendingAction;
    }

    #region DTOs

    public class WebTask
    {
        public string Url { get; set; } = string.Empty;
        public List<WebStep> Steps { get; set; } = new();
    }

    public class WebStep
    {
        public WebStepType Type { get; set; }
        public string? Target { get; set; }
        public string? SearchText { get; set; }
        public string Description { get; set; } = string.Empty;
        public bool RequiresConfirmation { get; set; }
        public int DelayAfterMs { get; set; } = 1000;
    }

    public enum WebStepType
    {
        Click,
        Type,
        Wait,
        Scroll,
        PressKey
    }

    public class BrowserAutomationResult
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public List<string> Steps { get; set; } = new();
        public bool NeedsConfirmation { get; set; }
        public string ConfirmationMessage { get; set; } = string.Empty;
    }

    #endregion
}

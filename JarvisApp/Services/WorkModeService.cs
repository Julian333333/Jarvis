using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace JarvisApp.Services
{
    /// <summary>
    /// Work Mode Service - Startet YouTube Musik und minimiert Browser
    /// </summary>
    public class WorkModeService
    {
        private readonly AutomationService _automation;

        public WorkModeService(AutomationService automation)
        {
            _automation = automation;
        }

        /// <summary>
        /// Startet Work Mode: YouTube "Back in Black" + Lautstärke 50% + Browser minimieren
        /// </summary>
        public async Task<string> ExecuteWorkModeAsync()
        {
            var results = new List<string>();
            results.Add("🎵 WORK MODE AKTIVIERT\n");

            try
            {
                // 1. YouTube öffnen mit "Back in Black"
                results.Add("▶️ Öffne YouTube...");
                var youtubeUrl = "https://www.youtube.com/results?search_query=back+in+black";
                _automation.StartProgram(youtubeUrl);
                await Task.Delay(1000); // Warte auf Browser-Start

                // 2. Erstes Video anklicken (Mitte des Bildschirms)
                results.Add("▶️ Klicke auf erstes Video...");
                var (width, height) = _automation.GetScreenResolution();
                _automation.MoveMouse(width / 2, height / 3);
                await Task.Delay(300);
                _automation.LeftClick();
                await Task.Delay(1000); // Warte bis Video lädt

                // 3. Lautstärke auf 50% setzen
                results.Add("🔊 Setze Lautstärke auf 50%...");
                
                // Setze Volume auf ~0%
                for (int i = 0; i < 25; i++)
                {
                    _automation.PressKey(VirtualKeyCode.VOLUME_DOWN);
                    await Task.Delay(20);
                }
                await Task.Delay(200);
                
                // Erhöhe auf ~50%
                for (int i = 0; i < 13; i++)
                {
                    _automation.PressKey(VirtualKeyCode.VOLUME_UP);
                    await Task.Delay(20);
                }

                // 4. Browser minimieren
                results.Add("🪟 Minimiere Browser...");
                await Task.Delay(500);
                _automation.PressKeyCombination(VirtualKeyCode.LWIN, VirtualKeyCode.DOWN);
                
                results.Add("\n✅ Work Mode aktiv! Musik läuft im Hintergrund.");
                return string.Join("\n", results);
            }
            catch (Exception ex)
            {
                results.Add($"\n❌ Fehler: {ex.Message}");
                return string.Join("\n", results);
            }
        }
    }
}

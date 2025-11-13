using System;
using System.Threading.Tasks;
using Windows.Media.SpeechRecognition;

namespace JarvisApp.Services
{
    public class SpeechService
    {
        private SpeechRecognizer _speechRecognizer;

        public SpeechService()
        {
            InitializeAsync();
        }

        private async void InitializeAsync()
        {
            try
            {
                _speechRecognizer = new SpeechRecognizer();
                
                // Wartet bis zu 10 Sekunden auf Sprache
                _speechRecognizer.Timeouts.InitialSilenceTimeout = TimeSpan.FromSeconds(10);
                
                // Stoppt nach 0,5 Sekunden Stille
                _speechRecognizer.Timeouts.EndSilenceTimeout = TimeSpan.FromSeconds(0.5);
                
                await _speechRecognizer.CompileConstraintsAsync();
            }
            catch
            {
                // Initialization will be retried when needed
            }
        }

        public async Task<string> ListenAsync()
        {
            try
            {
                if (_speechRecognizer == null)
                {
                    _speechRecognizer = new SpeechRecognizer();
                    
                    // Wartet bis zu 10 Sekunden auf Sprache
                    _speechRecognizer.Timeouts.InitialSilenceTimeout = TimeSpan.FromSeconds(10);
                    
                    // Stoppt nach 0,5 Sekunden Stille
                    _speechRecognizer.Timeouts.EndSilenceTimeout = TimeSpan.FromSeconds(0.5);
                    
                    await _speechRecognizer.CompileConstraintsAsync();
                }

                var result = await _speechRecognizer.RecognizeAsync();
                
                if (result.Status == SpeechRecognitionResultStatus.Success)
                {
                    return result.Text;
                }
                else
                {
                    return $"❌ Spracherkennung fehlgeschlagen: {result.Status}";
                }
            }
            catch (UnauthorizedAccessException)
            {
                return "❌ Mikrofonzugriff verweigert.\n\n" +
                       "💡 Lösung:\n" +
                       "1. Öffne Windows Einstellungen\n" +
                       "2. Gehe zu Datenschutz & Sicherheit → Mikrofon\n" +
                       "3. Aktiviere 'Mikrofon-Zugriff'\n" +
                       "4. Aktiviere 'Desktop-Apps Zugriff auf Mikrofon erlauben'";
            }
            catch (Exception ex)
            {
                return $"❌ Fehler bei Spracherkennung: {ex.Message}\n\n" +
                       "💡 Mögliche Lösungen:\n" +
                       "• Stelle sicher, dass ein Mikrofon angeschlossen ist\n" +
                       "• Überprüfe die Mikrofon-Berechtigungen in Windows\n" +
                       "• Aktiviere Windows-Spracherkennung in den Einstellungen";
            }
        }

        public void Dispose()
        {
            _speechRecognizer?.Dispose();
        }
    }
}

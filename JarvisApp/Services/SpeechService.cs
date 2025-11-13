using System;
using System.Threading.Tasks;
using Windows.Media.SpeechRecognition;
using Windows.Media.SpeechSynthesis;
using Windows.Storage.Streams;

namespace JarvisApp.Services
{
    public class SpeechService
    {
        private SpeechRecognizer? _speechRecognizer;
        private SpeechSynthesizer? _speechSynthesizer;

        public SpeechService()
        {
            InitializeAsync();
        }

        private async void InitializeAsync()
        {
            try
            {
                _speechRecognizer = new SpeechRecognizer();
                await _speechRecognizer.CompileConstraintsAsync();
                _speechSynthesizer = new SpeechSynthesizer();
            }
            catch
            {
                // Initialization will be retried when needed
            }
        }

        /// <summary>
        /// Startet Spracheingabe und gibt den erkannten Text zurück
        /// </summary>
        public async Task<string> ListenAsync()
        {
            try
            {
                if (_speechRecognizer == null)
                {
                    _speechRecognizer = new SpeechRecognizer();
                    
                    // Kontinuierliche Erkennung mit automatischem Stop bei Stille
                    _speechRecognizer.Timeouts.InitialSilenceTimeout = TimeSpan.FromSeconds(10);
                    _speechRecognizer.Timeouts.EndSilenceTimeout = TimeSpan.FromSeconds(1.5);
                    
                    await _speechRecognizer.CompileConstraintsAsync();
                }

                // Einmaliges Erkennen - wartet auf Sprache und stoppt automatisch bei Stille
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

        /// <summary>
        /// Spricht den gegebenen Text aus
        /// </summary>
        public async Task<IRandomAccessStream?> SpeakAsync(string text)
        {
            try
            {
                if (_speechSynthesizer == null)
                {
                    _speechSynthesizer = new SpeechSynthesizer();
                }

                var stream = await _speechSynthesizer.SynthesizeTextToStreamAsync(text);
                return stream;
            }
            catch
            {
                return null;
            }
        }

        public void Dispose()
        {
            _speechRecognizer?.Dispose();
            _speechSynthesizer?.Dispose();
        }
    }
}

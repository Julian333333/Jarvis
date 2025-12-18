using System;
using System.Globalization;
using System.Linq;
using System.Speech.Recognition;
using System.Speech.Synthesis;

namespace JarvisApp.Services
{
    /// <summary>
    /// Verwaltet Sprachaufnahme (Hotword + STT) und Sprachausgabe (TTS)
    /// </summary>
    public class SpeechService : IDisposable
    {
        private readonly SpeechRecognitionEngine? _recognizer;
        private readonly SpeechSynthesizer _synthesizer;
        private readonly string[] _hotwords = new[] { "jarvis", "hey jarvis" };
        private bool _awaitingCommand;
        private bool _isListening;

        public bool IsAvailable => _recognizer != null;
        public bool IsListening => _isListening;

        public event EventHandler? HotwordDetected;
        public event EventHandler<string>? CommandRecognized;
        public event EventHandler<bool>? ListeningStateChanged;
        public event EventHandler<string>? ErrorOccurred;

        public SpeechService()
        {
            try
            {
                _recognizer = CreateRecognizer();
                if (_recognizer != null)
                {
                    _recognizer.LoadGrammar(new DictationGrammar());
                    _recognizer.SpeechRecognized += OnSpeechRecognized;
                    _recognizer.AudioStateChanged += OnAudioStateChanged;
                    _recognizer.RecognizeCompleted += OnRecognizeCompleted;
                }
            }
            catch (Exception ex)
            {
                _recognizer = null;
                ErrorOccurred?.Invoke(this, $"Spracherkennung nicht verfügbar: {ex.Message}");
            }

            _synthesizer = new SpeechSynthesizer();
            try
            {
                _synthesizer.SelectVoiceByHints(VoiceGender.Male, VoiceAge.Adult, 0, new CultureInfo("de-DE"));
            }
            catch
            {
                // Fallback auf Standardsprache
            }
        }

        private SpeechRecognitionEngine? CreateRecognizer()
        {
            try
            {
                return new SpeechRecognitionEngine(new CultureInfo("de-DE"));
            }
            catch
            {
                try
                {
                    return new SpeechRecognitionEngine(new CultureInfo("en-US"));
                }
                catch
                {
                    return null;
                }
            }
        }

        public bool StartListening()
        {
            var recognizer = _recognizer;
            if (recognizer == null) return false;
            if (_isListening) return true;

            try
            {
                recognizer.SetInputToDefaultAudioDevice();
                recognizer.RecognizeAsync(RecognizeMode.Multiple);
                _isListening = true;
                ListeningStateChanged?.Invoke(this, true);
                return true;
            }
            catch (Exception ex)
            {
                ErrorOccurred?.Invoke(this, ex.Message);
                return false;
            }
        }

        public void StopListening()
        {
            var recognizer = _recognizer;
            if (recognizer == null) return;
            if (!_isListening) return;

            try
            {
                recognizer.RecognizeAsyncStop();
                _isListening = false;
                ListeningStateChanged?.Invoke(this, false);
            }
            catch (Exception ex)
            {
                ErrorOccurred?.Invoke(this, ex.Message);
            }
        }

        public void SpeakAsync(string text)
        {
            if (string.IsNullOrWhiteSpace(text)) return;
            _synthesizer.SpeakAsyncCancelAll();
            _synthesizer.SpeakAsync(text);
        }

        private void OnSpeechRecognized(object? sender, SpeechRecognizedEventArgs e)
        {
            var result = e.Result;
            var recognizedText = result?.Text?.Trim();
            if (result == null || string.IsNullOrWhiteSpace(recognizedText)) return;

            var lower = recognizedText.ToLowerInvariant();
            System.Diagnostics.Debug.WriteLine($"[Speech] Recognized: {recognizedText} (Confidence: {result.Confidence:P0})");

            if (_hotwords.Any(hw => lower.Contains(hw)))
            {
                _awaitingCommand = true;
                HotwordDetected?.Invoke(this, EventArgs.Empty);
                return;
            }

            if (_awaitingCommand)
            {
                _awaitingCommand = false;
                CommandRecognized?.Invoke(this, recognizedText);
            }
        }

        private void OnAudioStateChanged(object? sender, AudioStateChangedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine($"[Speech] AudioState: {e.AudioState}");
        }

        private void OnRecognizeCompleted(object? sender, RecognizeCompletedEventArgs e)
        {
            System.Diagnostics.Debug.WriteLine("[Speech] Recognize completed");
            _isListening = false;
            ListeningStateChanged?.Invoke(this, false);

            if (e.Error != null)
            {
                ErrorOccurred?.Invoke(this, e.Error.Message);
            }
        }

        public void Dispose()
        {
            StopListening();
            if (_recognizer != null)
            {
                _recognizer.SpeechRecognized -= OnSpeechRecognized;
                _recognizer.AudioStateChanged -= OnAudioStateChanged;
                _recognizer.RecognizeCompleted -= OnRecognizeCompleted;
                _recognizer.Dispose();
            }

            _synthesizer.Dispose();
        }
    }
}

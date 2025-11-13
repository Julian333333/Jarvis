using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using JarvisApp.Services;

namespace JarvisApp
{
    public sealed partial class MainWindow : Window
    {
        private readonly AIService _aiService;
        private readonly CommandService _commandService;
        private readonly SpeechService _speechService;

        public MainWindow()
        {
            this.InitializeComponent();
            
            // Set window title
            this.Title = "JARVIS AI Assistant";
            
            // Set window size
            var appWindow = this.AppWindow;
            appWindow.Resize(new Windows.Graphics.SizeInt32(1000, 700));

            // Initialize Services
            _aiService = new AIService();
            _commandService = new CommandService();
            _speechService = new SpeechService();

            // Check Ollama status on startup
            _ = CheckOllamaStatusAsync();
        }

        private async System.Threading.Tasks.Task CheckOllamaStatusAsync()
        {
            var isRunning = await _aiService.IsOllamaRunningAsync();
            
            if (isRunning)
            {
                StatusTextBlock.Text = "✅ Ollama verbunden";
                
                // Get available models
                var models = await _aiService.GetAvailableModelsAsync();
                if (models.Length > 0)
                {
                    StatusTextBlock.Text += $" | Modelle: {string.Join(", ", models)}";
                }
            }
            else
            {
                StatusTextBlock.Text = "⚠️ Ollama nicht gefunden - Starte mit: ollama serve";
                ResponseTextBlock.Text = "💡 Um die AI-Funktionen zu nutzen:\n\n" +
                    "1. Installiere Ollama von https://ollama.ai\n" +
                    "2. Öffne ein Terminal und starte: ollama serve\n" +
                    "3. Lade ein Modell: ollama pull llama2\n" +
                    "4. Starte diese App neu";
            }
        }

        private async void SendButton_Click(object sender, RoutedEventArgs e)
        {
            string input = InputTextBox.Text.Trim();
            
            if (string.IsNullOrEmpty(input))
            {
                StatusTextBlock.Text = "❌ Bitte gib eine Nachricht ein";
                return;
            }

            // Disable controls during processing
            InputTextBox.IsEnabled = false;
            SendButton.IsEnabled = false;
            StatusTextBlock.Text = "⏳ Verarbeite...";
            ResponseTextBlock.Text = "";

            try
            {
                // Zuerst prüfen, ob es ein System-Command ist
                var commandResult = await _commandService.ProcessCommandAsync(input);
                
                if (commandResult.Success)
                {
                    // Command wurde ausgeführt
                    ResponseTextBlock.Text = commandResult.Message;
                    StatusTextBlock.Text = commandResult.IsWarning ? "⚠️ Warnung" : "✅ Command ausgeführt";
                    InputTextBox.Text = string.Empty;
                }
                else
                {
                    // Kein Command erkannt -> An AI weiterleiten
                    StatusTextBlock.Text = "⏳ Generiere Antwort...";
                    
                    // Use streaming for real-time response
                    await _aiService.GenerateStreamingResponseAsync(
                        input,
                        onChunkReceived: chunk =>
                        {
                            // Update UI on main thread
                            DispatcherQueue.TryEnqueue(() =>
                            {
                                ResponseTextBlock.Text += chunk;
                            });
                        }
                    );

                    StatusTextBlock.Text = "✅ Antwort generiert";
                    InputTextBox.Text = string.Empty;
                }
            }
            catch (Exception ex)
            {
                StatusTextBlock.Text = "❌ Fehler";
                ResponseTextBlock.Text = $"Fehler: {ex.Message}";
            }
            finally
            {
                // Re-enable controls
                InputTextBox.IsEnabled = true;
                SendButton.IsEnabled = true;
                InputTextBox.Focus(FocusState.Programmatic);
            }
        }

        private void InputTextBox_KeyDown(object sender, Microsoft.UI.Xaml.Input.KeyRoutedEventArgs e)
        {
            // Send message on Enter key (without Shift)
            if (e.Key == Windows.System.VirtualKey.Enter && 
                !Microsoft.UI.Input.InputKeyboardSource.GetKeyStateForCurrentThread(Windows.System.VirtualKey.Shift).HasFlag(Windows.UI.Core.CoreVirtualKeyStates.Down))
            {
                e.Handled = true;
                SendButton_Click(sender, new RoutedEventArgs());
            }
        }

        private void ClearButton_Click(object sender, RoutedEventArgs e)
        {
            ResponseTextBlock.Text = string.Empty;
            InputTextBox.Text = string.Empty;
            StatusTextBlock.Text = "🔄 Bereit";
            InputTextBox.Focus(FocusState.Programmatic);
        }

        private async void VoiceButton_Click(object sender, RoutedEventArgs e)
        {
            VoiceButton.IsEnabled = false;
            StatusTextBlock.Text = "🎤 Höre zu...";
            
            try
            {
                var recognizedText = await _speechService.ListenAsync();
                
                if (recognizedText.StartsWith("❌"))
                {
                    StatusTextBlock.Text = "❌ Spracherkennung fehlgeschlagen";
                    ResponseTextBlock.Text = recognizedText;
                }
                else
                {
                    // Text ins Eingabefeld einfügen, NICHT automatisch senden
                    InputTextBox.Text = recognizedText;
                    StatusTextBlock.Text = $"✅ Erkannt: {recognizedText}";
                    
                    // Fokus auf Textfeld setzen, damit Enter gedrückt werden kann
                    InputTextBox.Focus(FocusState.Programmatic);
                }
            }
            catch (Exception ex)
            {
                StatusTextBlock.Text = "❌ Fehler";
                ResponseTextBlock.Text = $"Fehler bei Spracheingabe: {ex.Message}";
            }
            finally
            {
                VoiceButton.IsEnabled = true;
            }
        }
    }
}

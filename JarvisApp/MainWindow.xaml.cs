using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;
using System.Threading.Tasks;
using JarvisApp.Services;

namespace JarvisApp
{
    public sealed partial class MainWindow : Window
    {
        private readonly AIService _aiService;
        private readonly CommandService _commandService;
        private readonly AutomationService _automationService;
        private readonly BrowserAutomationService _browserAutomationService;
        private readonly IntelligentCommandService _intelligentCommandService;
        private readonly WorkModeService _workModeService;

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
            _automationService = new AutomationService();
            _browserAutomationService = new BrowserAutomationService(_automationService);
            _commandService = new CommandService();
            _intelligentCommandService = new IntelligentCommandService(_aiService, _commandService, _automationService, _browserAutomationService);
            _workModeService = new WorkModeService(_automationService);

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

            // Prüfe auf Bestätigung/Abbruch bei ausstehender Aktion
            if (_intelligentCommandService.IsWaitingForConfirmation)
            {
                var lowerInput = input.ToLower();
                
                if (lowerInput.Contains("ja") || lowerInput.Contains("bestätig") || lowerInput.Contains("ok") || lowerInput.Contains("yes"))
                {
                    var confirmResult = _intelligentCommandService.ConfirmAction();
                    ResponseTextBlock.Text += "\n\n" + confirmResult;
                    StatusTextBlock.Text = "✅ Aktion bestätigt";
                    InputTextBox.Text = string.Empty;
                    return;
                }
                else if (lowerInput.Contains("nein") || lowerInput.Contains("abbruch") || lowerInput.Contains("cancel") || lowerInput.Contains("no"))
                {
                    var cancelResult = _intelligentCommandService.CancelAction();
                    ResponseTextBlock.Text += "\n\n" + cancelResult;
                    StatusTextBlock.Text = "🚫 Aktion abgebrochen";
                    InputTextBox.Text = string.Empty;
                    return;
                }
            }

            // Disable controls during processing
            InputTextBox.IsEnabled = false;
            SendButton.IsEnabled = false;
            StatusTextBlock.Text = "🤖 AI analysiert Anfrage...";
            ResponseTextBlock.Text = "";

            try
            {
                // Spezial-Modus: Work Mode
                if (input.ToLower().Contains("work mode") || input.ToLower().Contains("arbeitsmodus"))
                {
                    StatusTextBlock.Text = "🎵 Starte Work Mode...";
                    var workModeResult = await _workModeService.ExecuteWorkModeAsync();
                    ResponseTextBlock.Text = workModeResult;
                    StatusTextBlock.Text = "✅ Work Mode aktiviert";
                    InputTextBox.Text = string.Empty;
                    return;
                }

                // 1. AI analysiert die Anfrage und führt Aktionen aus
                var intelligentResult = await _intelligentCommandService.ProcessCommandAsync(input);
                
                // Zeige Ergebnis an
                ResponseTextBlock.Text = intelligentResult;
                StatusTextBlock.Text = "✅ Fertig";
                InputTextBox.Text = string.Empty;
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
    }
}

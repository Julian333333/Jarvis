using Microsoft.UI.Dispatching;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Input;
using System;
using System.Collections.ObjectModel;
using System.Linq;
using System.Threading.Tasks;
using JarvisApp.Services;
using JarvisApp.Services.Autonomy;

namespace JarvisApp
{
    public sealed partial class MainWindow : Window
    {
        private readonly AIService _aiService;
        private readonly CommandService _commandService;
        private readonly AutomationService _automationService;
        private readonly BrowserAutomationService _browserAutomationService;
        private readonly VisionService _visionService;
        private readonly SpeechService _speechService;
        private readonly IntelligentCommandService _intelligentCommandService;
        private readonly WorkModeService _workModeService;
        private readonly AutonomyService _autonomyService;
        private readonly DispatcherQueue _dispatcher;
        private readonly ObservableCollection<string> _autonomyGoalItems = new();
        private readonly ObservableCollection<string> _autonomyLogItems = new();
        private bool _isUpdatingAutonomyMode;

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
            _visionService = new VisionService(_browserAutomationService, _automationService);
            _speechService = new SpeechService();
            _commandService = new CommandService();
            _intelligentCommandService = new IntelligentCommandService(_aiService, _commandService, _automationService, _browserAutomationService, _visionService);
            _workModeService = new WorkModeService(_automationService);
            _autonomyService = new AutonomyService(_intelligentCommandService, _visionService);
            _dispatcher = DispatcherQueue.GetForCurrentThread();

            InitializeSpeechIntegration();
            InitializeAutonomyPanel();
            HookAutonomyEvents();
            this.Closed += MainWindow_Closed;

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

                // Check for Vision Model (LLaVA)
                var hasVision = await _visionService.IsVisionModelAvailableAsync();
                if (hasVision)
                {
                    StatusTextBlock.Text += " | 👁️ Vision AI aktiv";
                }
                else
                {
                    StatusTextBlock.Text += " | ⚠️ Vision: ollama pull llava";
                }
            }
            else
            {
                StatusTextBlock.Text = "⚠️ Ollama nicht gefunden - Starte mit: ollama serve";
                ResponseTextBlock.Text = "💡 Um die AI-Funktionen zu nutzen:\n\n" +
                    "1. Installiere Ollama von https://ollama.ai\n" +
                    "2. Öffne ein Terminal und starte: ollama serve\n" +
                    "3. Lade ein Modell: ollama pull llama2\n" +
                    "4. Für Vision AI: ollama pull llava\n" +
                    "5. Starte diese App neu";
            }
        }

        private async void SendButton_Click(object sender, RoutedEventArgs e)
        {
            await ProcessInputAsync(InputTextBox.Text.Trim(), fromVoice: false);
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

        private async Task ProcessInputAsync(string input, bool fromVoice)
        {
            if (string.IsNullOrWhiteSpace(input))
            {
                if (!fromVoice)
                {
                    StatusTextBlock.Text = "❌ Bitte gib eine Nachricht ein";
                }
                return;
            }

            if (TryHandlePendingConfirmation(input))
            {
                return;
            }

            if (TryHandleAutonomyCommand(input, fromVoice))
            {
                if (!fromVoice)
                {
                    InputTextBox.Text = string.Empty;
                }
                return;
            }

            if (!fromVoice)
            {
                InputTextBox.IsEnabled = false;
                SendButton.IsEnabled = false;
                StatusTextBlock.Text = "🤖 AI analysiert Anfrage...";
                ResponseTextBlock.Text = string.Empty;
            }
            else
            {
                StatusTextBlock.Text = $"🎙️ Sprachbefehl: {input}";
            }

            try
            {
                if (IsWorkModeCommand(input))
                {
                    StatusTextBlock.Text = "🎵 Starte Work Mode...";
                    var workModeResult = await _workModeService.ExecuteWorkModeAsync();
                    ResponseTextBlock.Text = workModeResult;
                    StatusTextBlock.Text = "✅ Work Mode aktiviert";
                    if (!fromVoice)
                    {
                        InputTextBox.Text = string.Empty;
                    }
                    SpeakIfNeeded(workModeResult);
                    return;
                }

                var intelligentResult = await _intelligentCommandService.ProcessCommandAsync(input);
                ResponseTextBlock.Text = intelligentResult;
                StatusTextBlock.Text = "✅ Fertig";
                if (!fromVoice)
                {
                    InputTextBox.Text = string.Empty;
                }
                SpeakIfNeeded(intelligentResult);
            }
            catch (Exception ex)
            {
                StatusTextBlock.Text = "❌ Fehler";
                ResponseTextBlock.Text = $"Fehler: {ex.Message}";
                SpeakIfNeeded("Es gab einen Fehler.");
            }
            finally
            {
                if (!fromVoice)
                {
                    InputTextBox.IsEnabled = true;
                    SendButton.IsEnabled = true;
                    InputTextBox.Focus(FocusState.Programmatic);
                }
            }
        }

        private bool TryHandlePendingConfirmation(string input)
        {
            if (!_intelligentCommandService.IsWaitingForConfirmation)
            {
                return false;
            }

            var lowerInput = input.ToLower();
            if (lowerInput.Contains("ja") || lowerInput.Contains("bestätig") || lowerInput.Contains("ok") || lowerInput.Contains("yes"))
            {
                var confirmResult = _intelligentCommandService.ConfirmAction();
                ResponseTextBlock.Text += "\n\n" + confirmResult;
                StatusTextBlock.Text = "✅ Aktion bestätigt";
                InputTextBox.Text = string.Empty;
                SpeakIfNeeded("Aktion bestätigt.");
                return true;
            }
            else if (lowerInput.Contains("nein") || lowerInput.Contains("abbruch") || lowerInput.Contains("cancel") || lowerInput.Contains("no"))
            {
                var cancelResult = _intelligentCommandService.CancelAction();
                ResponseTextBlock.Text += "\n\n" + cancelResult;
                StatusTextBlock.Text = "🚫 Aktion abgebrochen";
                InputTextBox.Text = string.Empty;
                SpeakIfNeeded("Aktion abgebrochen.");
                return true;
            }

            return false;
        }

        private bool IsWorkModeCommand(string input)
        {
            var lower = input.ToLower();
            return lower.Contains("work mode") || lower.Contains("arbeitsmodus");
        }

        private bool TryHandleAutonomyCommand(string input, bool fromVoice)
        {
            if (_autonomyService == null)
            {
                return false;
            }

            var lower = input.ToLowerInvariant();

            if (lower.Contains("autonomie") && (lower.Contains("stop") || lower.Contains("stopp") || lower.Contains("halt") || lower.Contains("aus")))
            {
                _autonomyService.EmergencyStop("User stop");
                SetAutonomyModeSelection(AutonomyMode.Off);
                UpdateAutonomyStateText(AutonomyMode.Off, null);
                ResponseTextBlock.Text = "🛑 Autonomie gestoppt.";
                StatusTextBlock.Text = "🛑 Autonomie deaktiviert";
                SpeakIfNeeded("Autonomie gestoppt.");
                return true;
            }

            if (lower.Contains("autonomie") && (lower.Contains("start") || lower.Contains("an") || lower.Contains("aktiv") || lower.Contains("übernimm") || lower.Contains("voll")))
            {
                _autonomyService.SetMode(AutonomyMode.Full);
                SetAutonomyModeSelection(AutonomyMode.Full);
                UpdateAutonomyStateText(_autonomyService.Mode, _autonomyService.GetActiveGoal());
                StatusTextBlock.Text = "🤖 Autonomie aktiv";
                ResponseTextBlock.Text = "🤖 Jarvis übernimmt.";
                SpeakIfNeeded("Ich übernehme.");
                return true;
            }

            if (_autonomyService.Mode == AutonomyMode.Full && fromVoice)
            {
                QueueAutonomyGoal(input);
                return true;
            }

            return false;
        }

        private void QueueAutonomyGoal(string description, AutonomyPriority priority = AutonomyPriority.Normal)
        {
            if (_autonomyService == null)
            {
                return;
            }

            var trimmed = description.Trim();
            if (string.IsNullOrWhiteSpace(trimmed))
            {
                StatusTextBlock.Text = "⚠️ Kein Ziel angegeben.";
                return;
            }

            var snapshot = _autonomyService.AddGoal(trimmed, priority);
            StatusTextBlock.Text = $"🎯 Ziel hinzugefügt: {snapshot.Description}";
            ResponseTextBlock.Text = $"🎯 Autonomie-Ziel aufgenommen:\n{snapshot.Description}";
            SpeakIfNeeded("Neues Ziel aufgenommen.");
        }

        private void UpdateAutonomyStateText(AutonomyMode mode, AutonomyGoalSnapshot? activeGoal)
        {
            if (AutonomyStateTextBlock == null)
            {
                return;
            }

            var prefix = mode switch
            {
                AutonomyMode.Full => "🤖 Voll autonom",
                AutonomyMode.Paused => "⏸️ Autonomie pausiert",
                _ => "Autonomie deaktiviert"
            };

            if (activeGoal != null)
            {
                AutonomyStateTextBlock.Text = $"{prefix} | Aktiv: {activeGoal.Description}";
            }
            else
            {
                AutonomyStateTextBlock.Text = prefix;
            }

            AutonomyPauseButton.Content = mode == AutonomyMode.Paused ? "Fortsetzen" : "Pause";
        }

        private void SetAutonomyModeSelection(AutonomyMode mode)
        {
            if (AutonomyModeCombo == null)
            {
                return;
            }

            _isUpdatingAutonomyMode = true;
            try
            {
                foreach (var item in AutonomyModeCombo.Items.OfType<ComboBoxItem>())
                {
                    if (item.Tag is string tag && Enum.TryParse(tag, true, out AutonomyMode parsed) && parsed == mode)
                    {
                        AutonomyModeCombo.SelectedItem = item;
                        break;
                    }
                }
            }
            finally
            {
                _isUpdatingAutonomyMode = false;
            }
        }

        private void SpeakIfNeeded(string text)
        {
            if (VoiceToggle?.IsOn == true)
            {
                _speechService.SpeakAsync(text);
            }
        }

        private void InitializeAutonomyPanel()
        {
            AutonomyGoalsList.ItemsSource = _autonomyGoalItems;
            AutonomyLogList.ItemsSource = _autonomyLogItems;
            UpdateAutonomyStateText(_autonomyService.Mode, null);
        }

        private void HookAutonomyEvents()
        {
            _autonomyService.LogEntryAdded += AutonomyService_LogEntryAdded;
            _autonomyService.GoalsUpdated += AutonomyService_GoalsUpdated;
            _autonomyService.CurrentGoalChanged += AutonomyService_CurrentGoalChanged;
            _autonomyService.ModeChanged += AutonomyService_ModeChanged;
        }

        private void AutonomyService_LogEntryAdded(object? sender, AutonomyLogEntry e)
        {
            _dispatcher.TryEnqueue(() =>
            {
                var entry = $"{e.Timestamp:HH:mm:ss} [{e.Level}] {e.Message}";
                _autonomyLogItems.Insert(0, entry);
                while (_autonomyLogItems.Count > 120)
                {
                    _autonomyLogItems.RemoveAt(_autonomyLogItems.Count - 1);
                }
            });
        }

        private void AutonomyService_GoalsUpdated(object? sender, AutonomyGoalSnapshot[] snapshots)
        {
            _dispatcher.TryEnqueue(() =>
            {
                _autonomyGoalItems.Clear();
                foreach (var snapshot in snapshots)
                {
                    var summary = $"[{snapshot.Status}] {snapshot.Description}";
                    _autonomyGoalItems.Add(summary);
                }
            });
        }

        private void AutonomyService_CurrentGoalChanged(object? sender, AutonomyGoalSnapshot? snapshot)
        {
            _dispatcher.TryEnqueue(() =>
            {
                UpdateAutonomyStateText(_autonomyService.Mode, snapshot);
            });
        }

        private void AutonomyService_ModeChanged(object? sender, AutonomyMode mode)
        {
            _dispatcher.TryEnqueue(() =>
            {
                SetAutonomyModeSelection(mode);
                UpdateAutonomyStateText(mode, _autonomyService.GetActiveGoal());
            });
        }

        private void AutonomyModeCombo_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_isUpdatingAutonomyMode || _autonomyService == null)
            {
                return;
            }

            if (AutonomyModeCombo.SelectedItem is ComboBoxItem item && item.Tag is string tag && Enum.TryParse(tag, true, out AutonomyMode mode))
            {
                _autonomyService.SetMode(mode);
                UpdateAutonomyStateText(mode, _autonomyService.GetActiveGoal());
            }
        }

        private void AutonomyAddGoalButton_Click(object sender, RoutedEventArgs e)
        {
            if (_autonomyService == null)
            {
                return;
            }
            QueueGoalFromInput();
        }

        private void AutonomyGoalTextBox_KeyDown(object sender, KeyRoutedEventArgs e)
        {
            if (_autonomyService == null)
            {
                return;
            }
            if (e.Key == Windows.System.VirtualKey.Enter)
            {
                e.Handled = true;
                QueueGoalFromInput();
            }
        }

        private void QueueGoalFromInput()
        {
            var goalText = AutonomyGoalTextBox.Text.Trim();
            if (string.IsNullOrWhiteSpace(goalText))
            {
                StatusTextBlock.Text = "⚠️ Kein Ziel angegeben.";
                return;
            }

            QueueAutonomyGoal(goalText);
            AutonomyGoalTextBox.Text = string.Empty;
        }

        private void AutonomyPauseButton_Click(object sender, RoutedEventArgs e)
        {
            if (_autonomyService == null)
            {
                return;
            }
            if (_autonomyService.Mode == AutonomyMode.Full)
            {
                _autonomyService.Pause();
            }
            else if (_autonomyService.Mode == AutonomyMode.Paused)
            {
                _autonomyService.Resume();
            }

            UpdateAutonomyStateText(_autonomyService.Mode, _autonomyService.GetActiveGoal());
        }

        private void AutonomyStopButton_Click(object sender, RoutedEventArgs e)
        {
            if (_autonomyService == null)
            {
                return;
            }
            _autonomyService.EmergencyStop("User stop");
            SetAutonomyModeSelection(AutonomyMode.Off);
            UpdateAutonomyStateText(AutonomyMode.Off, null);
            StatusTextBlock.Text = "🛑 Autonomie deaktiviert";
        }

        private void InitializeSpeechIntegration()
        {
            if (!_speechService.IsAvailable)
            {
                VoiceToggle.IsEnabled = false;
                VoiceStatusTextBlock.Text = "❌ Sprachmodul nicht verfügbar";
                return;
            }

            _speechService.HotwordDetected += SpeechService_HotwordDetected;
            _speechService.CommandRecognized += SpeechService_CommandRecognized;
            _speechService.ErrorOccurred += SpeechService_ErrorOccurred;
            _speechService.ListeningStateChanged += SpeechService_ListeningStateChanged;
        }

        private void SpeechService_HotwordDetected(object? sender, EventArgs e)
        {
            _dispatcher.TryEnqueue(() =>
            {
                VoiceStatusTextBlock.Text = "👂 Hotword erkannt - warte auf Befehl";
                StatusTextBlock.Text = "👂 Jarvis hört zu";
                _speechService.SpeakAsync("Ja?");
            });
        }

        private void SpeechService_CommandRecognized(object? sender, string command)
        {
            _dispatcher.TryEnqueue(() =>
            {
                VoiceStatusTextBlock.Text = "🎙️ Befehl erkannt";
                ResponseTextBlock.Text = $"🎙️ {command}";
                _ = ProcessInputAsync(command, fromVoice: true);
            });
        }

        private void SpeechService_ErrorOccurred(object? sender, string error)
        {
            _dispatcher.TryEnqueue(() =>
            {
                VoiceStatusTextBlock.Text = $"❌ {error}";
                StatusTextBlock.Text = "❌ Sprachfehler";
            });
        }

        private void SpeechService_ListeningStateChanged(object? sender, bool isListening)
        {
            _dispatcher.TryEnqueue(() =>
            {
                VoiceStatusTextBlock.Text = isListening ? "🎙️ Lausche auf 'Jarvis'" : "🎙️ Sprache deaktiviert";
            });
        }

        private void MainWindow_Closed(object sender, WindowEventArgs args)
        {
            _speechService.Dispose();
            _autonomyService.Dispose();
        }

        private void VoiceToggle_Toggled(object sender, RoutedEventArgs e)
        {
            if (!_speechService.IsAvailable)
            {
                VoiceToggle.IsOn = false;
                VoiceStatusTextBlock.Text = "❌ Sprachmodul nicht verfügbar";
                return;
            }

            if (VoiceToggle.IsOn)
            {
                var started = _speechService.StartListening();
                if (!started)
                {
                    VoiceToggle.IsOn = false;
                    VoiceStatusTextBlock.Text = "❌ Mikrofon konnte nicht gestartet werden";
                    return;
                }

                StatusTextBlock.Text = "🎙️ Sprachsteuerung aktiv";
                VoiceStatusTextBlock.Text = "🎙️ Lausche auf 'Jarvis'";
            }
            else
            {
                _speechService.StopListening();
                VoiceStatusTextBlock.Text = "🎙️ Sprache deaktiviert";
                StatusTextBlock.Text = "🔇 Sprachsteuerung aus";
            }
        }
    }
}

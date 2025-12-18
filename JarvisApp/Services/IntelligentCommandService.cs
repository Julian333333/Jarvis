using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace JarvisApp.Services
{
    public class IntelligentCommandService
    {
        private readonly AIService _aiService;
        private readonly AutomationService _automation;
        private readonly CommandService _commandService;
        private readonly BrowserAutomationService _browserAutomation;
        private readonly VisionService _visionService;

        public IntelligentCommandService(AIService aiService, CommandService commandService, AutomationService automation, BrowserAutomationService browserAutomation, VisionService visionService)
        {
            _aiService = aiService;
            _commandService = commandService;
            _automation = automation;
            _browserAutomation = browserAutomation;
            _visionService = visionService;
        }

        public bool IsWaitingForConfirmation => _browserAutomation.IsWaitingForConfirmation;

        public string ConfirmAction() => _browserAutomation.ConfirmPendingAction();

        public string CancelAction() => _browserAutomation.CancelPendingAction();

        public async Task<string> ProcessCommandAsync(string userInput)
        {
            System.Diagnostics.Debug.WriteLine($"📥 ProcessCommandAsync: '{userInput}'");
            
            // Direkte Vision-Erkennung (Bypass AI-Analyse)
            var lowerInput = userInput.ToLower();
            System.Diagnostics.Debug.WriteLine($"🔍 Lower Input: '{lowerInput}'");
            
            if (lowerInput.Contains("siehst du") || lowerInput.Contains("bildschirm") || 
                lowerInput.Contains("screen") || lowerInput.Contains("analysiere") ||
                lowerInput.Contains("was ist auf") || lowerInput.Contains("beschreibe") ||
                lowerInput.Contains("öffne") || lowerInput.Contains("klicke") ||
                lowerInput.Contains("suche") || lowerInput.Contains("finde"))
            {
                System.Diagnostics.Debug.WriteLine("✅ Vision/Agent Keyword erkannt!");
                
                // Agent-Modus für komplexe Aufgaben
                if (lowerInput.Contains("öffne") || lowerInput.Contains("klicke") || 
                    lowerInput.Contains("suche") || lowerInput.Contains("finde") ||
                    lowerInput.Contains("mache") || lowerInput.Contains("tue"))
                {
                    System.Diagnostics.Debug.WriteLine("🤖 Starte autonomen Agent-Modus...");
                    return await _visionService.RunAutonomousAgentAsync(userInput);
                }
                
                // Einfache Bildschirm-Analyse
                if (lowerInput.Contains("bildschirm") || lowerInput.Contains("screen") || 
                    lowerInput.Contains("siehst") || lowerInput.Contains("was ist auf") ||
                    lowerInput.Contains("beschreibe") || lowerInput.Contains("analysiere"))
                {
                    System.Diagnostics.Debug.WriteLine("👁️ Rufe VisionService auf...");
                    return await _visionService.AnalyzeScreenAsync(userInput);
                }
            }
            
            System.Diagnostics.Debug.WriteLine("➡️ Weiter zur normalen AI-Verarbeitung");

            var result = await ProcessIntelligentCommandAsync(userInput);
            
            if (result.IsAIResponse && result.Actions.Count == 0)
            {
                System.Diagnostics.Debug.WriteLine("💬 Generiere normale AI-Antwort");
                var aiResponse = await _aiService.GenerateResponseAsync(userInput);
                return aiResponse;
            }
            
            return result.Message;
        }

        public async Task<IntelligentCommandResult> ProcessIntelligentCommandAsync(string userInput)
        {
            var analysis = await AnalyzeIntentWithAI(userInput);

            if (analysis == null || !analysis.IsActionable)
            {
                return new IntelligentCommandResult
                {
                    Success = true,
                    IsAIResponse = true,
                    Message = "Verarbeite als normale AI-Anfrage..."
                };
            }

            var result = new IntelligentCommandResult
            {
                Success = true,
                Actions = new List<string>()
            };

            foreach (var action in analysis.Actions)
            {
                var actionResult = await ExecuteActionAsync(action, userInput);
                result.Actions.Add(actionResult);
                
                if (analysis.Actions.Count > 1)
                {
                    await Task.Delay(500);
                }
            }

            if (analysis.NeedsAIResponse)
            {
                result.IsAIResponse = true;
                result.Message = "Aktionen ausgeführt. Zusätzliche Informationen folgen...";
            }
            else
            {
                result.Message = string.Join("\n", result.Actions);
            }

            return result;
        }

        private async Task<CommandAnalysis?> AnalyzeIntentWithAI(string userInput)
        {
            var prompt = "Analysiere folgende Benutzeranfrage und identifiziere die gewuenschten Aktionen.\n\n" +
                $"BENUTZERANFRAGE: \"{userInput}\"\n\n" +
                "Antworte NUR mit einem JSON-Objekt:\n" +
                "{\n" +
                "  \"isActionable\": true/false,\n" +
                "  \"needsAIResponse\": true/false,\n" +
                "  \"actions\": [\n" +
                "    {\"type\": \"action_type\", \"target\": \"target_value\", \"parameters\": \"optional\"}\n" +
                "  ]\n" +
                "}\n\n" +
                "Action-Types:\n" +
                "- open_program, open_file, type_text, press_key, click_mouse\n" +
                "- window_action, volume, web_search, send_whatsapp, web_automation\n" +
                "- analyze_screen (Vision AI)\n";

            try
            {
                var response = await _aiService.GenerateResponseAsync(prompt);
                
                var jsonStart = response.IndexOf('{');
                var jsonEnd = response.LastIndexOf('}');
                
                if (jsonStart >= 0 && jsonEnd > jsonStart)
                {
                    var json = response.Substring(jsonStart, jsonEnd - jsonStart + 1);
                    var analysis = JsonSerializer.Deserialize<CommandAnalysis>(json, new JsonSerializerOptions
                    {
                        PropertyNameCaseInsensitive = true
                    });
                    return analysis;
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"AI-Analyse fehlgeschlagen: {ex.Message}");
            }

            return null;
        }

        private async Task<string> ExecuteActionAsync(CommandAction action, string originalInput)
        {
            try
            {
                switch (action.Type?.ToLower())
                {
                    case "open_program":
                        return await ExecuteOpenProgramAsync(action.Target);

                    case "open_file":
                        return await ExecuteOpenFileAsync(action.Target);

                    case "type_text":
                        await _automation.TypeTextAsync(action.Target ?? "", 30);
                        return $"Tastatur: Text eingegeben: {action.Target}";

                    case "press_key":
                        return ExecutePressKey(action.Target);

                    case "click_mouse":
                        return ExecuteMouseClick(action.Target);

                    case "window_action":
                        return ExecuteWindowAction(action.Target, action.Parameters);

                    case "volume":
                        return ExecuteVolumeAction(action.Target);

                    case "web_search":
                        return await ExecuteWebSearchAsync(action.Target);

                    case "send_whatsapp":
                        return await ExecuteWhatsAppMessageAsync(action.Target, action.Parameters);

                    case "web_automation":
                        return await ExecuteWebAutomationAsync(action.Target, action.Parameters);

                    case "analyze_screen":
                        var question = string.IsNullOrEmpty(action.Parameters) ? action.Target : action.Parameters;
                        return await _visionService.AnalyzeScreenAsync(question);

                    default:
                        return $"Unbekannte Aktion: {action.Type}";
                }
            }
            catch (Exception ex)
            {
                return $"Fehler bei {action.Type}: {ex.Message}";
            }
        }

        private async Task<string> ExecuteOpenProgramAsync(string? programName)
        {
            var program = programName?.ToLower() ?? "";
            
            var programMap = new Dictionary<string, string>
            {
                ["notepad"] = "notepad.exe",
                ["editor"] = "notepad.exe",
                ["browser"] = "microsoft-edge:",
                ["edge"] = "microsoft-edge:",
                ["chrome"] = "chrome.exe",
                ["firefox"] = "firefox.exe",
                ["calculator"] = "calc.exe",
                ["rechner"] = "calc.exe",
                ["explorer"] = "explorer.exe",
                ["paint"] = "mspaint.exe",
                ["cmd"] = "cmd.exe",
                ["terminal"] = "cmd.exe",
                ["powershell"] = "powershell.exe",
                ["word"] = "winword.exe",
                ["excel"] = "excel.exe",
                ["powerpoint"] = "powerpnt.exe",
                ["outlook"] = "outlook.exe",
                ["whatsapp"] = "whatsapp:"
            };

            if (programMap.TryGetValue(program, out var programPath))
            {
                _automation.StartProgram(programPath);
                await Task.Delay(1000);
                return $"Programm {programName} geoeffnet";
            }

            return $"Programm '{programName}' nicht gefunden";
        }

        private async Task<string> ExecuteOpenFileAsync(string? filePath)
        {
            if (string.IsNullOrEmpty(filePath))
                return "Kein Dateipfad angegeben";

            try
            {
                _automation.StartProgram(filePath);
                await Task.Delay(500);
                return $"Datei geoeffnet: {filePath}";
            }
            catch
            {
                return $"Datei nicht gefunden: {filePath}";
            }
        }

        private string ExecutePressKey(string? keyCombo)
        {
            var key = keyCombo?.ToLower() ?? "";

            switch (key)
            {
                case "enter":
                    _automation.PressKey(VirtualKeyCode.RETURN);
                    return "Enter gedrueckt";
                
                case "ctrl_c":
                case "strg_c":
                    _automation.PressKeyCombination(VirtualKeyCode.CONTROL, VirtualKeyCode.VK_C);
                    return "Strg+C (Kopieren)";
                
                case "ctrl_v":
                case "strg_v":
                    _automation.PressKeyCombination(VirtualKeyCode.CONTROL, VirtualKeyCode.VK_V);
                    return "Strg+V (Einfuegen)";
                
                case "ctrl_x":
                case "strg_x":
                    _automation.PressKeyCombination(VirtualKeyCode.CONTROL, VirtualKeyCode.VK_X);
                    return "Strg+X (Ausschneiden)";
                
                case "alt_tab":
                    _automation.PressKeyCombination(VirtualKeyCode.ALT, VirtualKeyCode.TAB);
                    return "Alt+Tab";
                
                case "alt_f4":
                    _automation.PressKeyCombination(VirtualKeyCode.ALT, VirtualKeyCode.F4);
                    return "Alt+F4";
                
                default:
                    return $"Tastenkombination '{keyCombo}' nicht erkannt";
            }
        }

        private string ExecuteMouseClick(string? clickType)
        {
            switch (clickType?.ToLower())
            {
                case "left":
                    _automation.LeftClick();
                    return "Linksklick";
                
                case "right":
                    _automation.RightClick();
                    return "Rechtsklick";
                
                case "double":
                    _automation.DoubleClick();
                    return "Doppelklick";
                
                default:
                    _automation.LeftClick();
                    return "Klick";
            }
        }

        private string ExecuteWindowAction(string? action, string? windowTitle)
        {
            if (string.IsNullOrEmpty(windowTitle))
                return "Kein Fenstertitel angegeben";

            switch (action?.ToLower())
            {
                case "maximize":
                    _automation.MaximizeWindow(windowTitle);
                    return $"Fenster '{windowTitle}' maximiert";
                
                case "minimize":
                    _automation.MinimizeWindow(windowTitle);
                    return $"Fenster '{windowTitle}' minimiert";
                
                case "close":
                    _automation.CloseWindow(windowTitle);
                    return $"Fenster '{windowTitle}' geschlossen";
                
                case "focus":
                    _automation.FocusWindow(windowTitle);
                    return $"Fenster '{windowTitle}' fokussiert";
                
                default:
                    return $"Fenster-Aktion '{action}' nicht erkannt";
            }
        }

        private string ExecuteVolumeAction(string? action)
        {
            return "Lautstaerke-Steuerung";
        }

        private async Task<string> ExecuteWebSearchAsync(string? searchTerm)
        {
            if (string.IsNullOrEmpty(searchTerm))
                return "Kein Suchbegriff angegeben";

            var searchUrl = $"https://www.google.com/search?q={Uri.EscapeDataString(searchTerm)}";
            _automation.StartProgram(searchUrl);
            await Task.Delay(500);
            return $"Google-Suche: {searchTerm}";
        }

        private async Task<string> ExecuteWhatsAppMessageAsync(string? contact, string? message)
        {
            if (string.IsNullOrEmpty(contact))
                return "Kein Kontakt angegeben";
            
            if (string.IsNullOrEmpty(message))
                return "Keine Nachricht angegeben";

            try
            {
                _automation.StartProgram("whatsapp:");
                await Task.Delay(4000);

                var (width, height) = _automation.GetScreenResolution();

                var searchX = width / 6;
                var searchY = height / 8;
                _automation.MoveMouse(searchX, searchY);
                await Task.Delay(300);
                _automation.LeftClick();
                await Task.Delay(500);

                await _automation.TypeTextAsync(contact, 100);
                await Task.Delay(1500);

                _automation.PressKey(VirtualKeyCode.RETURN);
                await Task.Delay(1500);

                var messageX = width / 2;
                var messageY = height * 9 / 10;
                _automation.MoveMouse(messageX, messageY);
                await Task.Delay(300);
                _automation.LeftClick();
                await Task.Delay(500);

                await _automation.TypeTextAsync(message, 100);
                await Task.Delay(500);

                _automation.PressKey(VirtualKeyCode.RETURN);
                await Task.Delay(500);

                return $"WhatsApp-Nachricht an {contact} gesendet: \"{message}\"";
            }
            catch (Exception ex)
            {
                return $"Fehler beim Senden der WhatsApp-Nachricht: {ex.Message}";
            }
        }

        private async Task<string> ExecuteWebAutomationAsync(string? url, string? taskDescription)
        {
            if (string.IsNullOrEmpty(url))
                return "Keine URL angegeben";

            var task = ParseWebTask(url, taskDescription ?? "");
            
            var result = await _browserAutomation.ExecuteWebTaskAsync(url, task);
            
            if (result.NeedsConfirmation)
            {
                return result.ConfirmationMessage;
            }
            
            return string.Join("\n", result.Steps);
        }

        private WebTask ParseWebTask(string url, string description)
        {
            var task = new WebTask
            {
                Url = url,
                Steps = new List<WebStep>()
            };

            var lowerDesc = description.ToLower();

            if (lowerDesc.Contains("kauf") || lowerDesc.Contains("buy"))
            {
                var amountMatch = System.Text.RegularExpressions.Regex.Match(description, @"(\d+)\s*€?");
                var assetMatch = System.Text.RegularExpressions.Regex.Match(description, @"(btc|eth|bitcoin|ethereum)", System.Text.RegularExpressions.RegexOptions.IgnoreCase);

                var amount = amountMatch.Success ? amountMatch.Groups[1].Value : "5";
                var asset = assetMatch.Success ? assetMatch.Value.ToUpper() : "BTC";

                task.Steps.AddRange(new[]
                {
                    new WebStep
                    {
                        Type = WebStepType.Wait,
                        Description = "Warte auf vollstaendiges Laden der Seite",
                        DelayAfterMs = 2000
                    },
                    new WebStep
                    {
                        Type = WebStepType.Click,
                        Target = "EUR Input Field",
                        SearchText = "eur",
                        Description = "Klicke in das EUR-Eingabefeld",
                        DelayAfterMs = 500
                    },
                    new WebStep
                    {
                        Type = WebStepType.Type,
                        Target = amount,
                        Description = $"Gib {amount} EUR ein",
                        DelayAfterMs = 1000
                    },
                    new WebStep
                    {
                        Type = WebStepType.Click,
                        Target = "Review Order Button",
                        SearchText = "review",
                        Description = "Klicke auf 'Review order' Button",
                        DelayAfterMs = 3000
                    },
                    new WebStep
                    {
                        Type = WebStepType.Click,
                        Target = "Buy Now Button",
                        SearchText = "buy",
                        Description = "Klicke auf 'Buy now' Button - Kauf wird ausgefuehrt!",
                        RequiresConfirmation = true,
                        DelayAfterMs = 0
                    }
                });
            }

            return task;
        }
    }

    #region DTOs

    public class CommandAnalysis
    {
        [JsonPropertyName("isActionable")]
        public bool IsActionable { get; set; }

        [JsonPropertyName("needsAIResponse")]
        public bool NeedsAIResponse { get; set; }

        [JsonPropertyName("actions")]
        public List<CommandAction> Actions { get; set; } = new();
    }

    public class CommandAction
    {
        [JsonPropertyName("type")]
        public string? Type { get; set; }

        [JsonPropertyName("target")]
        public string? Target { get; set; }

        [JsonPropertyName("parameters")]
        public string? Parameters { get; set; }
    }

    public class IntelligentCommandResult
    {
        public bool Success { get; set; }
        public bool IsAIResponse { get; set; }
        public string Message { get; set; } = string.Empty;
        public List<string> Actions { get; set; } = new();
    }

    #endregion
}

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace JarvisApp.Services
{
    /// <summary>
    /// Intelligenter Command-Interpreter der AI nutzt, um Befehle zu verstehen und auszuführen
    /// </summary>
    public class IntelligentCommandService
    {
        private readonly AIService _aiService;
        private readonly AutomationService _automation;
        private readonly CommandService _commandService;

        public IntelligentCommandService(AIService aiService, CommandService commandService, AutomationService automation)
        {
            _aiService = aiService;
            _commandService = commandService;
            _automation = automation;
        }

        /// <summary>
        /// Analysiert Benutzer-Input mit AI und führt entsprechende Aktionen aus
        /// </summary>
        public async Task<IntelligentCommandResult> ProcessIntelligentCommandAsync(string userInput)
        {
            // 1. AI-Analyse: Was will der Benutzer?
            var analysis = await AnalyzeIntentWithAI(userInput);

            if (analysis == null || !analysis.IsActionable)
            {
                // Keine Aktion erkannt -> Normale AI-Antwort
                return new IntelligentCommandResult
                {
                    Success = true,
                    IsAIResponse = true,
                    Message = "Verarbeite als normale AI-Anfrage..."
                };
            }

            // 2. Führe erkannte Aktionen aus
            var result = new IntelligentCommandResult
            {
                Success = true,
                Actions = new List<string>()
            };

            foreach (var action in analysis.Actions)
            {
                var actionResult = await ExecuteActionAsync(action, userInput);
                result.Actions.Add(actionResult);
                
                // Warte zwischen Aktionen
                if (analysis.Actions.Count > 1)
                {
                    await Task.Delay(500);
                }
            }

            // 3. Wenn zusätzliche Info gewünscht, hole AI-Antwort
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

        /// <summary>
        /// Analysiert User-Input mit AI um Intent zu erkennen
        /// </summary>
        private async Task<CommandAnalysis?> AnalyzeIntentWithAI(string userInput)
        {
            var prompt = $@"Analysiere folgende Benutzeranfrage und identifiziere die gewünschten Aktionen.

BENUTZERANFRAGE: ""{userInput}""

Antworte NUR mit einem JSON-Objekt in diesem Format (keine zusätzlichen Texte):
{{
  ""isActionable"": true/false,
  ""needsAIResponse"": true/false,
  ""actions"": [
    {{
      ""type"": ""open_program"",
      ""target"": ""programname"",
      ""parameters"": ""optionale parameter""
    }}
  ]
}}

Verfügbare Action-Types:
- ""open_program"": Programm öffnen (target: notepad, browser, powerpoint, word, excel, etc.)
- ""open_file"": Datei öffnen (target: dateipfad)
- ""type_text"": Text eingeben (target: der text)
- ""press_key"": Tastenkombination (target: ctrl_c, ctrl_v, alt_tab, enter, etc.)
- ""click_mouse"": Mausklick (target: left, right, double)
- ""window_action"": Fenster-Aktion (target: maximize, minimize, close, focus mit parameters: fenstertitel)
- ""volume"": Lautstärke (target: up, down, mute)
- ""web_search"": Web-Suche (target: suchbegriff)

BEISPIELE:

1. ""Öffne PowerPoint"" →
{{
  ""isActionable"": true,
  ""needsAIResponse"": false,
  ""actions"": [
    {{""type"": ""open_program"", ""target"": ""powerpoint""}}
  ]
}}

2. ""Öffne die Präsentation Marketing.pptx"" →
{{
  ""isActionable"": true,
  ""needsAIResponse"": false,
  ""actions"": [
    {{""type"": ""open_file"", ""target"": ""Marketing.pptx""}}
  ]
}}

3. ""Schreibe eine Email an Max und sage ihm Hallo"" →
{{
  ""isActionable"": true,
  ""needsAIResponse"": false,
  ""actions"": [
    {{""type"": ""open_program"", ""target"": ""browser""}},
    {{""type"": ""type_text"", ""target"": ""Hallo Max""}}
  ]
}}

4. ""Was ist Künstliche Intelligenz?"" →
{{
  ""isActionable"": false,
  ""needsAIResponse"": true,
  ""actions"": []
}}

5. ""Öffne Chrome und suche nach Quantenphysik"" →
{{
  ""isActionable"": true,
  ""needsAIResponse"": false,
  ""actions"": [
    {{""type"": ""open_program"", ""target"": ""browser""}},
    {{""type"": ""web_search"", ""target"": ""Quantenphysik""}}
  ]
}}

Analysiere jetzt die Anfrage und antworte NUR mit dem JSON-Objekt:";

            try
            {
                var response = await _aiService.GenerateResponseAsync(prompt);
                
                // Extrahiere JSON aus Antwort
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

        /// <summary>
        /// Führt eine einzelne Aktion aus
        /// </summary>
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
                        return $"⌨️ Text eingegeben: {action.Target}";

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

                    default:
                        return $"⚠️ Unbekannte Aktion: {action.Type}";
                }
            }
            catch (Exception ex)
            {
                return $"❌ Fehler bei {action.Type}: {ex.Message}";
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
                ["outlook"] = "outlook.exe"
            };

            if (programMap.TryGetValue(program, out var programPath))
            {
                _automation.StartProgram(programPath);
                await Task.Delay(1000); // Warte bis Programm geladen ist
                return $"💻 {programName} geöffnet";
            }

            return $"❌ Programm '{programName}' nicht gefunden";
        }

        private async Task<string> ExecuteOpenFileAsync(string? filePath)
        {
            if (string.IsNullOrEmpty(filePath))
                return "❌ Kein Dateipfad angegeben";

            try
            {
                _automation.StartProgram(filePath);
                await Task.Delay(500);
                return $"📄 Datei geöffnet: {filePath}";
            }
            catch
            {
                return $"❌ Datei nicht gefunden: {filePath}";
            }
        }

        private string ExecutePressKey(string? keyCombo)
        {
            var key = keyCombo?.ToLower() ?? "";

            switch (key)
            {
                case "enter":
                    _automation.PressKey(VirtualKeyCode.RETURN);
                    return "⌨️ Enter gedrückt";
                
                case "ctrl_c":
                case "strg_c":
                    _automation.PressKeyCombination(VirtualKeyCode.CONTROL, VirtualKeyCode.VK_C);
                    return "⌨️ Strg+C (Kopieren)";
                
                case "ctrl_v":
                case "strg_v":
                    _automation.PressKeyCombination(VirtualKeyCode.CONTROL, VirtualKeyCode.VK_V);
                    return "⌨️ Strg+V (Einfügen)";
                
                case "ctrl_x":
                case "strg_x":
                    _automation.PressKeyCombination(VirtualKeyCode.CONTROL, VirtualKeyCode.VK_X);
                    return "⌨️ Strg+X (Ausschneiden)";
                
                case "alt_tab":
                    _automation.PressKeyCombination(VirtualKeyCode.ALT, VirtualKeyCode.TAB);
                    return "⌨️ Alt+Tab";
                
                case "alt_f4":
                    _automation.PressKeyCombination(VirtualKeyCode.ALT, VirtualKeyCode.F4);
                    return "⌨️ Alt+F4";
                
                default:
                    return $"❌ Tastenkombination '{keyCombo}' nicht erkannt";
            }
        }

        private string ExecuteMouseClick(string? clickType)
        {
            switch (clickType?.ToLower())
            {
                case "left":
                    _automation.LeftClick();
                    return "🖱️ Linksklick";
                
                case "right":
                    _automation.RightClick();
                    return "🖱️ Rechtsklick";
                
                case "double":
                    _automation.DoubleClick();
                    return "🖱️ Doppelklick";
                
                default:
                    _automation.LeftClick();
                    return "🖱️ Klick";
            }
        }

        private string ExecuteWindowAction(string? action, string? windowTitle)
        {
            if (string.IsNullOrEmpty(windowTitle))
                return "❌ Kein Fenstertitel angegeben";

            switch (action?.ToLower())
            {
                case "maximize":
                    _automation.MaximizeWindow(windowTitle);
                    return $"🪟 Fenster '{windowTitle}' maximiert";
                
                case "minimize":
                    _automation.MinimizeWindow(windowTitle);
                    return $"🪟 Fenster '{windowTitle}' minimiert";
                
                case "close":
                    _automation.CloseWindow(windowTitle);
                    return $"🪟 Fenster '{windowTitle}' geschlossen";
                
                case "focus":
                    _automation.FocusWindow(windowTitle);
                    return $"🪟 Fenster '{windowTitle}' fokussiert";
                
                default:
                    return $"❌ Fenster-Aktion '{action}' nicht erkannt";
            }
        }

        private string ExecuteVolumeAction(string? action)
        {
            // Nutze den alten CommandService für Lautstärke
            return "🔊 Lautstärke-Steuerung";
        }

        private async Task<string> ExecuteWebSearchAsync(string? searchTerm)
        {
            if (string.IsNullOrEmpty(searchTerm))
                return "❌ Kein Suchbegriff angegeben";

            var searchUrl = $"https://www.google.com/search?q={Uri.EscapeDataString(searchTerm)}";
            _automation.StartProgram(searchUrl);
            await Task.Delay(500);
            return $"🔍 Google-Suche: {searchTerm}";
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

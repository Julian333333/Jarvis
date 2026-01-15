using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace JarvisApp.Services
{
    /// <summary>
    /// Vision AI Service - Analysiert Screenshots mit Ollama LLaVA
    /// </summary>
    public class VisionService
    {
        private readonly HttpClient _httpClient;
        private readonly BrowserAutomationService _browserAutomation;
        private readonly AutomationService _automation;
        private const string OllamaApiUrl = "http://localhost:11434/api/generate";
        private const string VisionModel = "llava"; // Ollama LLaVA Model

        public VisionService(BrowserAutomationService browserAutomation, AutomationService automation)
        {
            _httpClient = new HttpClient { Timeout = TimeSpan.FromMinutes(2) };
            _browserAutomation = browserAutomation;
            _automation = automation;
        }

        /// <summary>
        /// Analysiert den aktuellen Bildschirm und gibt Beschreibung zurück
        /// </summary>
        public async Task<string> AnalyzeScreenAsync(string? question = null)
        {
            try
            {
                System.Diagnostics.Debug.WriteLine("🔍 Vision AI: Starte Bildschirm-Analyse...");

                // 1. Screenshot machen
                var screenshot = _browserAutomation.CaptureScreen();
                if (screenshot == null)
                {
                    return "❌ Konnte keinen Screenshot erstellen";
                }

                System.Diagnostics.Debug.WriteLine($"📸 Screenshot erstellt: {screenshot.Width}x{screenshot.Height}");

                // 2. Screenshot zu Base64 konvertieren
                var base64Image = ConvertImageToBase64(screenshot);
                screenshot.Dispose();

                System.Diagnostics.Debug.WriteLine($"🔄 Base64 Länge: {base64Image.Length} Zeichen");

                // 3. Vision AI fragen
                var prompt = question ?? "Beschreibe detailliert was du auf diesem Bildschirm siehst. Welche Programme sind offen? Was ist der Hauptinhalt?";
                
                System.Diagnostics.Debug.WriteLine($"💬 Sende Anfrage an LLaVA: {prompt}");
                
                var response = await SendVisionRequestAsync(prompt, base64Image);

                System.Diagnostics.Debug.WriteLine($"✅ LLaVA Antwort erhalten: {response.Substring(0, Math.Min(100, response.Length))}...");

                return $"👁️ Vision AI Analyse:\n\n{response}";
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"❌ Vision AI Fehler: {ex.Message}\n{ex.StackTrace}");
                return $"❌ Fehler bei der Bildschirm-Analyse: {ex.Message}\n\nStelle sicher dass:\n1. Ollama läuft (ollama serve)\n2. LLaVA installiert ist (ollama pull llava)\n3. Keine Firewall blockiert";
            }
        }

        /// <summary>
        /// Autonomer Agent-Modus: Analysiert Bildschirm und führt Aktionen aus
        /// </summary>
        public async Task<string> RunAutonomousAgentAsync(string goal, int maxSteps = 5)
        {
            try
            {
                System.Diagnostics.Debug.WriteLine($"🤖 Starte autonomen Agent-Modus: {goal}");

                for (int step = 1; step <= maxSteps; step++)
                {
                    System.Diagnostics.Debug.WriteLine($"📍 Schritt {step}/{maxSteps}");

                    // 1. Screenshot machen
                    var screenshot = _browserAutomation.CaptureScreen();
                    if (screenshot == null)
                    {
                        return $"❌ Schritt {step}: Konnte keinen Screenshot erstellen";
                    }

                    var base64Image = ConvertImageToBase64(screenshot);
                    screenshot.Dispose();

                    // 2. Vision AI fragen was zu tun ist
                    var prompt = $@"Du bist ein autonomer Computer-Agent. Dein Ziel ist: {goal}

Analysiere diesen Bildschirm und entscheide, welche Aktion als nächstes ausgeführt werden soll.

Antworte NUR mit einem JSON-Objekt:
{{
  ""action"": ""click"" | ""type"" | ""scroll"" | ""wait"" | ""done"",
  ""target"": ""Beschreibung wo geklickt/getippt werden soll"",
  ""text"": ""Text zum eingeben (nur bei type)"",
  ""x"": 0-100,
  ""y"": 0-100,
  ""reason"": ""Warum diese Aktion?"",
  ""goalAchieved"": true/false
}}

Wenn das Ziel erreicht ist, setze goalAchieved: true und action: ""done"".
Koordinaten sind in Prozent (0-100) von links-oben.";

                    var response = await SendVisionRequestAsync(prompt, base64Image);
                    
                    // 3. JSON parsen
                    try
                    {
                        var json = ExtractJsonObject(response);
                        var action = JsonSerializer.Deserialize<AutonomousAction>(json ?? response);
                        if (action == null)
                        {
                            return $"❌ Schritt {step}: Konnte Aktion nicht parsen";
                        }

                        System.Diagnostics.Debug.WriteLine($"🎯 Aktion: {action.Action}, Ziel: {action.TargetText}");

                        // 4. Prüfen ob fertig
                        if (action.GoalAchieved || action.Action?.ToLower() == "done")
                        {
                            return $"✅ Ziel erreicht nach {step} Schritten!\n\n{action.Reason}";
                        }

                        // 5. Aktion ausführen
                        var result = await ExecuteAutonomousActionAsync(action);
                        
                        System.Diagnostics.Debug.WriteLine($"✅ Aktion ausgeführt: {result}");

                        // 6. Kurze Pause zwischen Aktionen
                        await Task.Delay(2000);
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"❌ JSON Parse Fehler: {ex.Message}");
                        return $"❌ Schritt {step}: Fehler beim Parsen der Vision-Antwort: {ex.Message}";
                    }
                }

                return $"⏰ Maximale Schritte ({maxSteps}) erreicht. Ziel möglicherweise nicht erreicht.";
            }
            catch (Exception ex)
            {
                return $"❌ Fehler im autonomen Modus: {ex.Message}";
            }
        }

        /// <summary>
        /// Führt eine autonome Aktion aus
        /// </summary>
        private async Task<string> ExecuteAutonomousActionAsync(AutonomousAction action)
        {
            try
            {
                var (width, height) = _automation.GetScreenResolution();

                switch (action.Action?.ToLower())
                {
                    case "click":
                        if (action.X.HasValue && action.Y.HasValue)
                        {
                            var x = (int)(width * action.X.Value / 100.0);
                            var y = (int)(height * action.Y.Value / 100.0);
                            _automation.MoveMouse(x, y);
                            await Task.Delay(300);
                            _automation.LeftClick();
                            return $"🖱️ Klick bei ({action.X}%, {action.Y}%) - {action.TargetText}";
                        }
                        return "❌ Ungültige Koordinaten für Klick";

                    case "type":
                        if (!string.IsNullOrEmpty(action.Text))
                        {
                            await _automation.TypeTextAsync(action.Text, 50);
                            return $"⌨️ Text eingegeben: '{action.Text}'";
                        }
                        return "❌ Kein Text zum Eingeben";

                    case "scroll":
                        // Scroll down
                        _automation.PressKeyCombination(VirtualKeyCode.CONTROL, VirtualKeyCode.VK_Z); // Ctrl+End für Scroll
                        return "📜 Gescrollt";

                    case "wait":
                        await Task.Delay(3000);
                        return "⏳ Gewartet";

                    default:
                        return $"❌ Unbekannte Aktion: {action.Action}";
                }
            }
            catch (Exception ex)
            {
                return $"❌ Fehler bei Aktion {action.Action}: {ex.Message}";
            }
        }
        public async Task<VisionAnalysisResult> AnalyzeScreenForActionAsync(string goal)
        {
            try
            {
                var screenshot = _browserAutomation.CaptureScreen();
                if (screenshot == null)
                {
                    return new VisionAnalysisResult { Success = false, Message = "Screenshot fehlgeschlagen" };
                }

                var base64Image = ConvertImageToBase64(screenshot);
                screenshot.Dispose();

                var prompt = $@"Analysiere diesen Bildschirm und schlage Aktionen vor um folgendes Ziel zu erreichen: {goal}

Antworte im JSON-Format:
{{
  ""description"": ""Was ist auf dem Bildschirm zu sehen"",
  ""nextAction"": ""click"" oder ""type"" oder ""scroll"" oder ""wait"" oder ""done"",
  ""target"": ""Beschreibung wo geklickt/getippt werden soll"",
  ""value"": ""Text zum eingeben (nur bei type)"",
  ""coordinates"": {{""x"": 0-100, ""y"": 0-100}},
  ""explanation"": ""Warum diese Aktion?""
}}

Koordinaten sind in Prozent (0-100) von links-oben.";

                var response = await SendVisionRequestAsync(prompt, base64Image);
                
                // Parse JSON
                try
                {
                    var json = ExtractJsonObject(response);
                    var result = JsonSerializer.Deserialize<VisionAnalysisResult>(json ?? response);
                    if (result != null)
                    {
                        result.Success = true;
                        return result;
                    }
                }
                catch
                {
                    // Fallback: Text-Antwort
                    return new VisionAnalysisResult
                    {
                        Success = true,
                        Description = response,
                        NextAction = "wait"
                    };
                }

                return new VisionAnalysisResult { Success = false, Message = "Konnte Antwort nicht parsen" };
            }
            catch (Exception ex)
            {
                return new VisionAnalysisResult { Success = false, Message = ex.Message };
            }
        }

        /// <summary>
        /// Sendet Vision-Request an Ollama LLaVA
        /// </summary>
        private async Task<string> SendVisionRequestAsync(string prompt, string base64Image)
        {
            try
            {
                var requestBody = new
                {
                    model = VisionModel,
                    prompt = prompt,
                    images = new[] { base64Image },
                    stream = false
                };

                var json = JsonSerializer.Serialize(requestBody);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                System.Diagnostics.Debug.WriteLine($"🌐 POST Request an {OllamaApiUrl}");

                var response = await _httpClient.PostAsync(OllamaApiUrl, content);
                
                System.Diagnostics.Debug.WriteLine($"📡 HTTP Status: {response.StatusCode}");

                response.EnsureSuccessStatusCode();

                var responseText = await response.Content.ReadAsStringAsync();
                
                System.Diagnostics.Debug.WriteLine($"📥 Response Länge: {responseText.Length} Zeichen");

                var result = JsonSerializer.Deserialize<OllamaResponse>(responseText);

                if (result?.Response == null || string.IsNullOrEmpty(result.Response))
                {
                    System.Diagnostics.Debug.WriteLine("⚠️ Leere Antwort von Ollama");
                    return "❌ LLaVA hat keine Antwort zurückgegeben";
                }

                return result.Response;
            }
            catch (HttpRequestException ex)
            {
                System.Diagnostics.Debug.WriteLine($"🌐 HTTP Fehler: {ex.Message}");
                return $"❌ Verbindungsfehler zu Ollama: {ex.Message}\n\nPrüfe: ollama serve läuft?";
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"❌ Unbekannter Fehler: {ex.Message}");
                return $"❌ Fehler: {ex.Message}";
            }
        }

        /// <summary>
        /// Konvertiert Bitmap zu Base64 String
        /// </summary>
        private string ConvertImageToBase64(Bitmap image)
        {
            using var ms = new MemoryStream();
            image.Save(ms, ImageFormat.Png);
            var imageBytes = ms.ToArray();
            return Convert.ToBase64String(imageBytes);
        }

        private string? ExtractJsonObject(string response)
        {
            if (string.IsNullOrWhiteSpace(response))
            {
                return null;
            }

            var cleaned = response.Trim();
            if (cleaned.StartsWith("```"))
            {
                var firstNewline = cleaned.IndexOf('\n');
                if (firstNewline >= 0)
                {
                    cleaned = cleaned.Substring(firstNewline + 1);
                }
                cleaned = cleaned.Replace("```", "").Trim();
            }

            var start = cleaned.IndexOf('{');
            var end = cleaned.LastIndexOf('}');
            if (start >= 0 && end > start)
            {
                return cleaned.Substring(start, end - start + 1);
            }

            return null;
        }

        /// <summary>
        /// Prüft ob LLaVA Model verfügbar ist
        /// </summary>
        public async Task<bool> IsVisionModelAvailableAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("http://localhost:11434/api/tags");
                if (!response.IsSuccessStatusCode) return false;

                var content = await response.Content.ReadAsStringAsync();
                return content.Contains("llava");
            }
            catch
            {
                return false;
            }
        }
    }

    #region DTOs

    public class VisionAnalysisResult
    {
        public bool Success { get; set; }
        public string? Message { get; set; }
        public string? Description { get; set; }
        public string? NextAction { get; set; }
        public string? Target { get; set; }
        public string? Value { get; set; }
        public VisionCoordinates? Coordinates { get; set; }
        public string? Explanation { get; set; }
    }

    public class VisionCoordinates
    {
        public int X { get; set; }
        public int Y { get; set; }
    }

    public class AutonomousAction
    {
        [JsonPropertyName("action")]
        public string? Action { get; set; }
        
        [JsonPropertyName("target")]
        public JsonElement? Target { get; set; }
        
        [JsonPropertyName("text")]
        public string? Text { get; set; }
        
        [JsonPropertyName("x")]
        public int? X { get; set; }
        
        [JsonPropertyName("y")]
        public int? Y { get; set; }
        
        [JsonPropertyName("reason")]
        public string? Reason { get; set; }
        
        [JsonPropertyName("goalAchieved")]
        public bool GoalAchieved { get; set; }

        [JsonIgnore]
        public string TargetText => NormalizeJsonElement(Target);

        private static string NormalizeJsonElement(JsonElement? element)
        {
            if (element == null)
            {
                return string.Empty;
            }

            switch (element.Value.ValueKind)
            {
                case JsonValueKind.String:
                    return element.Value.GetString() ?? string.Empty;
                case JsonValueKind.Number:
                case JsonValueKind.True:
                case JsonValueKind.False:
                    return element.Value.ToString();
                case JsonValueKind.Object:
                case JsonValueKind.Array:
                    return element.Value.ToString();
                default:
                    return string.Empty;
            }
        }
    }

    public class OllamaResponse
    {
        [JsonPropertyName("response")]
        public string? Response { get; set; }
        
        [JsonPropertyName("done")]
        public bool? Done { get; set; }
        
        [JsonPropertyName("done_reason")]
        public string? DoneReason { get; set; }
    }

    #endregion
}

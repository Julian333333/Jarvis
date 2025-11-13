using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

namespace JarvisApp.Services
{
    public class AIService
    {
        private readonly HttpClient _httpClient;
        private const string OllamaBaseUrl = "http://localhost:11434";
        private const string DefaultModel = "llama3.2:3b";

        public AIService()
        {
            _httpClient = new HttpClient
            {
                BaseAddress = new Uri(OllamaBaseUrl),
                Timeout = TimeSpan.FromMinutes(5)
            };
        }

        /// <summary>
        /// Prüft ob Ollama Server läuft
        /// </summary>
        public async Task<bool> IsOllamaRunningAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/api/tags");
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Holt eine Liste der verfügbaren Modelle
        /// </summary>
        public async Task<string[]> GetAvailableModelsAsync()
        {
            try
            {
                var response = await _httpClient.GetFromJsonAsync<ModelsResponse>("/api/tags");
                if (response?.Models != null)
                {
                    return Array.ConvertAll(response.Models, m => m.Name);
                }
            }
            catch { }
            
            return Array.Empty<string>();
        }

        /// <summary>
        /// Generiert eine AI-Antwort (vollständig, nicht gestreamt)
        /// </summary>
        public async Task<string> GenerateResponseAsync(string prompt, string model = DefaultModel)
        {
            try
            {
                var request = new GenerateRequest
                {
                    Model = model,
                    Prompt = prompt,
                    Stream = false
                };

                var response = await _httpClient.PostAsJsonAsync("/api/generate", request);
                response.EnsureSuccessStatusCode();

                var result = await response.Content.ReadFromJsonAsync<GenerateResponse>();
                return result?.Response ?? "Keine Antwort erhalten.";
            }
            catch (HttpRequestException ex)
            {
                return $"❌ Verbindungsfehler: {ex.Message}\n\n💡 Stelle sicher, dass Ollama läuft:\n   ollama serve";
            }
            catch (Exception ex)
            {
                return $"❌ Fehler: {ex.Message}";
            }
        }

        /// <summary>
        /// Generiert eine AI-Antwort mit Streaming (für Echtzeit-Ausgabe)
        /// </summary>
        public async Task<string> GenerateStreamingResponseAsync(
            string prompt, 
            string model = DefaultModel,
            Action<string>? onChunkReceived = null)
        {
            try
            {
                var request = new GenerateRequest
                {
                    Model = model,
                    Prompt = prompt,
                    Stream = true
                };

                var response = await _httpClient.PostAsJsonAsync("/api/generate", request);
                response.EnsureSuccessStatusCode();

                var fullResponse = "";
                using var stream = await response.Content.ReadAsStreamAsync();
                using var reader = new System.IO.StreamReader(stream);

                while (!reader.EndOfStream)
                {
                    var line = await reader.ReadLineAsync();
                    if (string.IsNullOrWhiteSpace(line)) continue;

                    try
                    {
                        var chunk = JsonSerializer.Deserialize<GenerateResponse>(line);
                        if (chunk?.Response != null)
                        {
                            fullResponse += chunk.Response;
                            onChunkReceived?.Invoke(chunk.Response);
                        }

                        if (chunk?.Done == true) break;
                    }
                    catch { }
                }

                return fullResponse;
            }
            catch (HttpRequestException ex)
            {
                var errorMsg = $"❌ Verbindungsfehler: {ex.Message}\n\n💡 Stelle sicher, dass Ollama läuft:\n   ollama serve";
                onChunkReceived?.Invoke(errorMsg);
                return errorMsg;
            }
            catch (Exception ex)
            {
                var errorMsg = $"❌ Fehler: {ex.Message}";
                onChunkReceived?.Invoke(errorMsg);
                return errorMsg;
            }
        }

        /// <summary>
        /// Chat-Funktion mit Kontext
        /// </summary>
        public async Task<string> ChatAsync(string message, string model = DefaultModel)
        {
            try
            {
                var request = new ChatRequest
                {
                    Model = model,
                    Messages = new[]
                    {
                        new ChatMessage { Role = "user", Content = message }
                    },
                    Stream = false
                };

                var response = await _httpClient.PostAsJsonAsync("/api/chat", request);
                response.EnsureSuccessStatusCode();

                var result = await response.Content.ReadFromJsonAsync<ChatResponse>();
                return result?.Message?.Content ?? "Keine Antwort erhalten.";
            }
            catch (HttpRequestException ex)
            {
                return $"❌ Verbindungsfehler: {ex.Message}\n\n💡 Stelle sicher, dass Ollama läuft:\n   ollama serve";
            }
            catch (Exception ex)
            {
                return $"❌ Fehler: {ex.Message}";
            }
        }
    }

    #region DTOs (Data Transfer Objects)

    internal class GenerateRequest
    {
        [JsonPropertyName("model")]
        public string Model { get; set; } = "";

        [JsonPropertyName("prompt")]
        public string Prompt { get; set; } = "";

        [JsonPropertyName("stream")]
        public bool Stream { get; set; }
    }

    internal class GenerateResponse
    {
        [JsonPropertyName("model")]
        public string? Model { get; set; }

        [JsonPropertyName("response")]
        public string? Response { get; set; }

        [JsonPropertyName("done")]
        public bool Done { get; set; }
    }

    internal class ChatRequest
    {
        [JsonPropertyName("model")]
        public string Model { get; set; } = "";

        [JsonPropertyName("messages")]
        public ChatMessage[] Messages { get; set; } = Array.Empty<ChatMessage>();

        [JsonPropertyName("stream")]
        public bool Stream { get; set; }
    }

    internal class ChatMessage
    {
        [JsonPropertyName("role")]
        public string Role { get; set; } = "";

        [JsonPropertyName("content")]
        public string Content { get; set; } = "";
    }

    internal class ChatResponse
    {
        [JsonPropertyName("message")]
        public ChatMessage? Message { get; set; }

        [JsonPropertyName("done")]
        public bool Done { get; set; }
    }

    internal class ModelsResponse
    {
        [JsonPropertyName("models")]
        public ModelInfo[]? Models { get; set; }
    }

    internal class ModelInfo
    {
        [JsonPropertyName("name")]
        public string Name { get; set; } = "";
    }

    #endregion
}

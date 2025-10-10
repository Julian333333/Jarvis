using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using System;

namespace JarvisApp
{
    public sealed partial class MainWindow : Window
    {
        public MainWindow()
        {
            this.InitializeComponent();
            
            // Set window title
            this.Title = "JARVIS AI Assistant";
            
            // Set window size
            var appWindow = this.AppWindow;
            appWindow.Resize(new Windows.Graphics.SizeInt32(1000, 700));
        }

        private void SendButton_Click(object sender, RoutedEventArgs e)
        {
            string input = InputTextBox.Text.Trim();
            
            if (string.IsNullOrEmpty(input))
            {
                StatusTextBlock.Text = "Please enter a message";
                return;
            }

            // Update status
            StatusTextBlock.Text = "Processing...";
            
            // Simple response for demonstration
            ResponseTextBlock.Text = $"You asked: \"{input}\"\n\n" +
                                    $"This is a demo response. In a full implementation, this would connect to:\n" +
                                    $"• Ollama AI for intelligent responses\n" +
                                    $"• Voice recognition for speech input\n" +
                                    $"• System commands for task automation\n\n" +
                                    $"Received at: {DateTime.Now:HH:mm:ss}";
            
            // Clear input
            InputTextBox.Text = string.Empty;
            
            // Update status
            StatusTextBlock.Text = "Ready";
        }
    }
}

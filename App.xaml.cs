using Microsoft.UI.Xaml;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

namespace JarvisApp
{
    public partial class App : Application
    {
        private IHost _host;

        public App()
        {
            this.InitializeComponent();
            
            _host = Host.CreateDefaultBuilder()
                .ConfigureServices((context, services) =>
                {
                    // Register services here
                    services.AddSingleton<MainWindow>();
                })
                .Build();
        }

        protected override void OnLaunched(Microsoft.UI.Xaml.LaunchActivatedEventArgs args)
        {
            m_window = _host.Services.GetRequiredService<MainWindow>();
            m_window.Activate();
        }

        private Window m_window;
    }
}

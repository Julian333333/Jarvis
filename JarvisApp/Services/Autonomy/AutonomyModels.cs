using System;

namespace JarvisApp.Services.Autonomy
{
    public enum AutonomyMode
    {
        Off,
        Paused,
        Full
    }

    public enum AutonomyLogLevel
    {
        Info,
        Success,
        Warning,
        Error
    }

    public sealed class AutonomyLogEntry
    {
        public DateTimeOffset Timestamp { get; }
        public string Message { get; }
        public AutonomyLogLevel Level { get; }

        public AutonomyLogEntry(string message, AutonomyLogLevel level)
        {
            Timestamp = DateTimeOffset.Now;
            Message = message;
            Level = level;
        }
    }
}

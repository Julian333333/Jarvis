using System;

namespace JarvisApp.Services.Autonomy
{
    public enum AutonomyGoalStatus
    {
        Pending,
        InProgress,
        Completed,
        Failed,
        Canceled
    }

    public enum AutonomyPriority
    {
        Low = 0,
        Normal = 1,
        High = 2
    }

    public sealed class AutonomyGoal
    {
        public Guid Id { get; } = Guid.NewGuid();
        public string Description { get; }
        public AutonomyPriority Priority { get; }
        public int MaxSteps { get; }
        public AutonomyGoalStatus Status { get; internal set; } = AutonomyGoalStatus.Pending;
        public DateTimeOffset CreatedAt { get; } = DateTimeOffset.Now;
        public DateTimeOffset? StartedAt { get; internal set; }
        public DateTimeOffset? CompletedAt { get; internal set; }
        public string? LastResult { get; internal set; }

        public AutonomyGoal(string description, AutonomyPriority priority = AutonomyPriority.Normal, int maxSteps = 6)
        {
            if (string.IsNullOrWhiteSpace(description))
            {
                throw new ArgumentException("Goal description must not be empty", nameof(description));
            }

            Description = description.Trim();
            Priority = priority;
            MaxSteps = Math.Clamp(maxSteps, 3, 15);
        }

        internal AutonomyGoalSnapshot ToSnapshot()
        {
            return new AutonomyGoalSnapshot(Id, Description, Priority, Status, MaxSteps, CreatedAt, StartedAt, CompletedAt, LastResult);
        }

        public override string ToString()
        {
            return $"[{Status}] {Description}";
        }
    }

    public record AutonomyGoalSnapshot(
        Guid Id,
        string Description,
        AutonomyPriority Priority,
        AutonomyGoalStatus Status,
        int MaxSteps,
        DateTimeOffset CreatedAt,
        DateTimeOffset? StartedAt,
        DateTimeOffset? CompletedAt,
        string? LastResult);
}

using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using JarvisApp.Services;

namespace JarvisApp.Services.Autonomy
{
    /// <summary>
    /// Runs a background Sense→Plan→Act loop so Jarvis can pursue queued goals without user input.
    /// </summary>
    public sealed class AutonomyService : IDisposable
    {
        private readonly IntelligentCommandService _commandService;
        private readonly VisionService _visionService;
        private readonly List<AutonomyGoal> _goals = new();
        private readonly List<AutonomyLogEntry> _logs = new();
        private readonly object _sync = new();
        private CancellationTokenSource? _loopCts;
        private Task? _loopTask;
        private bool _disposed;
        private AutonomyMode _mode = AutonomyMode.Off;
        private AutonomyGoal? _activeGoal;

        public AutonomyService(IntelligentCommandService commandService, VisionService visionService)
        {
            _commandService = commandService;
            _visionService = visionService;
        }

        public AutonomyMode Mode => _mode;
        public bool IsRunning => _loopTask != null && !_loopTask.IsCompleted;

        public event EventHandler<AutonomyGoalSnapshot[]>? GoalsUpdated;
        public event EventHandler<AutonomyLogEntry>? LogEntryAdded;
        public event EventHandler<AutonomyMode>? ModeChanged;
        public event EventHandler<AutonomyGoalSnapshot?>? CurrentGoalChanged;

        public AutonomyGoalSnapshot[] GetGoalSnapshot()
        {
            lock (_sync)
            {
                return _goals.Select(goal => goal.ToSnapshot()).ToArray();
            }
        }

        public AutonomyLogEntry[] GetLogSnapshot()
        {
            lock (_sync)
            {
                return _logs.ToArray();
            }
        }

        public AutonomyGoalSnapshot AddGoal(string description, AutonomyPriority priority = AutonomyPriority.Normal, int maxSteps = 6)
        {
            var goal = new AutonomyGoal(description, priority, maxSteps);
            lock (_sync)
            {
                _goals.Add(goal);
            }

            RaiseGoalsUpdated();
            AppendLog($"Goal queued: {goal.Description}", AutonomyLogLevel.Info);
            EnsureLoop();
            return goal.ToSnapshot();
        }

        public void SetMode(AutonomyMode mode)
        {
            if (_mode == mode)
            {
                return;
            }

            _mode = mode;
            ModeChanged?.Invoke(this, _mode);
            AppendLog($"Autonomy mode set to {_mode}", AutonomyLogLevel.Info);

            if (_mode == AutonomyMode.Off)
            {
                StopLoop();
            }
            else
            {
                EnsureLoop();
            }
        }

        public void Pause()
        {
            if (_mode == AutonomyMode.Full)
            {
                _mode = AutonomyMode.Paused;
                ModeChanged?.Invoke(this, _mode);
                AppendLog("Autonomy paused", AutonomyLogLevel.Warning);
            }
        }

        public void Resume()
        {
            if (_mode == AutonomyMode.Paused)
            {
                _mode = AutonomyMode.Full;
                ModeChanged?.Invoke(this, _mode);
                AppendLog("Autonomy resumed", AutonomyLogLevel.Info);
                EnsureLoop();
            }
        }

        public void CancelAllGoals(AutonomyLogLevel level = AutonomyLogLevel.Warning, string? reason = null)
        {
            lock (_sync)
            {
                foreach (var goal in _goals.Where(g => g.Status is AutonomyGoalStatus.Pending or AutonomyGoalStatus.InProgress))
                {
                    goal.Status = AutonomyGoalStatus.Canceled;
                    goal.CompletedAt = DateTimeOffset.Now;
                    goal.LastResult = reason ?? "Canceled";
                }
            }

            RaiseGoalsUpdated();
            AppendLog(reason ?? "All goals canceled", level);
        }

        public AutonomyGoalSnapshot? GetActiveGoal()
        {
            lock (_sync)
            {
                return _activeGoal?.ToSnapshot();
            }
        }

        public void EmergencyStop(string? reason = null)
        {
            CancelAllGoals(AutonomyLogLevel.Error, reason ?? "Emergency stop");
            SetMode(AutonomyMode.Off);
        }

        private void EnsureLoop()
        {
            if (_loopTask != null && !_loopTask.IsCompleted)
            {
                return;
            }

            _loopCts = new CancellationTokenSource();
            _loopTask = Task.Run(() => RunLoopAsync(_loopCts.Token));
        }

        private void StopLoop()
        {
            try
            {
                _loopCts?.Cancel();
                _loopTask?.Wait(TimeSpan.FromSeconds(2));
            }
            catch (AggregateException)
            {
                // Ignored
            }
            finally
            {
                _loopCts?.Dispose();
                _loopCts = null;
                _loopTask = null;
            }
        }

        private async Task RunLoopAsync(CancellationToken token)
        {
            AppendLog("Autonomy loop started", AutonomyLogLevel.Info);
            while (!token.IsCancellationRequested)
            {
                if (_mode != AutonomyMode.Full)
                {
                    await Task.Delay(500, token);
                    continue;
                }

                AutonomyGoal? goal = null;
                lock (_sync)
                {
                    goal = _goals
                        .Where(g => g.Status == AutonomyGoalStatus.Pending)
                        .OrderByDescending(g => g.Priority)
                        .ThenBy(g => g.CreatedAt)
                        .FirstOrDefault();

                    if (goal != null)
                    {
                        goal.Status = AutonomyGoalStatus.InProgress;
                        goal.StartedAt = DateTimeOffset.Now;
                        _activeGoal = goal;
                    }
                }

                if (goal == null)
                {
                    await Task.Delay(750, token);
                    continue;
                }

                CurrentGoalChanged?.Invoke(this, goal.ToSnapshot());
                RaiseGoalsUpdated();

                await ExecuteGoalAsync(goal, token);

                lock (_sync)
                {
                    _activeGoal = null;
                }

                CurrentGoalChanged?.Invoke(this, null);
                RaiseGoalsUpdated();
                await Task.Delay(300, token);
            }
        }

        private async Task ExecuteGoalAsync(AutonomyGoal goal, CancellationToken token)
        {
            try
            {
                AppendLog($"Executing goal: {goal.Description}", AutonomyLogLevel.Info);
                string result;

                if (ShouldUseVision(goal.Description))
                {
                    result = await _visionService.RunAutonomousAgentAsync(goal.Description, goal.MaxSteps);
                }
                else
                {
                    result = await _commandService.ProcessCommandAsync(goal.Description);
                }

                token.ThrowIfCancellationRequested();

                goal.Status = AutonomyGoalStatus.Completed;
                goal.CompletedAt = DateTimeOffset.Now;
                goal.LastResult = result;
                AppendLog($"Goal completed: {goal.Description}", AutonomyLogLevel.Success);
            }
            catch (OperationCanceledException)
            {
                goal.Status = AutonomyGoalStatus.Canceled;
                goal.CompletedAt = DateTimeOffset.Now;
                goal.LastResult = "Canceled";
                AppendLog($"Goal canceled: {goal.Description}", AutonomyLogLevel.Warning);
            }
            catch (Exception ex)
            {
                goal.Status = AutonomyGoalStatus.Failed;
                goal.CompletedAt = DateTimeOffset.Now;
                goal.LastResult = ex.Message;
                AppendLog($"Goal failed: {goal.Description} -> {ex.Message}", AutonomyLogLevel.Error);
            }
        }

        private static bool ShouldUseVision(string description)
        {
            var lower = description.ToLowerInvariant();
            return lower.Contains("bildschirm") ||
                   lower.Contains("screen") ||
                   lower.Contains("vision") ||
                   lower.Contains("siehst") ||
                   lower.Contains("analysiere") ||
                   lower.Contains("screenshot") ||
                   lower.Contains("klicke") ||
                   lower.Contains("öffne") ||
                   lower.Contains("navigate");
        }

        private void AppendLog(string message, AutonomyLogLevel level)
        {
            var entry = new AutonomyLogEntry(message, level);
            lock (_sync)
            {
                _logs.Insert(0, entry);
                if (_logs.Count > 200)
                {
                    _logs.RemoveAt(_logs.Count - 1);
                }
            }

            LogEntryAdded?.Invoke(this, entry);
        }

        private void RaiseGoalsUpdated()
        {
            GoalsUpdated?.Invoke(this, GetGoalSnapshot());
        }

        public void Dispose()
        {
            if (_disposed)
            {
                return;
            }

            _disposed = true;
            StopLoop();
        }
    }
}

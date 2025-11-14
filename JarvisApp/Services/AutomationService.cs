using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading;
using System.Threading.Tasks;
using System.Linq;
using System.Collections.Generic;

namespace JarvisApp.Services
{
    /// <summary>
    /// Vollständige PC-Steuerung: Tastatur, Maus, Fenster, Prozesse
    /// </summary>
    public class AutomationService
    {
        #region Windows API Imports

        // Tastatur-Steuerung
        [DllImport("user32.dll")]
        private static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);

        [DllImport("user32.dll")]
        private static extern short VkKeyScan(char ch);

        // Maus-Steuerung
        [DllImport("user32.dll")]
        private static extern bool SetCursorPos(int X, int Y);

        [DllImport("user32.dll")]
        private static extern void mouse_event(uint dwFlags, int dx, int dy, uint dwData, UIntPtr dwExtraInfo);

        [DllImport("user32.dll")]
        private static extern bool GetCursorPos(out POINT lpPoint);

        // Fenster-Steuerung
        [DllImport("user32.dll")]
        private static extern IntPtr FindWindow(string? lpClassName, string? lpWindowName);

        [DllImport("user32.dll")]
        private static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        [DllImport("user32.dll")]
        private static extern bool IsWindowVisible(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern IntPtr GetForegroundWindow();

        [DllImport("user32.dll")]
        private static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);

        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);

        private delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

        // Bildschirm-Auflösung
        [DllImport("user32.dll")]
        private static extern int GetSystemMetrics(int nIndex);

        #endregion

        #region Konstanten

        private const uint KEYEVENTF_KEYDOWN = 0x0000;
        private const uint KEYEVENTF_KEYUP = 0x0002;
        private const uint KEYEVENTF_EXTENDEDKEY = 0x0001;

        private const uint MOUSEEVENTF_MOVE = 0x0001;
        private const uint MOUSEEVENTF_LEFTDOWN = 0x0002;
        private const uint MOUSEEVENTF_LEFTUP = 0x0004;
        private const uint MOUSEEVENTF_RIGHTDOWN = 0x0008;
        private const uint MOUSEEVENTF_RIGHTUP = 0x0010;
        private const uint MOUSEEVENTF_MIDDLEDOWN = 0x0020;
        private const uint MOUSEEVENTF_MIDDLEUP = 0x0040;
        private const uint MOUSEEVENTF_ABSOLUTE = 0x8000;

        private const int SW_HIDE = 0;
        private const int SW_SHOWNORMAL = 1;
        private const int SW_SHOWMINIMIZED = 2;
        private const int SW_MAXIMIZE = 3;
        private const int SW_SHOWNOACTIVATE = 4;
        private const int SW_SHOW = 5;
        private const int SW_MINIMIZE = 6;
        private const int SW_RESTORE = 9;

        private const int SM_CXSCREEN = 0;
        private const int SM_CYSCREEN = 1;

        #endregion

        #region Strukturen

        [StructLayout(LayoutKind.Sequential)]
        public struct POINT
        {
            public int X;
            public int Y;
        }

        #endregion

        #region Tastatur-Steuerung

        /// <summary>
        /// Schreibt Text wie mit der Tastatur
        /// </summary>
        public async Task TypeTextAsync(string text, int delayMs = 50)
        {
            foreach (char c in text)
            {
                if (c == '\n')
                {
                    PressKey(VirtualKeyCode.RETURN);
                }
                else
                {
                    TypeChar(c);
                }
                await Task.Delay(delayMs);
            }
        }

        /// <summary>
        /// Drückt eine einzelne Taste
        /// </summary>
        public void PressKey(VirtualKeyCode key, int holdMs = 50)
        {
            keybd_event((byte)key, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
            Thread.Sleep(holdMs);
            keybd_event((byte)key, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
        }

        /// <summary>
        /// Drückt eine Tastenkombination (z.B. Ctrl+C)
        /// </summary>
        public void PressKeyCombination(params VirtualKeyCode[] keys)
        {
            // Alle Tasten drücken
            foreach (var key in keys)
            {
                keybd_event((byte)key, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
                Thread.Sleep(10);
            }

            Thread.Sleep(50);

            // Alle Tasten loslassen (in umgekehrter Reihenfolge)
            foreach (var key in keys.Reverse())
            {
                keybd_event((byte)key, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
                Thread.Sleep(10);
            }
        }

        private void TypeChar(char c)
        {
            short vkCode = VkKeyScan(c);
            byte virtualKey = (byte)(vkCode & 0xFF);
            byte shiftState = (byte)(vkCode >> 8);

            // Shift-Taste drücken wenn nötig
            if ((shiftState & 1) != 0)
            {
                keybd_event((byte)VirtualKeyCode.SHIFT, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
            }

            // Taste drücken
            keybd_event(virtualKey, 0, KEYEVENTF_KEYDOWN, UIntPtr.Zero);
            Thread.Sleep(10);
            keybd_event(virtualKey, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);

            // Shift-Taste loslassen
            if ((shiftState & 1) != 0)
            {
                keybd_event((byte)VirtualKeyCode.SHIFT, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
            }
        }

        #endregion

        #region Maus-Steuerung

        /// <summary>
        /// Bewegt Maus zu Position
        /// </summary>
        public void MoveMouse(int x, int y)
        {
            SetCursorPos(x, y);
        }

        /// <summary>
        /// Führt Linksklick aus
        /// </summary>
        public void LeftClick()
        {
            mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, UIntPtr.Zero);
            Thread.Sleep(50);
            mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, UIntPtr.Zero);
        }

        /// <summary>
        /// Führt Rechtsklick aus
        /// </summary>
        public void RightClick()
        {
            mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, UIntPtr.Zero);
            Thread.Sleep(50);
            mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, UIntPtr.Zero);
        }

        /// <summary>
        /// Führt Doppelklick aus
        /// </summary>
        public void DoubleClick()
        {
            LeftClick();
            Thread.Sleep(100);
            LeftClick();
        }

        /// <summary>
        /// Klickt an bestimmter Position
        /// </summary>
        public void ClickAt(int x, int y)
        {
            MoveMouse(x, y);
            Thread.Sleep(100);
            LeftClick();
        }

        /// <summary>
        /// Holt aktuelle Mausposition
        /// </summary>
        public (int X, int Y) GetMousePosition()
        {
            GetCursorPos(out POINT point);
            return (point.X, point.Y);
        }

        #endregion

        #region Fenster-Steuerung

        /// <summary>
        /// Bringt Fenster in den Vordergrund
        /// </summary>
        public bool FocusWindow(string windowTitle)
        {
            IntPtr hWnd = FindWindowByTitle(windowTitle);
            if (hWnd != IntPtr.Zero)
            {
                SetForegroundWindow(hWnd);
                ShowWindow(hWnd, SW_RESTORE);
                return true;
            }
            return false;
        }

        /// <summary>
        /// Maximiert Fenster
        /// </summary>
        public bool MaximizeWindow(string windowTitle)
        {
            IntPtr hWnd = FindWindowByTitle(windowTitle);
            if (hWnd != IntPtr.Zero)
            {
                ShowWindow(hWnd, SW_MAXIMIZE);
                return true;
            }
            return false;
        }

        /// <summary>
        /// Minimiert Fenster
        /// </summary>
        public bool MinimizeWindow(string windowTitle)
        {
            IntPtr hWnd = FindWindowByTitle(windowTitle);
            if (hWnd != IntPtr.Zero)
            {
                ShowWindow(hWnd, SW_MINIMIZE);
                return true;
            }
            return false;
        }

        /// <summary>
        /// Schließt Fenster
        /// </summary>
        public bool CloseWindow(string windowTitle)
        {
            var processes = Process.GetProcesses()
                .Where(p => !string.IsNullOrEmpty(p.MainWindowTitle) && 
                           p.MainWindowTitle.Contains(windowTitle, StringComparison.OrdinalIgnoreCase));
            
            foreach (var process in processes)
            {
                try
                {
                    process.CloseMainWindow();
                    process.WaitForExit(2000);
                    if (!process.HasExited)
                    {
                        process.Kill();
                    }
                    return true;
                }
                catch { }
            }
            return false;
        }

        /// <summary>
        /// Listet alle offenen Fenster auf
        /// </summary>
        public List<string> GetOpenWindows()
        {
            var windows = new List<string>();
            
            EnumWindows((hWnd, lParam) =>
            {
                if (IsWindowVisible(hWnd))
                {
                    var text = new System.Text.StringBuilder(256);
                    if (GetWindowText(hWnd, text, 256) > 0)
                    {
                        string title = text.ToString();
                        if (!string.IsNullOrWhiteSpace(title))
                        {
                            windows.Add(title);
                        }
                    }
                }
                return true;
            }, IntPtr.Zero);

            return windows;
        }

        /// <summary>
        /// Holt aktuelles Vordergrund-Fenster
        /// </summary>
        public string GetActiveWindowTitle()
        {
            IntPtr hWnd = GetForegroundWindow();
            var text = new System.Text.StringBuilder(256);
            GetWindowText(hWnd, text, 256);
            return text.ToString();
        }

        private IntPtr FindWindowByTitle(string title)
        {
            IntPtr result = IntPtr.Zero;
            
            EnumWindows((hWnd, lParam) =>
            {
                if (IsWindowVisible(hWnd))
                {
                    var text = new System.Text.StringBuilder(256);
                    if (GetWindowText(hWnd, text, 256) > 0)
                    {
                        if (text.ToString().Contains(title, StringComparison.OrdinalIgnoreCase))
                        {
                            result = hWnd;
                            return false; // Stop enumeration
                        }
                    }
                }
                return true;
            }, IntPtr.Zero);

            return result;
        }

        #endregion

        #region Bildschirm-Info

        /// <summary>
        /// Holt Bildschirmauflösung
        /// </summary>
        public (int Width, int Height) GetScreenResolution()
        {
            return (GetSystemMetrics(SM_CXSCREEN), GetSystemMetrics(SM_CYSCREEN));
        }

        #endregion

        #region Prozess-Steuerung

        /// <summary>
        /// Startet Programm
        /// </summary>
        public Process? StartProgram(string path, string? arguments = null)
        {
            try
            {
                return Process.Start(new ProcessStartInfo
                {
                    FileName = path,
                    Arguments = arguments ?? "",
                    UseShellExecute = true
                });
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Beendet Prozess nach Namen
        /// </summary>
        public bool KillProcess(string processName)
        {
            try
            {
                var processes = Process.GetProcessesByName(processName);
                foreach (var process in processes)
                {
                    process.Kill();
                    process.WaitForExit(2000);
                }
                return processes.Length > 0;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Prüft ob Prozess läuft
        /// </summary>
        public bool IsProcessRunning(string processName)
        {
            return Process.GetProcessesByName(processName).Length > 0;
        }

        /// <summary>
        /// Listet alle laufenden Prozesse
        /// </summary>
        public List<string> GetRunningProcesses()
        {
            return Process.GetProcesses()
                .Where(p => !string.IsNullOrEmpty(p.MainWindowTitle))
                .Select(p => $"{p.ProcessName} - {p.MainWindowTitle}")
                .ToList();
        }

        #endregion
    }

    #region Virtual Key Codes

    public enum VirtualKeyCode : byte
    {
        // Modifier Keys
        SHIFT = 0x10,
        CONTROL = 0x11,
        ALT = 0x12,
        LWIN = 0x5B,
        RWIN = 0x5C,

        // Common Letters for shortcuts
        VK_A = 0x41,
        VK_C = 0x43,
        VK_V = 0x56,
        VK_X = 0x58,
        VK_Z = 0x5A,

        // Function Keys
        F1 = 0x70,
        F2 = 0x71,
        F3 = 0x72,
        F4 = 0x73,
        F5 = 0x74,
        F6 = 0x75,
        F7 = 0x76,
        F8 = 0x77,
        F9 = 0x78,
        F10 = 0x79,
        F11 = 0x7A,
        F12 = 0x7B,

        // Navigation Keys
        LEFT = 0x25,
        UP = 0x26,
        RIGHT = 0x27,
        DOWN = 0x28,
        HOME = 0x24,
        END = 0x23,
        PRIOR = 0x21,  // Page Up
        NEXT = 0x22,   // Page Down

        // Editing Keys
        BACK = 0x08,   // Backspace
        TAB = 0x09,
        RETURN = 0x0D, // Enter
        ESCAPE = 0x1B,
        SPACE = 0x20,
        DELETE = 0x2E,
        INSERT = 0x2D,

        // Special Keys
        PRINT = 0x2A,
        SNAPSHOT = 0x2C, // Print Screen
        PAUSE = 0x13,
        CAPITAL = 0x14,  // Caps Lock
        NUMLOCK = 0x90,
        SCROLL = 0x91,

        // Media Keys
        VOLUME_MUTE = 0xAD,
        VOLUME_DOWN = 0xAE,
        VOLUME_UP = 0xAF,
        MEDIA_NEXT_TRACK = 0xB0,
        MEDIA_PREV_TRACK = 0xB1,
        MEDIA_STOP = 0xB2,
        MEDIA_PLAY_PAUSE = 0xB3,
    }

    #endregion
}

# Focus Timer - Dynamic Island Style Pomodoro

A sleek Windows desktop application styled after Apple's Dynamic Island. Features a floating pill-shaped timer widget, Pomodoro timer, task management, weather display, and fullscreen focus mode.

![Pure Black & Green Theme](https://img.shields.io/badge/Theme-Pure%20Black%20%26%20Green-000000?style=for-the-badge)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776ab?style=for-the-badge)
![PySide6](https://img.shields.io/badge/PySide6-6.10.1-118c7c?style=for-the-badge)
![Windows](https://img.shields.io/badge/Platform-Windows-0078d4?style=for-the-badge)

## Features

### ⏱️ Pomodoro Timer
- **25-minute work sessions** with customizable duration
- **5-minute break periods** with customizable duration
- **Auto-start breaks** after work sessions complete
- **Sound notifications** with multiple alarm options (Chime, Bell, Digital, Gentle)
- **Progress circle** showing time remaining

### 🎨 Dynamic Island UI
- **Floating pill-shaped widget** that stays on top
- **Compact mini view** (200x48px) for minimal screen real estate
- **Expandable dashboard** (340x440px) with full controls
- **Pure black background** with vibrant green accents (#4ADE80)
- **Smooth animations** for expand/collapse transitions
- **Draggable** - move the widget anywhere on screen

### 📋 Task Management
- **Add tasks** before or during focus sessions
- **Track focus time** per task
- **Mark tasks complete** with checkbox
- **Delete tasks** easily
- **Task selection** for focused work

### 📊 Statistics & Analytics
- **Daily stats** - Total focus time and sessions today
- **Weekly chart** - Last 7 days of focus time
- **Session history** - All-time statistics
- **Progress tracking** - Visual bar charts

### 🌤️ Weather Display
- **Real-time weather** from wttr.in API
- **Current temperature** and conditions
- **Location display** on dashboard
- **Auto-refresh** every 30 minutes

### 🖥️ Fullscreen Focus Mode
- **Immersive fullscreen** with F11 or button
- **Large time display** showing hours:minutes
- **Greeting** (Good Morning/Night based on time)
- **Weather info** during focus sessions
- **Minimal distractions** - clean, dark interface

### 🔔 System Integration
- **System tray** integration with green accent
- **Tray menu** for quick controls
- **Keyboard shortcuts**:
  - `Space` - Play/Pause
  - `R` - Reset timer
  - `Esc` - Collapse widget
  - `F11` - Fullscreen mode
- **Sound alerts** and notifications
- **Auto-start** minimized to tray

### 💾 Data Storage
- **SQLite database** - All data stored locally
- **Location**: `%APPDATA%/DynamicIslandTimer/`
- **Tasks** - Persistent storage
- **Settings** - Duration preferences saved
- **Statistics** - Complete session history

## Installation

### Option 1: Standalone Executable (Recommended)
Simply download and run `FocusTimer.exe` from the `dist/` folder. No Python installation required!

### Option 2: From Source
```bash
# Clone the repository
git clone <repo-url>
cd apps

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

## Requirements (Source Installation)

- Python 3.12+
- PySide6 6.10.1
- pygame 2.6.1
- requests

## Project Structure

```
apps/
├── core/
│   ├── timer.py          # Pomodoro timer logic
│   ├── database.py       # SQLite management
│   ├── sounds.py         # Audio playback
│   └── weather.py        # Weather service (wttr.in)
├── ui/
│   ├── styles.py         # Theme configuration
│   ├── island.py         # Mini widget (pill-shaped)
│   ├── dashboard.py      # Expanded dashboard view
│   ├── fullscreen.py     # Fullscreen focus mode
│   ├── components.py     # Reusable UI components
│   └── icons.py          # Custom icon painter
├── static/
│   ├── sounds/           # Audio files
│   │   ├── chime.wav
│   │   ├── bell.wav
│   │   ├── digital.wav
│   │   └── gentle.wav
│   └── generate_icons.py # Icon generator
├── fonts/                # Custom fonts
├── main.py               # Application controller
└── requirements.txt      # Python dependencies
```

## Usage

### Starting the App
```bash
python main.py
# or launch FocusTimer.exe
```

The app starts minimized in the system tray. Click the green dot to expand the widget.

### Basic Workflow
1. **Add a task** in the Tasks tab
2. **Select the task** you want to focus on
3. **Click the green button** to start the timer
4. **Focus for 25 minutes** on your task
5. **Take a 5-minute break** after each session
6. **View stats** to track your progress

### Customization
Open the **Settings tab** to:
- Adjust work duration (5-60 minutes)
- Adjust break duration (1-30 minutes)
- Change alarm sound
- View keyboard shortcuts

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Space` | Play/Pause timer |
| `R` | Reset timer to beginning |
| `Esc` | Collapse expanded view |
| `F11` | Toggle fullscreen mode |
| `Click & Drag` | Move widget on screen |

## Theme

### Colors
- **Background**: Pure Black (#000000)
- **Primary Accent**: Green (#4ADE80)
- **Secondary Accent**: Yellow (#FACC15) - for break mode
- **Text Primary**: White (#FFFFFF)
- **Text Secondary**: Light Gray (#A3A3A3)
- **Elevated**: Dark Gray (#1A1A1A)

### Design System
- **Border Radius**: 12-24px for smooth pills & cards
- **Shadows**: Minimal, clean aesthetic
- **Borders**: Subtle, high-contrast accents
- **Typography**: Segoe UI, bold headings

## Building the Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build standalone exe
python -m PyInstaller --name "FocusTimer" --onefile --windowed \
  --add-data "static:static" --add-data "fonts:fonts" main.py
```

The executable will be created in `dist/FocusTimer.exe`

## Troubleshooting

### App won't start
- Ensure Python 3.12+ is installed
- Check that all dependencies are installed: `pip install -r requirements.txt`

### No sounds playing
- Check that audio files exist in `static/sounds/`
- Verify system volume is not muted
- Try different alarm sounds in settings

### Weather not showing
- Check internet connection
- wttr.in API may be temporarily unavailable
- Restart the app to retry

### Database errors
- Delete `%APPDATA%/DynamicIslandTimer/` folder and restart
- App will recreate database automatically

## Development

### Adding New Sounds
1. Place WAV files in `static/sounds/`
2. Add to `SoundManager.SOUNDS` dict in `core/sounds.py`
3. Add to combo box in `ui/dashboard.py` settings

### Modifying Colors
Edit `Theme` class in `ui/styles.py`:
```python
ACCENT = "#4ADE80"  # Main green
SECONDARY = "#FACC15"  # Break yellow
```

### Custom Icons
Modify `ui/icons.py` `IconPainter` class to add new painted icons.

## Performance

- **Memory**: ~80-120MB
- **CPU**: <1% idle, <5% while running
- **Disk**: SQLite database grows ~1KB per timer session
- **Startup time**: ~2-3 seconds

## Known Limitations

- Windows only (uses Windows layered windows API)
- Requires always-on-top capability
- Some terminal emulators may interfere with layered windows

## Future Features

- [ ] Cross-platform support (macOS, Linux)
- [ ] Multiple timer modes (Pomodoro, 52/17, etc.)
- [ ] Custom break activities (Stretch, Meditation)
- [ ] Export statistics (CSV, PDF)
- [ ] Dark/Light theme toggle
- [ ] Custom colors picker
- [ ] Synced timer with team
- [ ] Focus session reminders

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Author

Built with ❤️ using PySide6 and Python

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Start focusing, stop procrastinating! 🎯**

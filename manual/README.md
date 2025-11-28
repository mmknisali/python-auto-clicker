# Auto Clicker App

A fancy GUI application for automating keyboard and mouse actions with profiles, loops, and hotkeys.

## Features

- 🎯 Dark theme GUI with emojis
- 📋 Manage profiles with custom sequences
- ⌨ Add hotkeys via dropdown selection
- ⏰ Add sleep delays
- 🎥 Record sequences (Windows only)
- 🔄 Loop execution
- ▶️ Start, pause, stop controls
- 🔥 Hotkey controls (f1 start, f2 pause, f3 switch)
- 📁 Export/import profiles
- ⬆️⬇️ Move actions up/down

## Installation

### Installation

1. Download `AutoClicker.msi` from releases
2. Run the MSI installer (includes Python and all dependencies)
3. Launch "Auto Clicker" from Start Menu

### Manual Installation (for Developers)

1. Ensure Python 3.8+ is installed
2. Run `pip install pyqt6 pynput pyautogui`
3. Run `python main.py`

### Building MSI (for Developers)

To create the MSI installer:

1. Install PyInstaller: `pip install pyinstaller`
2. Run `pyinstaller --onedir --msi main.py`
3. Find `AutoClicker.msi` in `dist/` folder

## Usage

- Select a profile
- Use buttons to start once or loop
- Pause/resume with button or f2
- Stop with button
- Settings: add/edit/delete profiles, assign hotkeys
- Edit profile: add hotkeys, sleeps, record sequences, move actions

## Requirements

- Python 3.8+
- PyQt6
- pynput
- pyautogui

## License

MIT
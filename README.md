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

### Option 1: MSI Installer (Recommended for Windows)

1. Ensure Python 3.8+ is installed on your system 
2. Download `AutoClicker.msi` from the releases page
3. Run the MSI installer (it includes Python and all dependencies)
4. Launch "Auto Clicker" from the Start Menu
5. The app is ready to use

### Option 2: Manual Installation

1. Ensure Python 3.8+ is installed on your system
2. Install dependencies: `pip install pyqt6 pynput pyautogui`
3. Download `main.py` and `config.json` from the `manual/` folder
4. Run `python main.py`
5. The app will create a default config if none exists

## Usage

1. **Select Profile**: Choose a profile from the dropdown
2. **Edit Profiles**: Click "Settings" to add/edit/delete profiles
   - Add profiles with custom names
   - Edit profiles to add actions: hotkeys, sleeps
   - Use "Add Hotkey" to select modifier and key from dropdowns
   - Use "Add Sleep" to add delays
   - Use "Record Sequence" to record actions (Windows only)
   - Check "Loop" to repeat the sequence
   - Move actions up/down with buttons
3. **Controls**:
   - "Start Once": Run the profile once
   - "Start Loop": Run the profile in a loop
   - "Pause/Resume": Pause or resume execution
   - "Stop": Stop the loop
4. **Hotkeys** (can be changed in Settings):
   - F1: Start current profile
   - F2: Pause/Resume
   - F3: Switch to next profile
5. **Export/Import**: In Settings, export profiles to JSON or import from JSON

## Building the MSI (for Developers)

To create the MSI installer on Windows:

1. Install Python and dependencies: `pip install pyqt6 pynput pyautogui pyinstaller`
2. Run the build script: `build.bat` (in `Windows/` folder)
3. The MSI will be created in `dist/AutoClicker.msi`

## Requirements

- Python 3.8+
- PyQt6
- pynput
- pyautogui
- PyInstaller (for building)

## License

MIT

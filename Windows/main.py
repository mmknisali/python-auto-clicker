import pyautogui as pg
import time
import json
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QComboBox, QLabel, QDialog, QListWidget, QLineEdit, QInputDialog, QCheckBox, QFileDialog, QMessageBox, QStyle
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QColor
from pynput.keyboard import Listener

# Auto-click app with profiles and hotkeys on Wayland (Hyprland)
# Run with: source venv/bin/activate && python main.py

config_file = 'config.json'
default_config = {
    'profiles': {
        'Copy-Paste': {
            'actions': [
                {'type': 'hotkey', 'key1': 'ctrl', 'key2': 'a'},
                {'type': 'sleep', 'time': 0.5},
                {'type': 'hotkey', 'key1': 'ctrl', 'key2': 'c'},
                {'type': 'sleep', 'time': 0.5},
                {'type': 'hotkey', 'key1': 'ctrl', 'key2': 'v'},
                {'type': 'sleep', 'time': 0.5},
            ],
            'loop': False,
        },
        'Save': {
            'actions': [
                {'type': 'hotkey', 'key1': 'ctrl', 'key2': 's'},
            ],
            'loop': False,
        },
    },
    'current_profile': 'Copy-Paste',
    'start_key': 'f1',
    'pause_key': 'f2',
    'switch_key': 'f3',
}

if os.path.exists(config_file):
    with open(config_file) as f:
        config = json.load(f)
    # Migrate old config
    for name, data in config['profiles'].items():
        if isinstance(data, list):
            config['profiles'][name] = {'actions': data, 'loop': False}
else:
    config = default_config.copy()
    with open(config_file, 'w') as f:
        json.dump(config, f)

class KeyListener(QThread):
    key_pressed = pyqtSignal(str)

    def run(self):
        with Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        try:
            k = key.char
        except AttributeError:
            k = str(key).replace('Key.', '').lower()
        self.key_pressed.emit(k)

class Executor(QThread):
    def __init__(self, actions, loop, paused, stopped):
        super().__init__()
        self.actions = actions
        self.loop = loop
        self.paused = paused
        self.stopped = stopped

    def run(self):
        time.sleep(1)
        def execute_actions():
            for action in self.actions:
                if self.stopped[0]:
                    return
                while self.paused[0]:
                    time.sleep(0.1)
                if action['type'] == 'hotkey':
                    if action['key1']:
                        modifiers = action['key1'].split('+')
                        pg.hotkey(*modifiers, action['key2'])
                    else:
                        pg.press(action['key2'])
                elif action['type'] == 'sleep':
                    time.sleep(action['time'])
        if self.loop:
            while not self.stopped[0]:
                execute_actions()
        else:
            execute_actions()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Click App")
        self.layout = QVBoxLayout()
        title = QLabel("🎯 Auto Clicker App")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff00; margin: 10px;")
        self.layout.addWidget(title)
        self.layout.addWidget(QLabel("Select Profile:"))
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(config['profiles'].keys())
        self.profile_combo.setCurrentText(config['current_profile'])
        self.layout.addWidget(self.profile_combo)
        self.start_once_btn = QPushButton("▶ Start Once")
        self.start_once_btn.clicked.connect(lambda: self.start_execution(loop=False))
        self.layout.addWidget(self.start_once_btn)
        self.start_loop_btn = QPushButton("🔄 Start Loop")
        self.start_loop_btn.clicked.connect(lambda: self.start_execution(loop=True))
        self.layout.addWidget(self.start_loop_btn)
        self.pause_btn = QPushButton("⏸ Pause/Resume")
        self.pause_btn.clicked.connect(self.pause_execution)
        self.layout.addWidget(self.pause_btn)
        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.clicked.connect(self.stop_execution)
        self.layout.addWidget(self.stop_btn)
        self.settings_btn = QPushButton("⚙ Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        self.layout.addWidget(self.settings_btn)
        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)
        self.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                border: 1px solid #777;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #666;
            }
            QPushButton:pressed {
                background-color: #444;
            }
            QComboBox {
                background-color: #333;
                color: white;
                border: 1px solid #777;
                padding: 2px;
            }
            QListWidget {
                background-color: #333;
                color: white;
                border: 1px solid #777;
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                background-color: #333;
                color: white;
                border: 1px solid #777;
                padding: 2px;
            }
        """)
        self.listener = KeyListener()
        self.listener.key_pressed.connect(self.handle_key)
        self.listener.start()
        self.running = False
        self.paused = [False]
        self.stopped = [False]

    def handle_key(self, key):
        if key == config['start_key']:
            self.start_execution()
        elif key == config['pause_key']:
            self.pause_execution()
        elif key == config['switch_key']:
            self.switch_profile()

    def start_execution(self, loop=False):
        if self.running:
            return
        self.running = True
        self.paused[0] = False
        self.stopped[0] = False
        profile = self.profile_combo.currentText()
        actions = config['profiles'][profile]['actions']
        loop_flag = loop or config['profiles'][profile]['loop']
        self.executor = Executor(actions, loop_flag, self.paused, self.stopped)
        self.executor.finished.connect(self.on_finished)
        self.executor.start()

    def stop_execution(self):
        self.stopped[0] = True

    def pause_execution(self):
        self.paused[0] = not self.paused[0]

    def switch_profile(self):
        current = self.profile_combo.currentIndex()
        next_idx = (current + 1) % self.profile_combo.count()
        self.profile_combo.setCurrentIndex(next_idx)
        config['current_profile'] = self.profile_combo.currentText()
        with open(config_file, 'w') as f:
            json.dump(config, f)

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            self.reload_profiles()

    def reload_profiles(self):
        self.profile_combo.clear()
        self.profile_combo.addItems(config['profiles'].keys())
        if config['current_profile'] in config['profiles']:
            self.profile_combo.setCurrentText(config['current_profile'])

    def on_finished(self):
        self.running = False

class SettingsDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.layout = QVBoxLayout()
        # Profiles
        self.profiles_list = QListWidget()
        self.profiles_list.addItems(config['profiles'].keys())
        self.layout.addWidget(QLabel("Profiles:"))
        self.layout.addWidget(self.profiles_list)
        self.add_profile_btn = QPushButton("➕ Add Profile")
        self.add_profile_btn.clicked.connect(self.add_profile)
        self.layout.addWidget(self.add_profile_btn)
        self.edit_profile_btn = QPushButton("✏ Edit Profile")
        self.edit_profile_btn.clicked.connect(self.edit_profile)
        self.layout.addWidget(self.edit_profile_btn)
        self.delete_profile_btn = QPushButton("🗑 Delete Profile")
        self.delete_profile_btn.clicked.connect(self.delete_profile)
        self.layout.addWidget(self.delete_profile_btn)
        self.import_profile_btn = QPushButton("📁 Import Profile")
        self.import_profile_btn.clicked.connect(self.import_profile)
        self.layout.addWidget(self.import_profile_btn)
        # Hotkeys
        self.start_key_edit = QLineEdit(config['start_key'])
        self.layout.addWidget(QLabel("Start Key:"))
        self.layout.addWidget(self.start_key_edit)
        self.pause_key_edit = QLineEdit(config['pause_key'])
        self.layout.addWidget(QLabel("Pause Key:"))
        self.layout.addWidget(self.pause_key_edit)
        self.switch_key_edit = QLineEdit(config['switch_key'])
        self.layout.addWidget(QLabel("Switch Key:"))
        self.layout.addWidget(self.switch_key_edit)
        # Save
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)
        self.layout.addWidget(self.save_btn)
        self.setLayout(self.layout)

    def add_profile(self):
        name, ok = QInputDialog.getText(self, "New Profile", "Name:")
        if ok and name:
            config['profiles'][name] = []
            self.profiles_list.addItem(name)

    def edit_profile(self):
        current = self.profiles_list.currentItem()
        if not current:
            return
        name = current.text()
        edit_dialog = EditProfileDialog(config['profiles'][name], self)
        edit_dialog.exec()

    def delete_profile(self):
        current = self.profiles_list.currentItem()
        if not current:
            return
        name = current.text()
        del config['profiles'][name]
        self.profiles_list.takeItem(self.profiles_list.row(current))

    def export_profile(self):
        current = self.profiles_list.currentItem()
        if not current:
            return
        name = current.text()
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Profile", f"{name}.json", "JSON Files (*.json)")
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(config['profiles'][name], f)

    def import_profile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Profile", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path) as f:
                data = json.load(f)
            name, ok = QInputDialog.getText(self, "Import Profile", "Name:")
            if ok and name:
                config['profiles'][name] = data
                self.profiles_list.addItem(name)







    def save_settings(self):
        config['start_key'] = self.start_key_edit.text()
        config['pause_key'] = self.pause_key_edit.text()
        config['switch_key'] = self.switch_key_edit.text()
        with open(config_file, 'w') as f:
            json.dump(config, f)
        self.accept()

class EditProfileDialog(QDialog):
    def __init__(self, profile_data, parent):
        super().__init__(parent)
        self.profile_data = profile_data
        self.setWindowTitle("Edit Profile")
        self.layout = QVBoxLayout()
        self.actions_list = QListWidget()
        self.refresh_list()
        self.layout.addWidget(self.actions_list)
        self.add_hotkey_btn = QPushButton("⌨ Add Hotkey")
        self.add_hotkey_btn.clicked.connect(self.add_hotkey)
        self.layout.addWidget(self.add_hotkey_btn)
        self.add_sleep_btn = QPushButton("⏰ Add Sleep")
        self.add_sleep_btn.clicked.connect(self.add_sleep)
        self.layout.addWidget(self.add_sleep_btn)
        self.record_sequence_btn = QPushButton("🎥 Record Sequence")
        self.record_sequence_btn.clicked.connect(self.record_sequence)
        self.layout.addWidget(self.record_sequence_btn)
        self.remove_action_btn = QPushButton("🗑 Remove Action")
        self.remove_action_btn.clicked.connect(self.remove_action)
        self.layout.addWidget(self.remove_action_btn)
        self.move_up_btn = QPushButton("⬆ Move Up")
        self.move_up_btn.clicked.connect(self.move_up)
        self.layout.addWidget(self.move_up_btn)
        self.move_down_btn = QPushButton("⬇ Move Down")
        self.move_down_btn.clicked.connect(self.move_down)
        self.layout.addWidget(self.move_down_btn)
        self.loop_cb = QCheckBox("Loop")
        self.loop_cb.setChecked(self.profile_data.get('loop', False))
        self.layout.addWidget(self.loop_cb)
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_profile)
        self.layout.addWidget(self.save_btn)
        self.setLayout(self.layout)

    def add_hotkey(self):
        dialog = HotkeyDialog()
        if dialog.exec():
            key1 = dialog.modifier_combo.currentText()
            key2 = dialog.key_combo.currentText()
            if key2:
                self.profile_data['actions'].append({'type': 'hotkey', 'key1': key1 if key1 != 'None' else '', 'key2': key2})
                self.actions_list.addItem(f"Hotkey: {key1} + {key2}" if key1 and key1 != 'None' else f"Hotkey: {key2}")

    def add_sleep(self):
        time, ok = QInputDialog.getDouble(self, "Sleep", "Time (s):", 0.5, 0, 10, 1)
        if ok:
            self.profile_data['actions'].append({'type': 'sleep', 'time': time})
            self.actions_list.addItem(f"Sleep: {time}s")

    def remove_action(self):
        current = self.actions_list.currentRow()
        if current >= 0:
            del self.profile_data['actions'][current]
            self.actions_list.takeItem(current)

    def move_up(self):
        current = self.actions_list.currentRow()
        if current > 0:
            self.profile_data['actions'][current], self.profile_data['actions'][current-1] = self.profile_data['actions'][current-1], self.profile_data['actions'][current]
            self.refresh_list()
            self.actions_list.setCurrentRow(current-1)

    def move_down(self):
        current = self.actions_list.currentRow()
        if current < len(self.profile_data['actions']) - 1:
            self.profile_data['actions'][current], self.profile_data['actions'][current+1] = self.profile_data['actions'][current+1], self.profile_data['actions'][current]
            self.refresh_list()
            self.actions_list.setCurrentRow(current+1)

    def refresh_list(self):
        self.actions_list.clear()
        for action in self.profile_data['actions']:
            if action['type'] == 'hotkey':
                self.actions_list.addItem(f"Hotkey: {action['key1']} + {action['key2']}" if action['key1'] else f"Hotkey: {action['key2']}")
            elif action['type'] == 'sleep':
                self.actions_list.addItem(f"Sleep: {action['time']}s")

    def record_sequence(self):
        QMessageBox.information(self, "Recording", "Recording started. Press keys, then close dialog to stop.")
        self.record_dialog = RecordDialog()
        self.record_dialog.finished.connect(self.set_recorded_actions)
        self.record_dialog.exec()

    def set_recorded_actions(self, actions):
        self.profile_data['actions'] = actions
        self.refresh_list()

    def save_profile(self):
        self.profile_data['loop'] = self.loop_cb.isChecked()
        self.accept()



class RecordDialog(QDialog):
    finished = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recording")
        self.layout = QVBoxLayout()
        self.label = QLabel("Recording... Press keys, then close dialog to stop.")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.events = []
        self.start_time = time.time()
        self.pressed = set()
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def closeEvent(self, event):
        self.listener.stop()
        # Process events
        actions = []
        last_time = 0
        for event in self.events:
            if event[0] == 'key_press':
                key_data = event[1]
                if last_time > 0:
                    actions.append({'type': 'sleep', 'time': event[2] - last_time})
                actions.append({'type': 'hotkey', 'key1': key_data['key1'], 'key2': key_data['key2']})
                last_time = event[2]
        self.finished.emit(actions)
        event.accept()

    def on_press(self, key):
        if hasattr(key, 'char') and key.char and key.char.isprintable():
            modifiers = sorted(self.pressed)
            key1 = '+'.join(modifiers) if modifiers else ''
            key2 = key.char
            self.events.append(('key_press', {'key1': key1, 'key2': key2}, time.time() - self.start_time))
        else:
            k = str(key).replace('Key.', '').lower()
            if 'ctrl' in k:
                self.pressed.add('ctrl')
            elif 'alt' in k:
                self.pressed.add('alt')
            elif 'shift' in k:
                self.pressed.add('shift')

    def on_release(self, key):
        k = str(key).replace('Key.', '').lower()
        if 'ctrl' in k:
            self.pressed.discard('ctrl')
        elif 'alt' in k:
            self.pressed.discard('alt')
        elif 'shift' in k:
            self.pressed.discard('shift')

class HotkeyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Hotkey")
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Modifier:"))
        self.modifier_combo = QComboBox()
        self.modifier_combo.addItems(['None', 'ctrl', 'shift', 'alt', 'ctrl+shift', 'ctrl+alt', 'shift+alt', 'ctrl+shift+alt'])
        self.layout.addWidget(self.modifier_combo)
        self.layout.addWidget(QLabel("Key:"))
        self.key_combo = QComboBox()
        keys = [chr(i) for i in range(ord('a'), ord('z')+1)] + [str(i) for i in range(10)] + [f'f{i}' for i in range(1,13)] + ['enter', 'space', 'tab', 'backspace', 'delete', 'escape', 'up', 'down', 'left', 'right']
        self.key_combo.addItems(keys)
        self.layout.addWidget(self.key_combo)
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_btn)
        self.setLayout(self.layout)

class CaptureDialog(QDialog):
    captured = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Capture Key")
        self.layout = QVBoxLayout()
        self.label = QLabel("Press the key combination")
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.pressed = set()
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    def on_press(self, key):
        if hasattr(key, 'char') and key.char and key.char.isprintable():
            modifiers = sorted(self.pressed)
            key1 = '+'.join(modifiers) if modifiers else ''
            key2 = key.char
            self.captured.emit(key1, key2)
            self.listener.stop()
            self.accept()
        else:
            k = str(key).replace('Key.', '').lower()
            if 'ctrl' in k:
                self.pressed.add('ctrl')
            elif 'alt' in k:
                self.pressed.add('alt')
            elif 'shift' in k:
                self.pressed.add('shift')

    def on_release(self, key):
        k = str(key).replace('Key.', '').lower()
        if 'ctrl' in k:
            self.pressed.discard('ctrl')
        elif 'alt' in k:
            self.pressed.discard('alt')
        elif 'shift' in k:
            self.pressed.discard('shift')

if __name__ == "__main__":
    app = QApplication([])
    app.setStyle('Fusion')
    dark_palette = app.palette()
    dark_palette.setColor(dark_palette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.ColorRole.WindowText, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.ColorRole.Base, QColor(25, 25, 25))
    dark_palette.setColor(dark_palette.ColorRole.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.ColorRole.ToolTipBase, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.ColorRole.ToolTipText, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.ColorRole.Text, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(dark_palette.ColorRole.ButtonText, QColor(255, 255, 255))
    dark_palette.setColor(dark_palette.ColorRole.BrightText, QColor(255, 0, 0))
    dark_palette.setColor(dark_palette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(dark_palette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(dark_palette.ColorRole.HighlightedText, QColor(0, 0, 0))
    app.setPalette(dark_palette)
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    window = MainWindow()
    window.resize(600, 400)
    window.show()
    app.exec()
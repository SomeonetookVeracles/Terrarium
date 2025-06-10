from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QFormLayout, QComboBox, QCheckBox,
    QPushButton, QVBoxLayout, QScrollArea, QHBoxLayout, QApplication, 
    QMessageBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from config_helper import load_config, save_config, get_default_config, debug_log
import json  #! Keep this

class SettingsPage(QWidget):
    petReset = pyqtSignal()  # Emits when the pet is reset

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.init_ui()

    #* Apply theme instantly when selected
    def apply_theme_immediately(self):
        current_theme_name = self.theme_dropdown.currentText()
        all_themes = self.config.get("DISPLAY", {}).get("THEMES", [])
        fallback = "QWidget { background-color: white; }"

        for theme in all_themes:
            if theme["name"] == current_theme_name:
                css = theme.get("content", "").strip()
                if css:
                    QApplication.instance().setStyleSheet(css)
                    if self.config.get("GLOBALS", {}).get("DEVMODE", False):
                        print(f"[DEVMODE] Applied theme: {current_theme_name}")
                    return
                else:
                    print(f"[WARNING] Theme '{current_theme_name}' is empty. Using fallback.")
                    QApplication.instance().setStyleSheet(fallback)
                    return

        print(f"[WARNING] Theme '{current_theme_name}' not found. Using fallback.")
        QApplication.instance().setStyleSheet(fallback)        

    #* UI Setup
    def init_ui(self):
        self.setObjectName("settings-page")

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QFormLayout()
        scroll_layout.setSpacing(12)

        #* API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setPlaceholderText("Enter Hackatime Api Key")
        self.api_key_input.setText(self.config["GLOBALS"].get("WAKA_API_KEY", ""))
        scroll_layout.addRow(QLabel("Hackatime API Key"), self.api_key_input)
        #* Refresh Rate
        self.refreshrate = QLineEdit(str(int(self.config["GLOBALS"].get("refreshrate"))))
        self.refreshrate.setPlaceholderText("Default: 15s")
        self.refreshrate.textChanged.connect(self.update_refreshrate)
        scroll_layout.addRow(QLabel("Game TPS"), self.refreshrate)
        #* Width
        self.width_input = QLineEdit(str(int(self.config["DISPLAY"].get("width_ratio", 0.5) * 100)))
        self.width_input.setPlaceholderText("Default: 33%")
        self.width_input.textChanged.connect(self.update_width_ratio)
        scroll_layout.addRow(QLabel("% width of screen"), self.width_input)

        #* Height
        self.height_input = QLineEdit(str(int(self.config["DISPLAY"].get("height_ratio", 0.5) * 100)))
        self.height_input.setPlaceholderText("Default: 50%")
        self.height_input.textChanged.connect(self.update_height_ratio)
        scroll_layout.addRow(QLabel("% height of screen"), self.height_input)

        #* Theme dropdown
        self.theme_dropdown = QComboBox()
        self.themes = self.config["DISPLAY"].get("THEMES", [])
        current_theme = self.config["DISPLAY"].get("current_theme", "")
        for theme in self.themes:
            self.theme_dropdown.addItem(theme["name"])
        index = self.theme_dropdown.findText(current_theme)
        if index >= 0:
            self.theme_dropdown.setCurrentIndex(index)
        scroll_layout.addRow(QLabel("Select Theme"), self.theme_dropdown)
        self.theme_dropdown.currentTextChanged.connect(self.apply_theme_immediately)  

        #* Debug checkbox
        self.debug_checkbox = QCheckBox("Enable developer mode (NOT RECOMMENDED)")
        self.debug_checkbox.setChecked(self.config["GLOBALS"].get("DEVMODE", False))
        scroll_layout.addRow(self.debug_checkbox)

        #* Reset Pet Button
        pet_resetbtn = QPushButton("Reset Pet")
        pet_resetbtn.clicked.connect(self.reset_pet)
        scroll_layout.addRow(pet_resetbtn)

        #* Apply/Reset buttons
        button_layout = QHBoxLayout()
        appbtn = QPushButton("Apply Changes")
        appbtn.clicked.connect(self.apply_changes)
        button_layout.addWidget(appbtn)

        rstbtn = QPushButton("Reset to Default")
        rstbtn.clicked.connect(self.reset_changes)
        button_layout.addWidget(rstbtn)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        scroll_layout.addRow(button_widget)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)

        outer_layout = QVBoxLayout()
        outer_layout.addWidget(scroll_area)
        self.setLayout(outer_layout)

    #* Live-updating width ratio
    def update_width_ratio(self, value):
        try:
            val = int(value)
            if 20 <= val <= 100:
                self.config["DISPLAY"]["width_ratio"] = val / 100.0
        except ValueError:
            pass

    #* Live-updating height ratio
    def update_height_ratio(self, value):
        try:
            val = int(value)
            if 20 <= val <= 100:
                self.config["DISPLAY"]["height_ratio"] = val / 100.0
        except ValueError:
            pass
    def update_refreshrate(self, value):
        try:
                val = int(value)
                if 1 <= val <= 300:  
                        self.config["GLOBALS"]["refreshrate"] = val
        except ValueError:
                pass 
    #* Apply button logic
    def apply_changes(self):
        self.config["DISPLAY"]["current_theme"] = self.theme_dropdown.currentText()
        self.config["GLOBALS"]["DEVMODE"] = self.debug_checkbox.isChecked()
        self.config["GLOBALS"]["WAKA_API_KEY"] = self.api_key_input.text().strip()
        self.config["GLOBALS"]["refreshrate"] = self.refreshrate.text()
        save_config(self.config)
        self.apply_theme_immediately()

        if self.config.get("GLOBALS", {}).get("DEVMODE", False):
            print("[DEVMODE] Applied config values:")
            print(f" - Width:  {self.config['DISPLAY'].get('width_ratio', 0)}")
            print(f" - refresh rate: {self.config['GLOBALS'].get('refreshrate', 0)}")

            print(f" - Height: {self.config['DISPLAY'].get('height_ratio', 0)}")
            print(f" - Theme:  {self.config['DISPLAY'].get('current_theme', '')}")
            print(f" - DevMode: {self.config['GLOBALS'].get('DEVMODE', False)}")
            print(f" - api.key_input: {self.config['GLOBALS'].get('WAKA_API_KEY', '')}")
    #* Reset button logic
    def reset_changes(self):
        defaults = get_default_config()
        display = defaults["DISPLAY"]
        globals_ = defaults["GLOBALS"]

        self.width_input.setText(str(int(display["width_ratio"] * 100)))
        self.height_input.setText(str(int(display["height_ratio"] * 100)))
        index = self.theme_dropdown.findText(display["current_theme"])
        if index >= 0:
            self.theme_dropdown.setCurrentIndex(index)
        self.debug_checkbox.setChecked(globals_["DEVMODE"])

        self.config["DISPLAY"].update(display)
        self.config["GLOBALS"].update(globals_)

        save_config(self.config)
        self.apply_theme_immediately()

        if self.config["GLOBALS"].get("DEVMODE", False):
            print("[DEVMODE] Reset to default config.")

    #* Pet reset logic w/ confirmation
    def reset_pet(self):
        config = load_config()
        border_style = "QMessageBox { border: 2px solid #444; border-radius: 8px; background-color: #fff; }"
        
        if "GAME" in config and "active-pet" in config["GAME"]:
            confirm = QMessageBox(self)
            confirm.setWindowTitle("Reset Pet")
            confirm.setText("Are you sure you want to delete your pet?")
            confirm.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            confirm.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
            confirm.setStyleSheet(border_style)
            confirm.setModal(True)
            confirm.move(self.geometry().center() - confirm.rect().center())
            result = confirm.exec_()

            if result == QMessageBox.Yes:
                del config["GAME"]["active-pet"]
                save_config(config)
                debug_log("Pet reset from settings page.")

                info = QMessageBox(self)
                info.setWindowTitle("Pet Reset")
                info.setText("Your pet has been deleted.")
                info.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
                info.setStyleSheet(border_style)
                info.setModal(True)
                info.exec_()

                self.petReset.emit()  # reload pet page
        else:
            info = QMessageBox(self)
            info.setWindowTitle("No Pet")
            info.setText("There is no pet to reset.")
            info.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
            info.setStyleSheet(border_style)
            info.setModal(True)
            info.exec_()

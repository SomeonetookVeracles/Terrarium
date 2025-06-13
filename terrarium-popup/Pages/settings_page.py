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

        #* Width ratio input
        self.width_input = QLineEdit()
        self.width_input.setText(str(int(self.config["DISPLAY"].get("width_ratio", 0.8) * 100)))
        self.width_input.textChanged.connect(self.update_width_ratio)
        scroll_layout.addRow(QLabel("Width Ratio (%)"), self.width_input)

        #* Height ratio input
        self.height_input = QLineEdit()
        self.height_input.setText(str(int(self.config["DISPLAY"].get("height_ratio", 0.8) * 100)))
        self.height_input.textChanged.connect(self.update_height_ratio)
        scroll_layout.addRow(QLabel("Height Ratio (%)"), self.height_input)

        #* Theme dropdown
        self.theme_dropdown = QComboBox()
        all_themes = self.config.get("DISPLAY", {}).get("THEMES", [])
        for theme in all_themes:
            self.theme_dropdown.addItem(theme["name"])

        index = self.theme_dropdown.findText(self.config["DISPLAY"].get("current_theme", "fluent-Dark"))
        if index >= 0:
            self.theme_dropdown.setCurrentIndex(index)
        scroll_layout.addRow(QLabel("Select Theme"), self.theme_dropdown)
        self.theme_dropdown.currentTextChanged.connect(self.apply_theme_immediately)  

        #* Debug checkbox
        self.debug_checkbox = QCheckBox("Enable developer mode (NOT RECOMMENDED)")
        self.debug_checkbox.setChecked(self.config["GLOBALS"].get("DEVMODE", False))
        scroll_layout.addRow(self.debug_checkbox)

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

    #* Apply button logic
    def apply_changes(self):
        self.config["DISPLAY"]["current_theme"] = self.theme_dropdown.currentText()
        self.config["GLOBALS"]["DEVMODE"] = self.debug_checkbox.isChecked()
        save_config(self.config)
        self.apply_theme_immediately()

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


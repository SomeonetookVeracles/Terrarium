from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QFormLayout, QComboBox, QCheckBox,
    QPushButton, QVBoxLayout, QScrollArea, QHBoxLayout, QApplication
)
from PyQt5.QtCore import Qt
from config_helper import load_config, save_config, get_default_config
import json #! Keep this

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.init_ui()
    def apply_theme_immediately(self):
        current_theme_name = self.theme_dropdown.currentText()
        all_themes = self.config.get("DISPLAY", {}).get("THEMES", [])

        #fallback
        fallback = "QWidget { background-color: white; }"

        # Find theme by name
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
    def init_ui(self):
        self.setObjectName("settings-page")

        #* Scroll Area Setup
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QFormLayout()
        scroll_layout.setSpacing(12)
        #* - Helper method to apply themes
        
        #* - Width Ratio Input
        #TODO - Add guardrails so you can't put in absurd sizes
        self.width_input = QLineEdit(str(int(self.config["DISPLAY"].get("width_ratio", 0.5) * 100)))
        self.width_input.setPlaceholderText("Default: 33%")
        self.width_input.textChanged.connect(self.update_width_ratio)
        scroll_layout.addRow(QLabel("% width of screen"), self.width_input)

        #* - Height Ratio Input
        #TODO - Add Guardrails so you can't put in absurd sizes
        self.height_input = QLineEdit(str(int(self.config["DISPLAY"].get("height_ratio", 0.5) * 100)))
        self.height_input.setPlaceholderText("Default: 50%")
        self.height_input.textChanged.connect(self.update_height_ratio)
        scroll_layout.addRow(QLabel("% height of screen"), self.height_input)

        #* - Theme Dropdown
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

        #* - Debug Checkbox
        #TODO - Set visual indicator for debug mode
        self.debug_checkbox = QCheckBox("Enable developer mode (NOT RECOMMENDED)")
        self.debug_checkbox.setChecked(self.config["GLOBALS"].get("DEVMODE", False))
        scroll_layout.addRow(self.debug_checkbox)

        #* - Spacer + Apply/Reset Buttons
        button_layout = QHBoxLayout()

        #Applybutton - Saves all UI changes to config
        #TODO - Make it so the icon greys out if not applicable
        appbtn = QPushButton("Apply Changes")
        appbtn.clicked.connect(self.apply_changes)
        button_layout.addWidget(appbtn)

        #Resetbutton - Reverts values back to original config
        #TODO - Make it so the icon greys out if not applicable
        rstbtn = QPushButton("Reset to Default")
        rstbtn.clicked.connect(self.reset_changes)
        button_layout.addWidget(rstbtn)

        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        scroll_layout.addRow(button_widget)  # or use addWidget(button_widget)

        #Finalize Scroll Area
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)

        #Outer Layout
        outer_layout = QVBoxLayout()
        outer_layout.addWidget(scroll_area)
        self.setLayout(outer_layout)

    #* - Live-updating width ratio
    def update_width_ratio(self, value):
        try:
            val = int(value)
            if 20 <= val <= 100:
                self.config["DISPLAY"]["width_ratio"] = val / 100.0
        except ValueError:
            pass #Ignore input #TODO - Add "invalid" notification in UI
    #* - Live-updating height ratio
    def update_height_ratio(self, value):
        try:
            val = int(value)
            if 20 <= val <=100:
                self.config["DISPLAY"]["height_ratio"] = val / 100.0
        except ValueError:
            pass 
    #* - Logic for apply button
    def apply_changes(self):
        #Update remaining fields manually
        self.config["DISPLAY"]["current_theme"] = self.theme_dropdown.currentText()
        self.config["GLOBALS"]["DEVMODE"] = self.debug_checkbox.isChecked()
        save_config(self.config)
        if self.config.get("GLOBALS", {}).get("DEVMODE", False):
            print("[DEVMODE] Applied config values:")
            print(f" - Width:  {self.config['DISPLAY'].get('width_ratio', 0)}")
            print(f" - Height: {self.config['DISPLAY'].get('height_ratio', 0)}")
            print(f" - Theme:  {self.config['DISPLAY'].get('current_theme', '')}")
            print(f" - DevMode: {self.config['GLOBALS'].get('DEVMODE', False)}")
        self.config["DISPLAY"]["current_theme"] = self.theme_dropdown.currentText()
        self.apply_theme_immediately()
    #* - Logic for reset button
    def reset_changes(self):
        defaults = get_default_config()

        #Pull from default config
        display = defaults["DISPLAY"]
        globals_ = defaults["GLOBALS"]

        #Reset UI fields
        self.width_input.setText(str(int(display["width_ratio"] * 100)))
        self.height_input.setText(str(int(display["height_ratio"] * 100)))
        index = self.theme_dropdown.setCurrentIndex(display["current_theme"])
        if index >= 0:
            self.theme_dropdown.setCurrentIndex(index)
        self.debug_checkbox.setChecked(globals_["DEVMODE"])

        #Update current working config
        self.config["DISPLAY"].update(display)
        self.config["GLOBALS"].update(globals_)

        #Save and reapply -- Live updating
        save_config(self.config)
        self.apply_theme_immediately() 
        
        if self.config["GLOBALS"].get("DEVMODE", False):
            print("[DEVMODE] Reset to default config.")
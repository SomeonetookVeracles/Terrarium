from PyQt5.QtWidgets import (
    QWidget, QLabel, QSlider, QFormLayout, QComboBox
)
from PyQt5.QtCore import Qt
from config_helper import load_config, save_config


class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.init_ui()

    def init_ui(self):
        self.setObjectName("settings-page")
        layout = QFormLayout()
        layout.setSpacing(12)

        # Width Ratio
        width_label = QLabel("Width % of screen")
        width_label.setObjectName("settings-label")
        layout.addWidget(width_label)

        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setObjectName("settings-slider")
        self.width_slider.setRange(10, 100)
        self.width_slider.setValue(int(self.config["DISPLAY"].get("width_ratio", 0.8) * 100))
        self.width_slider.valueChanged.connect(self.update_WR)
        layout.addWidget(self.width_slider)

        # Height Ratio
        height_label = QLabel("Height % of screen")
        height_label.setObjectName("settings-label")
        layout.addWidget(height_label)

        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setObjectName("settings-slider")
        self.height_slider.setRange(10, 100)
        self.height_slider.setValue(int(self.config["DISPLAY"].get("height_ratio", 0.8) * 100))
        self.height_slider.valueChanged.connect(self.update_HR)
        layout.addWidget(self.height_slider)

        # Theme selection dropdown
        theme_label = QLabel("Select Theme")
        theme_label.setObjectName("settings-label")
        layout.addWidget(theme_label)

        self.theme_dropdown = QComboBox()
        self.theme_dropdown.setObjectName("settings-dropdown")  # ✅ Fix here
        themes = self.config["DISPLAY"].get("THEMES", [])
        current_theme = self.config["DISPLAY"].get("current_theme", "")

        for theme in themes:
            self.theme_dropdown.addItem(theme["name"])

        index = self.theme_dropdown.findText(current_theme)
        if index >= 0:
            self.theme_dropdown.setCurrentIndex(index)

        self.theme_dropdown.currentTextChanged.connect(self.update_theme)
        layout.addWidget(self.theme_dropdown)

        # ✅ Set layout to make it visible
        self.setLayout(layout)

    def update_WR(self, value):
        self.config["DISPLAY"]["width_ratio"] = value / 100.0
        save_config(self.config)

    def update_HR(self, value):
        self.config["DISPLAY"]["height_ratio"] = value / 100.0
        save_config(self.config)  # ✅ Fix missing save

    def update_theme(self, theme_name):
        self.config["DISPLAY"]["current_theme"] = theme_name
        save_config(self.config)
        print(f"Theme changed to: {theme_name}")

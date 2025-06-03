from PyQt5.QtWidgets import (
    QWidget, QLabel, QCheckBox, QSlider, QFormLayout, QSizePolicy
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

        # Dark mode checkbox
        self.dark_checkbox = QCheckBox("Enable Dark Mode")
        self.dark_checkbox.setObjectName("settings-checkbox")
        self.dark_checkbox.setChecked(self.config["DISPLAY"].get("DARKMODE", False))
        self.dark_checkbox.stateChanged.connect(self.toggle_DM)
        layout.addWidget(self.dark_checkbox)

        # Width Ratio
        width_label = QLabel("Width % of screen")
        width_label.setObjectName("settings-label")
        layout.addWidget(width_label)

        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setObjectName("settings-slider")
        self.width_slider.setRange(10, 100)
        self.width_slider.setValue(int(self.config["DISPLAY"]["width_ratio"] * 100))
        self.width_slider.valueChanged.connect(self.update_WR)
        layout.addWidget(self.width_slider)

        # Height Ratio
        height_label = QLabel("Height % of screen")
        height_label.setObjectName("settings-label")
        layout.addWidget(height_label)

        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setObjectName("settings-slider")
        self.height_slider.setRange(10, 100)
        self.height_slider.setValue(int(self.config["DISPLAY"]["height_ratio"] * 100))
        self.height_slider.valueChanged.connect(self.update_HR)
        layout.addWidget(self.height_slider)

        self.setLayout(layout)

    def toggle_DM(self, state):
        self.config["DISPLAY"]["DARKMODE"] = bool(state)
        save_config(self.config)

    def update_WR(self, value):
        self.config["DISPLAY"]["width_ratio"] = value / 100.0
        save_config(self.config)

    def update_HR(self, value):
        self.config["DISPLAY"]["height_ratio"] = value / 100.0
        save_config(self.config)

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QLabel, QPushButton,
    QComboBox, QColorDialog, QLineEdit, QFormLayout, QHBoxLayout
)
from PyQt5.QtGui import QColor, QMovie
from PyQt5.QtCore import Qt
import os

from config_helper import load_config, save_config, debug_log
from Services.sprite_loader import generate_current_pet_gif  # Ensure this reads config internally


class PetPage(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.pet_type = None
        self.base_color = QColor("#FFFFFF")
        self.selected_pattern = None
        self.pet_addons = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        pet_data = self.config.get("GAME", {}).get("active-pet", None)
        if not pet_data:
            self.init_pet_creator()
        else:
            self.init_pet_status(pet_data)

    def init_pet_status(self, pet_data):
        status_screen = QWidget()
        layout = QVBoxLayout()
        status_screen.setLayout(layout)

        layout.addWidget(QLabel(f"Name: {pet_data.get('Name', 'Unnamed')}"))
        layout.addWidget(QLabel(f"Type: {pet_data.get('type', 'Unknown')}"))
        layout.addWidget(QLabel(f"Personality: {pet_data.get('persona', 'N/A')}"))

        movie = self.compose_pet_image(pet_data)
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)

        if movie:
            img_label.setMovie(movie)
            movie.start()
        else:
            img_label.setText("Image not found.")

        layout.addWidget(img_label, alignment=Qt.AlignCenter)

        self.stack.addWidget(status_screen)
        self.stack.setCurrentIndex(0)

    def init_pet_creator(self):
        # Page 1: Select type
        type_select = QWidget()
        layout1 = QVBoxLayout()
        type_select.setLayout(layout1)

        self.type_dropdown = QComboBox()
        pet_types = self.config.get("GAME", {}).get("pettypes", [])
        for pet in pet_types:
            self.type_dropdown.addItem(pet['name'])
        layout1.addWidget(QLabel("Select creature type:"))
        layout1.addWidget(self.type_dropdown)

        next_btn1 = QPushButton("Next")
        next_btn1.clicked.connect(self.go_to_appearance_page)
        layout1.addWidget(next_btn1)

        # Page 2: Appearance customization
        appearance = QWidget()
        layout2 = QVBoxLayout()
        appearance.setLayout(layout2)

        row_layout = QHBoxLayout()

        self.color_picker_btn = QPushButton("Pick Base Color")
        self.color_picker_btn.clicked.connect(self.pick_color)
        row_layout.addWidget(self.color_picker_btn)

        self.pattern_dropdown = QComboBox()
        self.pattern_dropdown.addItem("None")  # Default
        self.pattern_dropdown.currentIndexChanged.connect(self.render_pet_preview)
        row_layout.addWidget(self.pattern_dropdown)

        layout2.addLayout(row_layout)

        self.appearance_preview = QLabel("Preview will appear here")
        self.appearance_preview.setAlignment(Qt.AlignCenter)
        layout2.addWidget(self.appearance_preview)

        layout2.addStretch()

        next_btn2 = QPushButton("Next")
        next_btn2.clicked.connect(self.go_to_naming_page)
        layout2.addWidget(next_btn2, alignment=Qt.AlignRight)

        # Page 3: Name and personality
        name_screen = QWidget()
        form = QFormLayout()
        name_screen.setLayout(form)

        self.name_input = QLineEdit()
        self.persona_input = QComboBox()
        for persona in self.config.get("GAME", {}).get("personatypes", []):
            self.persona_input.addItem(persona["name"])

        form.addRow(QLabel("Pet Name:"), self.name_input)
        form.addRow(QLabel("Personality:"), self.persona_input)

        finish_btn = QPushButton("Finish")
        finish_btn.clicked.connect(self.finish_creation)
        form.addRow(finish_btn)

        # Add pages to stack
        self.stack.addWidget(type_select)   # 0
        self.stack.addWidget(appearance)    # 1
        self.stack.addWidget(name_screen)   # 2
        self.stack.setCurrentIndex(0)

    def go_to_appearance_page(self):
        self.pet_type = self.type_dropdown.currentText()
        self.update_pattern_list()
        self.render_pet_preview()
        self.stack.setCurrentIndex(1)

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.base_color = color
            self.color_picker_btn.setText(f"Color: {color.name()}")
            self.render_pet_preview()

    def go_to_naming_page(self):
        choice = self.pattern_dropdown.currentText()
        self.selected_pattern = None if choice == "None" else choice
        self.stack.setCurrentIndex(2)

    def finish_creation(self):
        pet_data = {
            "type": self.pet_type,
            "base_color": self.base_color.name(),
            "pattern": self.selected_pattern,
            "Name": self.name_input.text().strip() or "Unnamed",
            "persona": self.persona_input.currentText().strip()
        }

        self.config.setdefault("GAME", {})["active-pet"] = pet_data
        save_config(self.config)
        debug_log("Pet saved:", pet_data)

        generate_current_pet_gif()

        preview_screen = self.create_pet_preview(pet_data)
        self.stack.addWidget(preview_screen)
        self.stack.setCurrentIndex(self.stack.count() - 1)

    def create_pet_preview(self, pet_data):
        preview_widget = QWidget()
        layout = QVBoxLayout()
        preview_widget.setLayout(layout)

        layout.addWidget(QLabel(f"{pet_data['Name']}, the {pet_data['type']}"))

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)

        movie = self.compose_pet_image(pet_data)
        if movie:
            image_label.setMovie(movie)
            movie.start()
        else:
            image_label.setText("Image not found.")

        layout.addWidget(image_label)
        return preview_widget

    def compose_pet_image(self, pet_data):
        try:
            gif_path = os.path.join("Visuals", "currentPet.gif")
            if os.path.exists(gif_path):
                return QMovie(gif_path)
            debug_log("currentPet.gif not found.")
            return None
        except Exception as e:
            debug_log("Error loading pet image:", str(e))
            return None

    def update_pattern_list(self):
        self.pattern_dropdown.clear()
        self.pattern_dropdown.addItem("None")

        pettypes = self.config.get("GAME", {}).get("pettypes", [])
        pet_entry = next((p for p in pettypes if p["name"] == self.pet_type), None)

        if not pet_entry:
            debug_log(f"Pet type '{self.pet_type}' not found in config.")
            return

        sprite_path = pet_entry.get("sprite_path") or pet_entry.get("path")
        if not sprite_path:
            debug_log(f"No sprite_path or path set for pet type '{self.pet_type}'.")
            return

        pattern_dir = os.path.join(sprite_path, "patterns")

        if not os.path.isdir(pattern_dir):
            debug_log(f"Pattern directory not found: {pattern_dir}")
            return

        try:
            patterns = [f for f in os.listdir(pattern_dir)
                        if f.lower().endswith((".png", ".jpg", ".jpeg"))]
            debug_log(f"Found patterns: {patterns}")
            for pattern_file in patterns:
                self.pattern_dropdown.addItem(pattern_file)
        except Exception as e:
            debug_log("Error reading pattern directory:", str(e))

    def render_pet_preview(self):
        pet_data = {
            "type": self.type_dropdown.currentText(),
            "base_color": self.base_color.name(),
            "pattern": self.pattern_dropdown.currentText() if self.pattern_dropdown.currentText() != "None" else None,
            "Name": "Preview",
            "persona": "N/A"
        }

        self.config.setdefault("GAME", {})["active-pet"] = pet_data
        save_config(self.config)

        try:
            generate_current_pet_gif()
            gif_path = os.path.join("Visuals", "currentPet.gif")
            if os.path.exists(gif_path):
                movie = QMovie(gif_path)
                self.appearance_preview.setMovie(movie)
                movie.start()
            else:
                self.appearance_preview.setText("Preview image not found.")
        except Exception as e:
            self.appearance_preview.setText(f"Preview error: {str(e)}")

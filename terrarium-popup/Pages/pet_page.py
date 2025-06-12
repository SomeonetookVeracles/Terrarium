from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QLabel, QPushButton,
    QComboBox, QColorDialog, QLineEdit, QFormLayout, QHBoxLayout,
    QGroupBox
)
from PyQt5.QtGui import QColor, QMovie
from PyQt5.QtCore import Qt, QSize
import os

from config_helper import load_config, save_config, debug_log
from Services.sprite_loader import generate_current_pet_gif  # Ensure this reads config internally


class PetPage(QWidget):
    """
    PetPage manages pet creation and status viewing with a stacked layout:
    - Pet status display
    - Pet creation steps: type selection, appearance customization, naming
    The pet preview GIF is scaled up by 2x for better visibility.
    """

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

    def reset_pet(self):
        """Clear the active pet from config and reset UI to pet creator."""
        if "active-pet" in self.config.get("GAME", {}):
            del self.config["GAME"]["active-pet"]
            save_config(self.config)
            debug_log("Pet reset: active-pet removed from config.")
        # Remove all widgets from stack and delete them
        while self.stack.count() > 0:
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()
        self.init_pet_creator()

    def init_pet_status(self, pet_data):
        status_screen = QWidget()
        layout = QVBoxLayout()
        status_screen.setLayout(layout)

        # Group box to fold labels neatly
        info_box = QGroupBox("Pet Information")
        info_layout = QVBoxLayout()
        info_box.setLayout(info_layout)

        info_layout.addWidget(QLabel(f"Name: {pet_data.get('Name', 'Unnamed')}"))
        info_layout.addWidget(QLabel(f"Type: {pet_data.get('type', 'Unknown')}"))
        info_layout.addWidget(QLabel(f"Personality: {pet_data.get('persona', 'N/A')}"))

        layout.addWidget(info_box, alignment=Qt.AlignTop)

        movie = self.compose_pet_image(pet_data)
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)

        if movie:
            img_label.setMovie(movie)
            movie.start()
        else:
            img_label.setText("Image not found.")

        layout.addWidget(img_label, alignment=Qt.AlignTop)

        # Optional: add a Reset Pet button here to allow reset
        reset_btn = QPushButton("Reset Pet")
        reset_btn.clicked.connect(self.reset_pet)
        layout.addWidget(reset_btn, alignment=Qt.AlignCenter)

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

        # Preview label
        self.appearance_preview = QLabel("Preview will appear here")
        self.appearance_preview.setAlignment(Qt.AlignCenter)
        layout2.addWidget(self.appearance_preview)

        # Controls at bottom: Color picker and pattern dropdown side-by-side
        controls_layout = QHBoxLayout()

        self.color_picker_btn = QPushButton("Pick Base Color")
        self.color_picker_btn.clicked.connect(self.pick_color)
        controls_layout.addWidget(self.color_picker_btn)

        self.pattern_dropdown = QComboBox()
        self.pattern_dropdown.addItem("None")  # Default
        self.pattern_dropdown.currentIndexChanged.connect(self.render_pet_preview)
        controls_layout.addWidget(self.pattern_dropdown)

        layout2.addLayout(controls_layout)

        # Navigation buttons row below controls
        nav_buttons_layout = QHBoxLayout()
        back_btn2 = QPushButton("Back")
        next_btn2 = QPushButton("Next")
        back_btn2.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        next_btn2.clicked.connect(self.go_to_naming_page)
        nav_buttons_layout.addWidget(back_btn2)
        nav_buttons_layout.addStretch()
        nav_buttons_layout.addWidget(next_btn2)

        layout2.addLayout(nav_buttons_layout)

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

        btn_row3 = QHBoxLayout()
        back_btn3 = QPushButton("Back")
        finish_btn = QPushButton("Finish")

        back_btn3.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        finish_btn.clicked.connect(self.finish_creation)

        btn_row3.addWidget(back_btn3)
        btn_row3.addStretch()
        btn_row3.addWidget(finish_btn)

        form.addRow(btn_row3)

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
        # Build new pet data
        pet_data = {
            "type": self.pet_type,
            "base_color": self.base_color.name(),
            "pattern": self.selected_pattern,
            "Name": self.name_input.text().strip() or "Unnamed",
            "persona": self.persona_input.currentText().strip()
        }

        # Reset existing pet data before saving new pet
        if "active-pet" in self.config.get("GAME", {}):
            del self.config["GAME"]["active-pet"]

        self.config.setdefault("GAME", {})["active-pet"] = pet_data
        save_config(self.config)
        debug_log("Pet saved:", pet_data)

        generate_current_pet_gif()

        # Remove old preview/status widgets to avoid stack buildup
        while self.stack.count() > 0:
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()

        preview_screen = self.create_pet_preview(pet_data)
        self.stack.addWidget(preview_screen)
        self.stack.setCurrentIndex(0)

    def create_pet_preview(self, pet_data):
        preview_widget = QWidget()
        layout = QVBoxLayout()
        preview_widget.setLayout(layout)

        info_box = QGroupBox("Pet Summary")
        info_layout = QVBoxLayout()
        info_box.setLayout(info_layout)

        info_layout.addWidget(QLabel(f"Name: {pet_data['Name']}"))
        info_layout.addWidget(QLabel(f"Type: {pet_data['type']}"))
        info_layout.addWidget(QLabel(f"Personality: {pet_data['persona']}"))

        layout.addWidget(info_box, alignment=Qt.AlignTop)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)

        movie = self.compose_pet_image(pet_data)
        if movie:
            image_label.setMovie(movie)
            movie.start()
        else:
            image_label.setText("Image not found.")

        layout.addWidget(image_label, alignment=Qt.AlignTop)
        return preview_widget

    def compose_pet_image(self, pet_data):
        try:
            gif_path = os.path.join("Visuals", "currentPet.gif")
            if os.path.exists(gif_path):
                movie = QMovie(gif_path)
                # Scale movie 2x
                movie.setScaledSize(QSize(64, 64) * 2)
                return movie
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
                movie.setScaledSize(QSize(64, 64) * 2)  # scale preview 2x here too
                self.appearance_preview.setMovie(movie)
                movie.start()
            else:
                self.appearance_preview.setText("Preview image not found.")
        except Exception as e:
            self.appearance_preview.setText(f"Preview error: {str(e)}")

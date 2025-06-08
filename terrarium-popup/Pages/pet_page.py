from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QLabel, QPushButton,
    QComboBox, QFileDialog, QLineEdit, QFormLayout, QColorDialog, QHBoxLayout
)
from PyQt5.QtGui import QColor, QPixmap, QPainter, QImage
from PyQt5.QtCore import Qt
import os
from config_helper import load_config, save_config, debug_log

class PetPage(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # init stack for multiple layered screens
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Check if a pet already exists
        pet_data = self.config.get("GAME", {}).get("active-pet", False)
        if not pet_data:
            self.init_pet_creator()
        else:
            self.init_pet_status(pet_data)

    def init_pet_status(self, pet_data):
        """If pet already exists, show status summary."""
        status_screen = QWidget()
        layout = QVBoxLayout()
        status_screen.setLayout(layout)

        # Header
        layout.addWidget(QLabel(f"Name: {pet_data.get('Name', 'Unnamed')}"))
        layout.addWidget(QLabel(f"Type: {pet_data.get('type', 'Unknown')}"))
        layout.addWidget(QLabel(f"Personality: {pet_data.get('persona', 'N/A')}"))

        # Render composed image preview
        image = self.compose_pet_image(pet_data)
        if image:
            img_label = QLabel()
            img_label.setPixmap(QPixmap.fromImage(image).scaled(200, 200, Qt.KeepAspectRatio))
            layout.addWidget(img_label, alignment=Qt.AlignCenter)

        # TODO: Add buttons like "Edit Pet", "Delete", etc.
        self.stack.addWidget(status_screen)
        self.stack.setCurrentIndex(0)

    def init_pet_creator(self):
        """Multi-step creator wizard — type -> appearance -> naming."""
        # Page 1: Choose pet type
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

        # Page 2: Customize appearance (color + pattern)
        appearance = QWidget()
        layout2 = QVBoxLayout()
        appearance.setLayout(layout2)

        row_layout = QHBoxLayout()
        self.color_picker_btn = QPushButton("Pick Base Color")
        self.color_picker_btn.clicked.connect(self.pick_color)
        row_layout.addWidget(self.color_picker_btn)

        self.pattern_dropdown = QComboBox()
        self.pattern_dropdown.addItem("None")  # Allow blank pattern
        for fname in os.listdir("Visuals/patterns"):
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                self.pattern_dropdown.addItem(fname)
        row_layout.addWidget(self.pattern_dropdown)

        layout2.addStretch()  # Push row to bottom
        layout2.addLayout(row_layout)

        next_btn2 = QPushButton("Next")
        next_btn2.clicked.connect(self.go_to_naming_page)
        layout2.addWidget(next_btn2, alignment=Qt.AlignRight)

        # Page 3: Name and personality
        name_screen = QWidget()
        form = QFormLayout()
        name_screen.setLayout(form)

        self.name_input = QLineEdit()
        self.persona_input = QComboBox()
        personatypes = self.config.get("GAME", {}).get("personatypes", [])
        for persona in personatypes:
            self.persona_input.addItem(persona["name"])

        form.addRow(QLabel("Pet Name:"), self.name_input)
        form.addRow(QLabel("Personality:"), self.persona_input)

        finish_btn = QPushButton("Finish")
        finish_btn.clicked.connect(self.finish_creation)
        form.addRow(finish_btn)

        # Add pages to the stacked layout
        self.stack.addWidget(type_select)    # 0
        self.stack.addWidget(appearance)     # 1
        self.stack.addWidget(name_screen)    # 2
        self.stack.setCurrentIndex(0)

        # Internal state
        self.base_color = QColor("#FFFFFF")
        self.selected_pattern = None

    def go_to_appearance_page(self):
        self.pet_type = self.type_dropdown.currentText()
        self.stack.setCurrentIndex(1)

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.base_color = color
            self.color_picker_btn.setText(f"Color: {color.name()}")

    def go_to_naming_page(self):
        choice = self.pattern_dropdown.currentText()
        self.selected_pattern = None if choice == "None" else choice
        self.stack.setCurrentIndex(2)

    def finish_creation(self):
        pet_data = {
            "type": self.pet_type,
            "base_color": self.base_color.name(),
            "pattern": self.selected_pattern,
            "Name": self.name_input.text().strip(),
            "persona": self.persona_input.currentText().strip()
        }

        # Save to config
        self.config.setdefault("GAME", {})["active-pet"] = pet_data
        save_config(self.config)
        debug_log("Pet saved:", pet_data)

        # Show preview
        preview_screen = self.create_pet_preview(pet_data)
        self.stack.addWidget(preview_screen)
        self.stack.setCurrentIndex(3)

    def create_pet_preview(self, pet_data):
        """Generates the preview screen showing the composed sprite."""
        preview_widget = QWidget()
        layout = QVBoxLayout()
        preview_widget.setLayout(layout)

        layout.addWidget(QLabel(f"{pet_data['Name']} the {pet_data['type']}"))

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)

        final_image = self.compose_pet_image(pet_data)
        if final_image:
            image_label.setPixmap(QPixmap.fromImage(final_image).scaled(200, 200, Qt.KeepAspectRatio))
        else:
            image_label.setText("Image not found.")

        layout.addWidget(image_label)

        return preview_widget

    def compose_pet_image(self, pet_data):
        """Combines base sprite + color overlay + optional pattern."""
        try:
            pet_type = pet_data["type"]
            base_color = QColor(pet_data["base_color"])
            pattern = pet_data.get("pattern")

            base_path = os.path.join("Visuals", "Sprites", pet_type, "base.png")
            if not os.path.exists(base_path):
                debug_log(f"Missing base sprite: {base_path}")
                return None

            base_image = QImage(base_path)
            color_overlay = QImage(base_image.size(), QImage.Format_ARGB32)
            color_overlay.fill(base_color)

            result = QImage(base_image.size(), QImage.Format_ARGB32)
            painter = QPainter(result)

            # Start with base
            painter.setCompositionMode(QPainter.CompositionMode_Source)
            painter.drawImage(0, 0, base_image)

            # Apply base color
            painter.setCompositionMode(QPainter.CompositionMode_Multiply)
            painter.drawImage(0, 0, color_overlay)

            # Optional pattern
            if pattern:
                pattern_path = os.path.join("Visuals", "Sprites", pet_type, pattern)
                if os.path.exists(pattern_path):
                    pattern_image = QImage(pattern_path)
                    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                    painter.drawImage(0, 0, pattern_image)

            painter.end()
            return result

        except Exception as e:
            debug_log("Error composing image:", str(e))
            return None

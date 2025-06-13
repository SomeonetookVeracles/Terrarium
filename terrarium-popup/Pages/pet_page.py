from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QLabel, QPushButton,
    QComboBox, QColorDialog, QLineEdit, QFormLayout, QHBoxLayout,
    QGroupBox
)
from PyQt5.QtGui import QColor, QMovie
from PyQt5.QtCore import Qt, QSize
import os
from PIL import Image, ImageSequence

from config_helper import load_config, save_config, debug_log
from Services.sprite_loader import generate_current_pet_gif


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

    def reset_pet(self):
        if "active-pet" in self.config.get("GAME", {}):
            del self.config["GAME"]["active-pet"]
            save_config(self.config)
            debug_log("Pet reset: active-pet removed from config.")
        while self.stack.count() > 0:
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()
        self.init_pet_creator()

    def init_pet_status(self, pet_data):
        status_screen = QWidget()
        layout = QVBoxLayout()
        status_screen.setLayout(layout)

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

        reset_btn = QPushButton("Reset Pet")
        reset_btn.clicked.connect(self.reset_pet)
        layout.addWidget(reset_btn, alignment=Qt.AlignCenter)

        self.stack.addWidget(status_screen)
        self.stack.setCurrentIndex(0)

    def init_pet_creator(self):
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
        appearance = QWidget()
        layout2 = QVBoxLayout()
        appearance.setLayout(layout2)
        self.appearance_preview = QLabel("Preview will appear here")
        self.appearance_preview.setAlignment(Qt.AlignCenter)
        layout2.addWidget(self.appearance_preview)
        controls_layout = QHBoxLayout()
        self.color_picker_btn = QPushButton("Pick Base Color")
        self.color_picker_btn.clicked.connect(self.pick_color)
        controls_layout.addWidget(self.color_picker_btn)
        self.pattern_dropdown = QComboBox()
        self.pattern_dropdown.addItem("None")
        self.pattern_dropdown.currentIndexChanged.connect(self.render_pet_preview)
        controls_layout.addWidget(self.pattern_dropdown)
        layout2.addLayout(controls_layout)
        nav_buttons_layout = QHBoxLayout()
        back_btn2 = QPushButton("Back")
        next_btn2 = QPushButton("Next")
        back_btn2.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        next_btn2.clicked.connect(self.go_to_naming_page)
        nav_buttons_layout.addWidget(back_btn2)
        nav_buttons_layout.addStretch()
        nav_buttons_layout.addWidget(next_btn2)
        layout2.addLayout(nav_buttons_layout)
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
        self.stack.addWidget(type_select)   # 0
        self.stack.addWidget(appearance)    # 1
        self.stack.addWidget(name_screen)   # 2
        self.stack.setCurrentIndex(0)
    def go_to_appearance_page(self):
        try:
            self.pet_type = self.type_dropdown.currentText()
            self.update_pattern_list()
            self.render_pet_preview()
            self.stack.setCurrentIndex(1)
        except Exception as e:
            debug_log(f"Error transitioning to appearance page: {str(e)}", level="error")
            import traceback
            debug_log(traceback.format_exc(), level="error")
    def pick_color(self):
        try:
            color = QColorDialog.getColor()
            if color.isValid():
                self.base_color = color
                self.color_picker_btn.setText(f"Color: {color.name()}")
                self.render_pet_preview()
        except Exception as e:
            debug_log(f"Error picking color: {str(e)}", level="error")
            import traceback
            debug_log(traceback.format_exc(), level="error")
    def go_to_naming_page(self):
        choice = self.pattern_dropdown.currentText()
        self.selected_pattern = None if choice == "None" else choice
        self.stack.setCurrentIndex(2)
    def finish_creation(self):
        try:
            pet_data = {
                "type": self.pet_type,
                "base_color": self.base_color.name(),
                "pattern": self.selected_pattern,
                "Name": self.name_input.text().strip() or "Unnamed",
                "persona": self.persona_input.currentText().strip()
            }
            if "active-pet" in self.config.get("GAME", {}):
                del self.config["GAME"]["active-pet"]
            self.config.setdefault("GAME", {})["active-pet"] = pet_data
            save_config(self.config)
            debug_log("Pet saved:", pet_data)
            generate_current_pet_gif()
            while self.stack.count() > 0:
                widget = self.stack.widget(0)
                self.stack.removeWidget(widget)
                widget.deleteLater()
            preview_screen = self.create_pet_preview(pet_data)
            self.stack.addWidget(preview_screen)
            self.stack.setCurrentIndex(0)
            if hasattr(self.parent(), 'main_widget'):
                self.parent().main_widget.pet_updated.emit()
        except Exception as e:
            debug_log(f"Error finishing pet creation: {str(e)}", level="error")
            import traceback
            debug_log(traceback.format_exc(), level="error")
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
            image_label.setText("Image not found")

        layout.addWidget(image_label, alignment=Qt.AlignTop)
        return preview_widget

    def compose_pet_image(self, pet_data):
        """Compose the pet image from base sprite"""
        try:
            # Get and normalize pet type
            pet_type = pet_data.get('type', '').lower()
            if pet_type == "pet rock":
                pet_type = "rock"
            
            # Get base sprite path
            base_path = os.path.join("Visuals", "Sprites", pet_type, "Patterns", "Base.gif")
            if os.path.exists(base_path):
                movie = QMovie(base_path)
                # Scale movie 2x
                movie.setScaledSize(QSize(64, 64) * 2)
                return movie
            debug_log(f"Base sprite not found: {base_path}", level="error")
            return None
        except Exception as e:
            debug_log(f"Error loading pet image: {str(e)}", level="error")
            return None

    def update_pattern_list(self):
        """Update the pattern dropdown based on selected pet type"""
        try:
            self.pattern_dropdown.clear()
            self.pattern_dropdown.addItem("None")
            
            # Get pet type and normalize it
            pet_type = self.type_dropdown.currentText()
            normalized_type = pet_type.lower()
            if normalized_type == "pet rock":
                normalized_type = "rock"
            
            # Get patterns from directory
            pattern_dir = os.path.join("Visuals", "Sprites", normalized_type, "Patterns")
            if os.path.exists(pattern_dir):
                patterns = [f for f in os.listdir(pattern_dir) 
                           if f.lower().endswith(('.png', '.gif')) 
                           and f.lower() != 'base.gif']
                for pattern in patterns:
                    self.pattern_dropdown.addItem(pattern)
                debug_log(f"Updated pattern list for {pet_type}")
            else:
                debug_log(f"Pattern directory not found: {pattern_dir}", level="warning")
            
        except Exception as e:
            debug_log(f"Error updating pattern list: {str(e)}", level="error")
            import traceback
            debug_log(traceback.format_exc(), level="error")

    def render_pet_preview(self):
        """Render a preview of the pet with current settings"""
        try:
            # Get current pet type and normalize it
            pet_type = self.type_dropdown.currentText()
            normalized_type = pet_type.lower()
            if normalized_type == "pet rock":
                normalized_type = "rock"
            
            # Get base sprite path
            base_path = os.path.join("Visuals", "Sprites", normalized_type, "Patterns", "Base.gif")
            if not os.path.exists(base_path):
                debug_log(f"Base sprite not found: {base_path}", level="error")
                self.appearance_preview.setText("Preview not available")
                return
            
            # Load base sprite
            base_sprite = Image.open(base_path)
            frames = []
            
            # Process each frame
            for frame in ImageSequence.Iterator(base_sprite):
                # Convert frame to RGBA
                frame = frame.convert('RGBA')
                
                # Apply base color if specified
                if self.base_color:
                    # Convert hex color to RGB
                    color = tuple(int(self.base_color.name()[i:i+2], 16) for i in (1, 3, 5))
                    # Create a color overlay
                    overlay = Image.new('RGBA', frame.size, (*color, 128))
                    frame = Image.alpha_composite(frame, overlay)
                
                # Apply pattern if specified
                pattern = self.pattern_dropdown.currentText()
                if pattern and pattern.lower() != "none":
                    pattern_path = os.path.join("Visuals", "Sprites", normalized_type, "Patterns", pattern)
                    if os.path.exists(pattern_path):
                        pattern_sprite = Image.open(pattern_path)
                        if pattern_sprite.mode != 'RGBA':
                            pattern_sprite = pattern_sprite.convert('RGBA')
                        # Resize pattern to match base sprite
                        pattern_sprite = pattern_sprite.resize(frame.size, Image.Resampling.LANCZOS)
                        frame = Image.alpha_composite(frame, pattern_sprite)
                        debug_log(f"Applied pattern: {pattern}")
                    else:
                        debug_log(f"Pattern not found: {pattern_path}", level="warning")
                
                frames.append(frame)
            
            # Save preview GIF
            preview_path = os.path.join("Visuals", "currentPet.gif")
            if frames:
                frames[0].save(
                    preview_path,
                    save_all=True,
                    append_images=frames[1:],
                    duration=base_sprite.info.get('duration', 100),
                    loop=0,
                    disposal=2
                )
                
                # Display preview
                movie = QMovie(preview_path)
                movie.setScaledSize(QSize(64, 64) * 2)  # Scale preview 2x
                self.appearance_preview.setMovie(movie)
                movie.start()
                debug_log("Preview rendered successfully")
            else:
                debug_log("No frames generated for preview", level="error")
                self.appearance_preview.setText("Preview not available")
            
        except Exception as e:
            debug_log(f"Error rendering preview: {str(e)}", level="error")
            import traceback
            debug_log(traceback.format_exc(), level="error")
            self.appearance_preview.setText("Preview error")

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QLabel, QPushButton,
    QComboBox, QFileDialog, QLineEdit, QFormLayout
)
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
import os
from config_helper import load_config, save_config
#TODO: From PIL import Image #More advanced image editing (Low priority)

class PetPage(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        #   Check if there's an active pet
        pet_data = self.config.get("GAME", {}).get("active-pet", False)

        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        if not pet_data:
            #This means no data is saved, launches creator.
            self.init_pet_creator()
        else:
            #TODO: Create a pet status page (High Priority)
            self.stack.addWidget(QLabel("TODO: Current Pet Status"))

    def init_pet_creator(self):
        #* - P1, Pet type selection
        type_select = QWidget()
        layout1 = QVBoxLayout()
        type_select.setLayout(layout1)

        self.type_dropdown = QComboBox()
        pet_types = self.config.get("GAME", {}).get("pettypes", [])
        for pet in pet_types:
            self.type_dropdown.addItem(pet['name'])
        layout1.addWidget(QLabel("Select creature type:"))
        layout1.addWidget(self.type_dropdown)

        next_btn1 = QPushButton("Next") #TODO: Implement selection check (Medium Priority)
        next_btn1.clicked.connect(self.go_to_appearance_page)
        layout1.addWidget(next_btn1)

        #* - P2, Appearance customization
        appearance = QWidget()
        layout2 = QVBoxLayout()
        appearance.setLayout(layout2)

        self.color_picker_btn = QPushButton("Pick Base Color")
        self.color_picker_btn.clicked.connect(self.pick_color)
        layout2.addWidget(self.color_picker_btn)

        self.pattern_dropdown = QComboBox()
        self.pattern_dropdown.addItem("None") #TODO: Implement Pattern system. (Medium Priority)
        #TODO: Dynamically load patterns from file. (Medium Priority)
        for fname in os.listdir("Visuals/patterns"):
            if fname.lower().endswith((".png", ".jpg")):
                self.pattern_dropdown.addItem(fname)
        layout2.addWidget(QLabel("Choose Pattern:"))
        layout2.addWidget(self.pattern_dropdown)

        next_btn2 = QPushButton("Next") #TODO: Implement selection check (Medium Priority)
        next_btn2.clicked.connect(self.go_to_naming_page)
        layout2.addWidget(next_btn2)

        #* - P3, Name and Personality
        name_screen = QWidget()
        form = QFormLayout()
        name_screen.setLayout(form)

        self.name_input = QLineEdit()
        self.persona_input = QComboBox()
        personatypes = self.config.get("GAME", {}).get("personatypes", []) #TODO: Dynamically load from json
        for persona in personatypes:
            self.persona_input.addItem(persona["name"])
        form.addRow(QLabel("Pet Name:"), self.name_input)
        form.addRow(QLabel("Pet Personality:"), self.persona_input)

        finish_btn = QPushButton("Finish")
        finish_btn.clicked.connect(self.finish_creation)
        form.addRow(finish_btn)

        #Add all pages to stack
        self.stack.addWidget(type_select) # Index = 0
        self.stack.addWidget(appearance) # Index = 1
        self.stack.addWidget(name_screen) # Index = 2
        self.stack.setCurrentIndex(0)

        # State Variables
        self.base_color = QColor("#FFFFFF") # default coloring
        self.selected_pattern = None # Placeholder

    def go_to_appearance_page(self):
        selected_type = self.type_dropdown.currentText()
        self.pet_type = selected_type # Save selection
        self.stack.setCurrentIndex(1)

    def pick_color(self):
        from PyQt5.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            self.base_color = color
            self.color_picker_btn.setText(f"Color: {color.name()}")
    def go_to_naming_page(self):
        self.selected_pattern = self.pattern_dropdown.currentText()
        self.stack.setCurrentIndex(2)
    def finish_creation(self):
        pet_data = {
            "type": self.pet_type,
            "base_color": self.base_color.name(), #Stored as hex code
            "pattern": self.selected_pattern,
            "Name": self.name_input.text().strip(),
            "persona": self.persona_input.current_text().strip()
        }
        self.config.setdefault("GAME", {})["active-pet"] = pet_data
        save_config(self.config)

        #TODO: Generate and save image using pil (Low Priority)

        # Confirm and reload to status view
        self.stack.addWidget(QLabel(f"Created a {pet_data['type']} named {pet_data['Name']}."))
        self.stack.setCurrentIndex(3)
 
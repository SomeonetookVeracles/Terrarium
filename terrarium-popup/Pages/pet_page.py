from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QLabel, QPushButton,
    QComboBox, QFileDialog, QLineEdit, QFormLayout, QColorDialog, QHBoxLayout
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import os
from config_helper import load_config, save_config, debug_log

class PetPage(QWidget):
    def __init__(self):
        super().__init()
        self.config = load_config()
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout()

        pet_data = self.config.get("GAME", {}).get("active-pet", False)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        if not pet_data:
            self.init_pet_creator()
        else:
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
        layout1.addWidget(QLabel("Select creature type: "))
        layout1.addWidget(self.type_dropdown)

        next_btn1 = QPushButton("Next")
        next_btn1.clicked.connect(self.goto_appearance_page)
        layout1.addWidget(next_btn1)

        #* - P2, Appearance Customization
        appearance = QWidget()
        layout2 = QVBoxLayout()
        appearance.setLayout(layout2)

        row_layout = QHBoxLayout()

        # Base Color Picker
        self.color_picker_btn = QPushButton("Pick Base Color")
        self.color_picker_btn.clicked.connect(self.pick_color)
        row_layout.addWidget(self.color_picker_btn)

        # Pattern Dropdown
        self.pattern_dropdown = QComboBox()
        self.pattern_dropdown.addItem("None")
        for fname in os.listdir("Visuals/patterns"):
            if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                self.pattern_dropdown.addItem(fname)
        row_layout.addWidget(self.pattern_dropdown)

        layout2.addstretch() #Pushes to bottom
        layout2.addLayout(row_layout)

        # Advance Button
        next_btn2 = QPushButton("Next")
        next_btn2.clicked.connect(self.go_to_naming_page)
        layout2.addWidget(next_btn2, alignment=Qt.AlignRight)
        
        #* - P3, Name and Personality
        name_screen = QWidget()
        form = QFormLayout()
        name_screen.setLayout(form)
        
        self.name_input = QLineEdit()
        self.persona_input = QComboBox()
        personatypes = self.config.get("GAME", {}).get("personatypes", [])
        for persona in personatypes:
            self.persona_input.addItem(persona["name"])
        form.addRow(QLabel("Pet Name:"), self.name_input) 
        form.addRow(QLabel("Pet Personality"), self.persona_input)

        finish_btn = QPushButton("Finish")
        finish_btn.clicked.connect(self.finish_creation)
        form.addRow(finish_btn)

        #Add pages to stack
        self.stack.addWidget(type_select) # 0
        self.stack.addWidget(appearance) # 1
        self.stack.addWidget(name_screen) #2
        self.stack.setCurrentIndex(0)

        #State
        self.base_color = QColor("#FFFFFF")
        self.selected_pattern = None 
    def go_to_appearance_page(self):
        self.pet_type = self.type_dropdown.currentText()
        self.stack.setCurrentindex(1)
    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.base_color = color 
            self.color_picker_btn.setText(f"Color: {color.name()}")
    def go_to_naming_page(self):
        pattern_choice = self.pattern_dropdown.currentText()
        self.selected_pattern = None if pattern_choice == "None" else pattern_choice
        self.stack.setCurrentIndex(2)
    def finish_creation(self):
        pet_data = {
            "type": self.pet_type,
            "base_color": self.base_color.name(),
            "pattern": self.selected_pattern,
            "Name": self.name_input.text().strip(),
            "persona": self.persona_input.currentText().strip()
        }
        self.config.setdefault("GAME", {})["active-pet"] = pet_data
        save_config(self.config)

        debug_log("Pet creation complete")
        
        self.stack.addWidget(QLabel(f"Created a {pet_data['type']} named {pet_data['Name']}."))
        self.stack.setCurrentIndex(3)
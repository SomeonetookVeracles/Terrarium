#This page will be the main page on app startup, probably
#It will contain the main game, unless it doesn't work, in which I will kill myself.

#Imports 
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class MainPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        label = QLabel("Terrarium Main Page")
        label.setAlignment(Qt.AlignLeft)  # Align label text left
        layout.addWidget(label)
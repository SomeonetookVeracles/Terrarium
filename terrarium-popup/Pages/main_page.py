import sys
import pygame
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from config_helper import load_config

config = load_config()

class testWidget(QWidget):
    def __init__(self, width = 400, height = 300): #! DONT CHANGE THIS
        super().__init__()
        pygame.display.init()

        self.surface = pygame.Surface((width, height))
        self.ant_pos = [width // 2, height //2]

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        #TODO ---> ADD FPS COUNTER
        self.timer.start(30) #Around 33 fps when stable
    def update_frame(self):
        #Make sure surface size matches window size
        if self.surface.get_width() != self.width() or self.surface.get_height() != self.height():
            self.surface = pygame.Surface((self.width(), self.height()))
            self.ant_pos = [self.width() // 2, self.height() // 2]
        self.ant_pos[0] = (self.ant_pos[0] + 2) % self.surface.get_width()
        self.ant_pos[1] = (self.ant_pos[1] + 1) % self.surface.get_height()

        # Draw on surface
        self.surface.fill((240, 40, 240))  # clear with background color
        pygame.draw.circle(self.surface, (0, 0, 0), self.ant_pos, 10)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        width, height = self.surface.get_size()
        raw_data = pygame.image.tostring(self.surface, "RGB")
        image = QImage(raw_data, width, height, QImage.Format_RGB888)

        painter.drawImage(0, 0, image)

    def resizeEvent(self, event):
        # Resize pygame surface to match the widget
        self.surface = pygame.Surface((self.width(), self.height()))
        super().resizeEvent(event)

class MainPage(QWidget):
    def __init__(self):
        super().__init__()
        config = load_config()
        width = config["DISPLAY"].get("winwidth", 400)
        height = config["DISPLAY"].get("winheight", 300)
        if not isinstance(width, int) or width <= 0:
            width = 400
        if not isinstance(height, int) or height <= 0:
            height = 300

        self.pygame_widget = testWidget(width, height)

        layout = QVBoxLayout()
        layout.addWidget(self.pygame_widget)
        self.setLayout(layout)

#   This contains the main game, it's pretty buggy right now, so don't change it without asking -Owen

#region imports
import sys
import pygame
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPainter 
from PyQt5.QtWidgets import QWidget, QVBoxLayout

from config_helper import load_config
config = load_config()

#endregion 

class PygameWidget(QWidget):
    def __init__(self, width=400, height = 300): # TODO --> Rewrite this so it actually fills the area, need to link to the config file somehow
        super().__init__()
        self.setFixedSize(width, height)

        #Init pygame as headless, this will be important later
        pygame.display.init()
        self.surface = pygame.Surface((width, height))

        # TEST SCRIPT
        self.ant_pos = [width // 2, height // 2]

        #region Tick speed (around 30FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30) # Around 30 fps
        #endregion
    def update_frame(self): #Refreshes screen
        self.ant_pos[0] = (self.ant_pos[0] + 2) % self.surface.get_width()
        self.ant_pos[1] = (self.ant_pos[1] + 1) % self.surface.get_height()

        #   Draw on pygame surface
        self.surface.fill((240, 40, 240)) #Pinkish color
        pygame.draw.circle(self.surface, (0, 0, 0), self.ant_pos, 10) #Black circle

        self.update()
    def paintEvent(self, event):
        painter = QPainter(self)
        #convert pygame surface to string buffer, as a workaround to pygame not wanting to embed inside a widget, 

        raw_str = pygame.image.tostring(self.surface, "RGB") #Converts the image into raw image data, could hugely impact performance
        image = QImage(raw_str, self.surface.get_width(), self.surface.get_height(), QImage.Format_RGB888) #Parses it into a image
        painter.drawImage(0, 0, image) #Draws image in window

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
        self.pygame_widget = PygameWidget(400, 300) # TODO --> Rewrite this so it actually fills the area, need to link to the config file somehow
        layout = QVBoxLayout()
        layout.addWidget(self.pygame_widget)
        self.setLayout(layout)

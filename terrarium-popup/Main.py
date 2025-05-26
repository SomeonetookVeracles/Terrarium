import sys
import threading 
from PyQt5.QtWidgets import QApplication, QMainWindow 
from PyQt5.QtCore import Qt, QRect 
from pystray import Icon, Menu, MenuItem 
from PIL import Image, ImageDraw 

hPct = 0.33 # Horizontal width percentage (1/3 screen)
vPct = 0.5 # Vertical height percentage (1/2 screen) 

class TrayApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width() * hPct)
        height = int(screen.height() * vPct)

        # Corner Positioning
        x = screen.width() - width
        y = screen.height() - height

        self.setGeometry(QRect(x, y, width, height))
        self.setWindowTitle("Terrarium")
        
        
        #AOT, No resize/move/min/max buttons
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.FramelessWindowHint
        )

    def closeEvent(self, event):
        event.ignore()
        self.showMinimized()

def create_icon():
    # Basic Red/White icon
    icon_img = Image.new("RGB", (64, 64), "red")
    draw = ImageDraw.Draw(icon_img)

    def on_open(icon, item):
        window.show()

    def on_exit(icon, item):
        icon.stop()
        app.quit()
    return Icon("Terrarium", icon_img, "Terrarium", menu=Menu(
        MenuItem("Open", on_open),
        MenuItem("Exit", on_exit)
    ))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrayApp()
    window.show()

    icon = create_icon()
    threading.Thread(target=icon.run, daemon=True).start()

    sys.exit(app.exec_())
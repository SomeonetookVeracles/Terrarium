import sys
import os
from PyQt5.QtWidgets import(
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt 

from Services.theme_catcher import update_theme_list
from config_helper import load_config, save_config

from Pages.settings_page import SettingsPage
from Pages.main_page import MainPage

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_current_stylesheet(): #Accesses current stylesheet from the config file
    #TODO ---> MAKE THIS UPDATE IN REAL TIME
    config = load_config()
    current_theme = config.get("DISPLAY", {}).get("current_theme", "")
    themes = config.get("DISPLAY", {}).get("THEMES", [])
    for theme in themes:
        if theme["name"] == current_theme:
            return theme["content"]
        fallback_path = resource_path("Visuals/fluent-Light.qss")
        if os.path.exists(fallback_path):
            with open(fallback_path, "r", encoding="utf-8") as f:
                return f.read() 
        return ""
class TerrariumUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.pages = QStackedWidget() #Switched this from QStackedLayout, should help with performance a tad.
        self.sidebar_layout = QVBoxLayout()
        self.init_ui()
        self.init_tray()

    def init_ui(self):
        self.setWindowTitle("Terrarium")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        screen = QApplication.primaryScreen().availableGeometry()
        width_ratio = self.config["DISPLAY"].get("width_ratio", 0.8)
        height_ratio = self.config["DISPLAY"].get("height_ratio", 0.8)
        #region Establishing Variables
        width = int(screen.width() * width_ratio)
        height = int(screen.height() * height_ratio)
        x = screen.width() - width
        y = screen.height() - height 
        #endregion

        self.setGeometry(x, y, width, height)
        #Sidebar Init
        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidewidth = self.config["DISPLAY"].get("sidebar_width", 120)
        sidebar_widget.setFixedWidth(sidewidth)
        sidebar_widget.setLayout(self.sidebar_layout)

        #Set win dimensions for other components
        #This is done here because Pygame will be loaded on startup by default
        self.config["DISPLAY"]["winwidth"] = width - sidewidth
        self.config["DISPLAY"]["winheight"] = height #Calculating this here instead of in the file helps keep pygame from spazzing out
        save_config(self.config)

        #Add pages
        self.add_page("Main", MainPage)
        self.add_page("Settings", SettingsPage)
        self.pages.setCurrentIndex(0)

        #Combine sidebar and main widget, compartmentalizing like this helps debug easier
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)#Keep both of these at zero, otherwise it looks funky 
        main_layout.setSpacing(0)                 #Same
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.pages)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def add_page(self, name, widget_class):
        page_widget = widget_class()
        index = self.pages.count()
        self.pages.addWidget(page_widget)

        btn = QPushButton(name)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setObjectName("sidebar-button")
        btn.clicked.connect(lambda: self.pages.setCurrentIndex(index))
        self.sidebar_layout.addWidget(btn)

    def init_tray(self):
        self.tray = QSystemTrayIcon(self)
        icon_path = os.path.join("Visuals", "trayIcon.png") # Establish icon path
        if os.path.exists(icon_path): #If it can find the path, use it, otherwise just make an icon
            self.tray.setIcon(QIcon(icon_path))
        else: #TODO ---> Make the backup icon a the invalid texture from minecraft or something more interesting                            
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor("Blue")) # Got tired of red, swapped to blue
            self.tray.setIcon(QIcon(pixmap))
        #Create menu when right clicking the tray icon
        #TODO ---> Add mute, option to open into settings, and theme changer, and maybe a debug mode
        tray_menu = QMenu()

        open_action = QAction("Open", self) #! Open window
        open_action.triggered.connect(self.show_normal)
        tray_menu.addAction(open_action)

        close_action = QAction("Close", self) #! Close Window
        close_action.triggered.connect(self.hide)
        tray_menu.addAction(close_action)

        term_action = QAction("Quit", self) #! Close process entirely
        term_action.triggered.connect(lambda: QApplication.instance().quit())
        tray_menu.addAction(term_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.setVisible(True)
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isMinimized() or not self.isinvisible():
                self.show_normal()
            else:
                self.hide()
    def show_normal(self):
        self.show()
        self.raise_()
        self.activateWindow()
    def closeEvent(self, event):
        event.ignore()
        self.hide()
if __name__ == "__main__":
    update_theme_list()
    app = QApplication(sys.argv)
    app.setStyleSheet(load_current_stylesheet())
    window = TerrariumUI()
    window.show()
    sys.exit(app.exec_())


import os
import sys
from Services.Hakatime_service import WakatimeService
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QSystemTrayIcon, QMenu, QAction, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QTimer
from config_helper import load_config, save_config, debug_log
from Services.theme_catcher import update_theme_list
from Services.theme_loader import load_current_theme_stylesheet
# All pages
from Pages.pet_page import PetPage
from Pages.settings_page import SettingsPage
from Pages.main_page import MainPage

class TerrariumUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pages = QStackedWidget()
        self.sidebar_layout = QVBoxLayout()
        self.init_ui()
        self.init_tray()
        self.hackatime_service = WakatimeService(self)
    def init_ui(self):
        self.setWindowTitle("Terrarium")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        screen = QApplication.primaryScreen().availableGeometry()
        config = load_config()
        width = int(screen.width() * config["DISPLAY"].get("width_ratio", 0.8))
        height = int(screen.height() * config["DISPLAY"].get("height_ratio", 0.8))
        x = screen.width() - width
        y = screen.height() - height
        self.setGeometry(x, y, width, height)
        sidebar_widget = QWidget()
        self.sidebar_layout.setAlignment(Qt.AlignTop)
        self.sidebar_layout.setContentsMargins(8, 8, 8, 8)
        self.sidebar_layout.setSpacing(10)
        sidewidth = config["DISPLAY"].get("sidebar_width", 120)
        sidebar_widget.setFixedWidth(sidewidth)
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setLayout(self.sidebar_layout)

        config["DISPLAY"]["winheight"] = height
        config["DISPLAY"]["winwidth"] = width - sidewidth
        save_config(config)
        self.pages.setObjectName("content")
        self.add_page("Main", MainPage)
        self.add_page("Status", PetPage)
        self.add_page("Settings", SettingsPage)
        self.pages.setCurrentIndex(0) 
        main_layout = QHBoxLayout()
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.pages)

        container = QWidget()
        container.setLayout(main_layout)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 180))
        container.setGraphicsEffect(shadow)
        #Give the shadow margin space, required because of the lack of borders from framelessness
        shadow_wrapper = QWidget()
        wrapper_layout = QVBoxLayout()
        wrapper_layout.setContentsMargins(20, 20, 20, 20) # Makes room for shadows, don't adjust
        wrapper_layout.addWidget(container)
        shadow_wrapper.setLayout(wrapper_layout)

        self.setCentralWidget(shadow_wrapper)
        # Debug flagging
        print("Pages count:", self.pages.count())
        print("Window geometry:", self.geometry())

    def add_page(self, name, widget_class):
        page = widget_class()
        index = self.pages.count()
        self.pages.addWidget(page) 

        btn = QPushButton(name)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setObjectName("sidebar-button")
        btn.clicked.connect(lambda: self.pages.setCurrentIndex(index))
        self.sidebar_layout.insertWidget(index, btn)

    def init_tray(self):
        self.tray = QSystemTrayIcon(self)
        icon_path = os.path.join("Visuals", "trayIcon64.png") # Establish icon path
        if os.path.exists(icon_path): #Fallback catcher, if it can't find the icon it just makes one
            self.tray.setIcon(QIcon(icon_path))
        else:
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor("red"))
            self.tray.setIcon(QIcon(pixmap))
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.setToolTip("Terrarium")


        tray_menu = QMenu()

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.show_normal)
        tray_menu.addAction(open_action)

        close_action = QAction("Close", self)
        close_action.triggered.connect(self.hide)
        tray_menu.addAction(close_action)

        term_action = QAction("Exit", self)
        term_action.triggered.connect(lambda: QApplication.instance().quit())
        tray_menu.addAction(term_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.setVisible(True)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
                debug_log("Window Hidden")
            else:
                self.show_normal()
                debug_log("Window Opened")
    def show_normal(self):
        self.show()
        self.raise_()
        self.activateWindow()
        debug_log("Window Opened")
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        debug_log("Window Closed")

if __name__ == "__main__":
    # Update themes at startup
    update_theme_list()
    app = QApplication(sys.argv)
    window = TerrariumUI()
    window.show()
    # Apply current theme's stylesheet
    app.setStyleSheet(load_current_theme_stylesheet())
    sys.exit(app.exec_())

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedLayout, QStackedWidget,
    QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QRect

from Services.theme_catcher import update_theme_list
from config_helper import load_config, save_config, debug_log
from Services.theme_loader import load_current_theme_stylesheet

# All pages
from Pages.pet_page import PetPage
from Pages.settings_page import SettingsPage
from Pages.main_page import MainPage

class TerrariumUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pages = QStackedWidget()  # ✅ Replaced QStackedLayout with QStackedWidget
        self.sidebar_layout = QVBoxLayout()
        self.init_ui()
        self.init_tray()

    def init_ui(self):
        self.setWindowTitle("Terrarium")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Geometry based on DISPLAY config
        screen = QApplication.primaryScreen().availableGeometry()
        config = load_config()
        width = int(screen.width() * config["DISPLAY"].get("width_ratio", 0.8))
        height = int(screen.height() * config["DISPLAY"].get("height_ratio", 0.8))
        x = screen.width() - width
        y = screen.height() - height

        self.setGeometry(x, y, width, height)

        # Sidebar setup
        sidebar_widget = QWidget()
        self.sidebar_layout.setAlignment(Qt.AlignTop)
        self.sidebar_layout.setContentsMargins(8, 8, 8, 8)
        self.sidebar_layout.setSpacing(10)
        sidewidth = config["DISPLAY"].get("sidebar_width", 120)
        sidebar_widget.setFixedWidth(sidewidth)
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setLayout(self.sidebar_layout)

        # Save win size for embedded PygameWidget
        config["DISPLAY"]["winheight"] = height
        config["DISPLAY"]["winwidth"] = width - sidewidth
        save_config(config)

        # ✅ Use QStackedWidget for content
        self.pages.setObjectName("content")

        # Add pages
        self.add_page("Main", MainPage)
        self.add_page("Status", PetPage)
        self.add_page("Settings", SettingsPage)
        self.pages.setCurrentIndex(0)  # Set initial page

        # Combine into main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(self.pages)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

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

    # Apply current theme's stylesheet
    app.setStyleSheet(load_current_theme_stylesheet())

    window = TerrariumUI()
    window.show()
    sys.exit(app.exec_())

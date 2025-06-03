import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedLayout, QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtGui import QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, QRect
from config_helper import load_config
from Pages.settings_page import SettingsPage
from Pages.main_page import MainPage 

config = load_config()

class TerrariumUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pages = QStackedLayout()
        self.sidebar_layout = QVBoxLayout()
        self.init_ui()
        self.init_tray()

    def init_ui(self):
        self.setWindowTitle("Terrarium")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Geometry based on DISPLAY config
        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width() * config["DISPLAY"]["width_ratio"])
        height = int(screen.height() * config["DISPLAY"]["height_ratio"])
        x = screen.width() - width
        y = screen.height() - height
        self.setGeometry(QRect(x, y, width, height))

        # Sidebar setup
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(120)
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setLayout(self.sidebar_layout)

        # Stacked content area
        stacked_widget = QWidget()
        stacked_widget.setLayout(self.pages)
        stacked_widget.setObjectName("content")

        # Add pages
        self.add_page("Main", MainPage)
        self.add_page("Settings", SettingsPage)

        # Combine into main layout
        main_layout = QHBoxLayout()
        main_layout.addWidget(sidebar_widget)
        main_layout.addWidget(stacked_widget)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

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
        self.tray = QSystemTrayIcon()
        icon_path = os.path.join("Visuals", "icon.png")
        if os.path.exists(icon_path):
            self.tray.setIcon(QIcon(icon_path))
        else:
            pixmap = QPixmap(64, 64)
            pixmap.fill(QColor("red"))
            self.tray.setIcon(QIcon(pixmap))

        self.tray.setVisible(True)

        tray_menu = QMenu()
        open_action = QAction("Open")
        open_action.triggered.connect(self.show_normal)

        exit_action = QAction("Exit")
        exit_action.triggered.connect(QApplication.instance().quit)

        tray_menu.addAction(open_action)
        tray_menu.addAction(exit_action)
        self.tray.setContextMenu(tray_menu)

        self.tray.activated.connect(self.on_tray_activated)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isMinimized() or not self.isVisible():
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

def resource_path(relative_path):
    # Get absolute path
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_stylesheet(path):
    full_path = resource_path(path)
    with open(full_path, "r") as f:
        return f.read()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Load stylehseet from visuals folder
    app.setStyleSheet(load_stylesheet("Visuals/style.qss"))  # Load global style
    window = TerrariumUI()
    window.show()
    sys.exit(app.exec_())
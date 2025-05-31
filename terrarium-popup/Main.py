import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QStackedLayout, QLabel
)
from PyQt5.QtCore import Qt, QRect 
from PyQt5.QtGui import QColor, QPalette 

#   Page Classes ---> Put new pages here.
class MainPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Main Page"))
        self.setLayout(layout)
class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Settings Page"))
        self.setLayout(layout)

#   Main Window ---> Pretty self explanatory, 
class TerrariumUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pages = QStackedLayout()
        self.sidebar_layout = QVBoxLayout()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Terrarium")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        screen = QApplication.primaryScreen().availableGeometry()
        width = int(screen.width() * 0.33)    # TODO ---> MAKE JSON ARCHIVE AND GLOBAL VARIABLE
        height = int(screen.height() * 0.50)    # TODO ---> MAKE JSON ARCHIVE AND GLOBAL VARIABLE
        x = screen.width() - width 
        y = screen.height() - height
        self.setGeometry(QRect(x, y, width, height))

        #   Sidebar Widget ---> This is the settings for the sidebar with all the settings and other shenanigans
        sidebar_widget = QWidget()
        sidebar_widget.setFixedWidth(120) # TODO ---> Make Adjustible to width
        sidebar_widget.setStyleSheet("""
            background-color: #2E3440;
            border-right: 1px solid #444;
        """)
        sidebar_widget.setLayout(self.sidebar_layout)
        self.sidebar_layout.addStretch() # TODO ---> ADD BUTTONS ABOVE THIS

        #   Stacked Pages Widget
        stacked_widget = QWidget()
        stacked_widget.setLayout(self.pages)
        stacked_widget.setStyleSheet("background-color: #ECEFF4; padding: 20px")

        # TODO ---> ADD PAGES HERE
        self.page_index = 0
        self.page_map = {}
        self.add_page("main", MainPage)
        self.add_page("settings", SettingsPage)

        #   Layout Wrapping
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
        btn.setMinimumHeight(40) # TODO ---> MAKE ADJUSTIBLE WITH SIZING
        btn.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #3B4252;
                border: none;
                padding: 10px;
                text-align: left;   
            }
            QPushButton:hover {
                background-color: #434C5E;
            }
        """)
        btn.clicked.connect(lambda: self.pages.setCurrentIndex(index))
        self.sidebar_layout.insertWidget(index, btn)
    def closeEvent(self, event):
        event.ignore()
        self.showMinimized()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TerrariumUI()
    window.show()
    sys.exit(app.exec_())
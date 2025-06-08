from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from PyQt5.QtGui import QColor

class Notification(QWidget):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("notification-popup")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)

        label = QLabel(message)
        label.setWordWrap(True)
        label.setObjectName("notification-label")
        layout.addWidget(label)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.setGraphicsEffect(shadow)

        QTimer.singleShot(3000, self.close)

    def show_at(self, pos):
        self.adjustSize()
        self.move(pos)
        self.show()
        self.setWindowOpacity(0)
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(300)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.start()

def show_notification(message, window):
    notif = Notification(message)
    geo = window.geometry()
    x = geo.right() - 300  # Adjust for width
    y = geo.bottom() - 100
    notif.show_at(QPoint(x, y))

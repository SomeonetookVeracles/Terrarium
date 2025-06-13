from PyQt5.QtWidgets import QWidget, QLabel, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QPainter, QColor, QPainterPath, QFont

class SpeechBubble(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Initialize properties
        self.text = ""
        self.current_text = ""
        self.typing_speed = 30  # milliseconds per character
        self.typing_timer = QTimer()
        self.typing_timer.timeout.connect(self._type_next_char)
        self.typing_index = 0
        
        # Create text label
        self.text_label = QLabel(self)
        self.text_label.setStyleSheet("""
            QLabel {
                color: #333333;
                background: transparent;
                font-size: 14px;
                font-family: 'Arial';
            }
        """)
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        # Animation properties
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Set initial size and position
        self.resize(200, 100)
        self.move(100, 100)
        
    def show_message(self, text, duration=5000, position=None):
        """Show a message with typing animation"""
        self.text = text
        self.current_text = ""
        self.typing_index = 0
        
        # Set position if provided
        if position:
            self.move(position)
            
        # Start typing animation
        self.typing_timer.start(self.typing_speed)
        
        # Show the bubble
        self.show()
        self.raise_()
        
        # Schedule auto-hide
        QTimer.singleShot(duration, self.hide_message)
        
    def hide_message(self):
        """Hide the speech bubble with fade animation"""
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.start()
        self.fade_animation.finished.connect(self.hide)
        
    def _type_next_char(self):
        """Type the next character in the animation"""
        if self.typing_index < len(self.text):
            self.current_text += self.text[self.typing_index]
            self.text_label.setText(self.current_text)
            self.typing_index += 1
            self._update_size()
        else:
            self.typing_timer.stop()
            
    def _update_size(self):
        """Update the size based on the text content"""
        # Calculate required size
        metrics = self.text_label.fontMetrics()
        text_width = metrics.horizontalAdvance(self.text_label.text())
        text_height = metrics.height() * (self.text_label.text().count('\n') + 1)
        
        # Add padding
        width = min(text_width + 40, 300)  # Max width of 300
        height = text_height + 40
        
        # Update size
        self.resize(width, height)
        self.text_label.setGeometry(20, 20, width - 40, height - 40)
        
    def paintEvent(self, event):
        """Custom paint event for the speech bubble"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create bubble path
        path = QPainterPath()
        rect = self.rect().adjusted(10, 10, -10, -10)
        
        # Draw main bubble
        path.addRoundedRect(rect, 15, 15)
        
        # Draw triangle pointer
        pointer = QPainterPath()
        pointer.moveTo(rect.left() + 20, rect.bottom())
        pointer.lineTo(rect.left() + 30, rect.bottom() + 10)
        pointer.lineTo(rect.left() + 40, rect.bottom())
        path.addPath(pointer)
        
        # Fill with white and draw border
        painter.fillPath(path, QColor(255, 255, 255))
        painter.setPen(QColor(200, 200, 200))
        painter.drawPath(path)
        
    def mousePressEvent(self, event):
        """Handle mouse press to allow dragging"""
        self.old_pos = event.globalPos()
        
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        delta = event.globalPos() - self.old_pos
        self.move(self.pos() + delta)
        self.old_pos = event.globalPos() 
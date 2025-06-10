# test_widget.py
import sys
import pygame
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QProgressBar,
    QLabel, QApplication
)
from config_helper import load_config, debug_log
from Services.data_catcher import get_metric_names, get_metric_values, deteriorate_metrics


class testWidget(QWidget):
    def __init__(self, width=400, height=300):
        super().__init__()
        pygame.display.init()

        self.surface = pygame.Surface((width, height))
        self.ant_pos = [width // 2, height // 2]

        self.metric_names = get_metric_names()
        self.metrics_config = get_metric_values()

        self.bars = []
        self.labels = []

        self.setup_overlay_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_bars)
        self.update_timer.start(1000)

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_metrics_config)
        self.refresh_timer.start(15000)

        self.decay_timer = QTimer()
        self.decay_timer.timeout.connect(self.apply_decay)
        self.decay_timer.start(15000)

    def setup_overlay_ui(self):
        self.overlay_container = QWidget(self)
        self.overlay_container.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.overlay_container.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(self.overlay_container)
        layout.setContentsMargins(10, 0, 10, 10)
        layout.setSpacing(15)

        for name in self.metric_names:
            title_label = QLabel(name)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    font-weight: bold;
                    color: white;
                }
            """)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setFixedHeight(12)
            bar.setStyleSheet("""
                QProgressBar {
                    background-color: #eee;
                    border: 1px solid #bbb;
                    border-radius: 4px;
                }
                QProgressBar::chunk {
                    background-color: #00bfff;
                    border-radius: 4px;
                }
            """)

            box_widget = QWidget()
            box_layout = QVBoxLayout(box_widget)
            box_layout.setContentsMargins(8, 6, 8, 6)
            box_layout.setSpacing(4)
            box_layout.addWidget(title_label, alignment=Qt.AlignCenter)
            box_layout.addWidget(bar)

            box_widget.setStyleSheet("""
                QWidget {
                    background-color: rgba(0, 0, 0, 150);
                    border-radius: 6px;
                }
            """)

            layout.addWidget(box_widget)
            self.bars.append(bar)
            self.labels.append(title_label)

    def resizeEvent(self, event):
        self.surface = pygame.Surface((self.width(), self.height()))
        if hasattr(self, 'overlay_container'):
            self.overlay_container.setGeometry(0, self.height() - 60, self.width(), 50)
        super().resizeEvent(event)

    def update_frame(self):
        if self.surface.get_width() == 0 or self.surface.get_height() == 0:
            return

        self.ant_pos[0] = (self.ant_pos[0] + 2) % self.surface.get_width()
        self.ant_pos[1] = (self.ant_pos[1] + 1) % self.surface.get_height()

        self.surface.fill((240, 40, 240))
        pygame.draw.circle(self.surface, (0, 0, 0), self.ant_pos, 10)
        self.update()

    def update_bars(self):
        for i, name in enumerate(self.metric_names):
            value = self.metrics_config.get(name, 0)
            self.bars[i].setValue(max(0, min(value, 100)))
            self.labels[i].setText(f"{name}: {value}%")

    def refresh_metrics_config(self):
        self.metrics_config = get_metric_values()

    def apply_decay(self):
        deteriorate_metrics()
        self.refresh_metrics_config()

    def paintEvent(self, event):
        painter = QPainter(self)
        width, height = self.surface.get_size()
        raw_data = pygame.image.tostring(self.surface, "RGB")
        image = QImage(raw_data, width, height, QImage.Format_RGB888)
        painter.drawImage(0, 0, image)


class MainPage(QWidget):
    def __init__(self):
        super().__init__()
        display_config = load_config().get("DISPLAY", {})
        width = display_config.get("winwidth", 400)
        height = display_config.get("winheight", 300)
        if not isinstance(width, int) or width <= 0:
            width = 400
        if not isinstance(height, int) or height <= 0:
            height = 300

        self.pygame_widget = testWidget(width, height)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.pygame_widget)
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainPage()
    main.show()
    sys.exit(app.exec_())

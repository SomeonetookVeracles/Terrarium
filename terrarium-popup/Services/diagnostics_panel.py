from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from Services.logger import get_log

class DiagnosticsPanel(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Diagnostics Log")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        refresh_btn = QPushButton("Refresh Log")
        refresh_btn.clicked.connect(self.load_log)
        layout.addWidget(refresh_btn)

        self.load_log()

    def load_log(self):
        self.log_area.setPlainText(get_log())

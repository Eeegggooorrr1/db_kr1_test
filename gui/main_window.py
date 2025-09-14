import os
from datetime import datetime

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from PySide6.QtWidgets import (QMainWindow, QPushButton, QWidget, QVBoxLayout,
                               QDialog, QLabel, QLineEdit, QTextEdit, QDialogButtonBox, QDoubleSpinBox, QCheckBox,
                               QHBoxLayout, QFileDialog, QMessageBox, QComboBox, QTableWidget, QTableWidgetItem,
                               QHeaderView)
from typing import Optional

from db.database import SessionLocal
from db.models import AttackTypeEnum
from db.requests import create_experiment, get_experiment_max_id, get_run_max_id, create_run, create_image
from gui.add_widget import ChoiceDialog
from gui.view_widget import ViewDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главное окно")
        self.setFixedSize(300, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        add_btn = QPushButton("Вставить данные")
        add_btn.clicked.connect(self.open_dialog)

        view_btn = QPushButton("Посмотреть данные")
        view_btn.clicked.connect(self.open_view)

        layout.addWidget(add_btn)
        layout.addWidget(view_btn)

    def open_dialog(self):
        dialog = ChoiceDialog(self)
        dialog.exec()
    def open_view(self):
        self.dialog = ViewDialog(self)
        self.dialog.show()
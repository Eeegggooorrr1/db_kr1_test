import os

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from PySide6.QtWidgets import (QMainWindow, QPushButton, QWidget, QVBoxLayout,
                               QDialog, QLabel, QLineEdit, QTextEdit, QDialogButtonBox, QDoubleSpinBox, QCheckBox,
                               QHBoxLayout, QFileDialog, QMessageBox)
from typing import Optional

from db.database import SessionLocal
from db.requests import create_experiment, get_experiment_max_id, get_run_max_id, create_run, create_image


class ChoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выберите действие")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        btn_experiment = QPushButton("Создать эксперимент")
        btn_experiment.clicked.connect(lambda: self.open_form(ExperimentForm))

        btn_run = QPushButton("Создать прогон")
        btn_run.clicked.connect(lambda: self.open_form(RunForm))

        btn_image = QPushButton("Добавить изображение")
        btn_image.clicked.connect(lambda: self.open_form(ImageForm))

        layout.addWidget(btn_experiment)
        layout.addWidget(btn_run)
        layout.addWidget(btn_image)

        self.setLayout(layout)

    def open_form(self, form_class):
        form = form_class(self)
        form.exec()


class ExperimentForm(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать эксперимент")
        self.setFixedSize(400, 250)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Номер эксперимента:"))
        self.number_edit = QLineEdit(str(get_experiment_max_id()+1))
        self.number_edit.setReadOnly(True)
        self.number_edit.setStyleSheet("background-color: #f0f0f0; color: #666666;")
        layout.addWidget(self.number_edit)


        layout.addWidget(QLabel("Название*:"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Описание:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        layout.addWidget(self.desc_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_data(self):
        description = self.desc_edit.toPlainText().strip()
        return {
            'name': self.name_edit.text().strip(),
            'description': description if description else None,
        }

    def accept(self):
        data = self.get_data()
        create_experiment(name=data['name'], description=data['description'])

        super().accept()
        print("Данные эксперимента:", self.get_data())


class RunForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать прогон")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Номер прогона:"))
        self.number_edit = QLineEdit(str(get_run_max_id() + 1))
        self.number_edit.setReadOnly(True)
        self.number_edit.setStyleSheet("background-color: #f0f0f0; color: #666666;")
        layout.addWidget(self.number_edit)

        layout.addWidget(QLabel("Номер эксперимента*:"))
        self.experiment_id_edit = QLineEdit()
        layout.addWidget(self.experiment_id_edit)

        layout.addWidget(QLabel("Точность:"))
        self.accuracy_spin = QDoubleSpinBox()
        self.accuracy_spin.setRange(0.0, 1.0)
        self.accuracy_spin.setSingleStep(0.01)
        self.accuracy_spin.setDecimals(4)
        layout.addWidget(self.accuracy_spin)

        layout.addWidget(QLabel("Проверен:"))
        self.verified_checkbox = QCheckBox()
        self.verified_checkbox.setText("Да")
        layout.addWidget(self.verified_checkbox)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_data(self):
        return {
            'experiment_id': int(self.experiment_id_edit.text()),
            'accuracy': self.accuracy_spin.value(),
            'flagged': self.verified_checkbox.isChecked()
        }

    def accept(self):
        data = self.get_data()
        create_run(experiment_id=data['experiment_id'], accuracy=data['accuracy'], flagged=data['flagged'])

        super().accept()
        print("Данные эксперимента:", self.get_data())



class ImageForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Аннотирование изображения")
        self.setFixedSize(800, 600)
        self.image_path = ""
        self.rect = QRect()
        self.drawing = False
        self.start_point = None
        self.current_rect = None
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        info_layout = QHBoxLayout()
        info_layout.addWidget(QLabel("Путь к файлу:"))
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        info_layout.addWidget(self.path_edit)

        info_layout.addWidget(QLabel("Название:"))
        self.name_edit = QLineEdit()
        self.name_edit.setReadOnly(True)
        info_layout.addWidget(self.name_edit)
        main_layout.addLayout(info_layout)

        self.select_btn = QPushButton("Выбрать изображение")
        self.select_btn.clicked.connect(self.select_image)
        main_layout.addWidget(self.select_btn)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.image_label.setMinimumSize(400, 300)
        self.image_label.mousePressEvent = self.mouse_press_event
        self.image_label.mouseMoveEvent = self.mouse_move_event
        self.image_label.mouseReleaseEvent = self.mouse_release_event
        main_layout.addWidget(self.image_label)

        coords_layout = QHBoxLayout()
        coords_layout.addWidget(QLabel("Центр X:"))
        self.center_x_edit = QLineEdit()
        self.center_x_edit.setReadOnly(True)
        coords_layout.addWidget(self.center_x_edit)

        coords_layout.addWidget(QLabel("Центр Y:"))
        self.center_y_edit = QLineEdit()
        self.center_y_edit.setReadOnly(True)
        coords_layout.addWidget(self.center_y_edit)

        coords_layout.addWidget(QLabel("Ширина:"))
        self.width_edit = QLineEdit()
        self.width_edit.setReadOnly(True)
        coords_layout.addWidget(self.width_edit)

        coords_layout.addWidget(QLabel("Высота:"))
        self.height_edit = QLineEdit()
        self.height_edit.setReadOnly(True)
        coords_layout.addWidget(self.height_edit)
        main_layout.addLayout(coords_layout)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )

        if file_path:
            self.image_path = file_path
            self.path_edit.setText(file_path)
            self.name_edit.setText(os.path.basename(file_path))

            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.image_label.setPixmap(scaled_pixmap)
                self.original_pixmap = pixmap
            else:
                QMessageBox.warning(self, "Ошибка", "Не удалось загрузить изображение")

    def mouse_press_event(self, event):
        if not self.image_label.pixmap():
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.start_point = event.pos()
            self.current_rect = QRect(self.start_point, self.start_point)

    def mouse_move_event(self, event):
        if self.drawing and self.start_point:
            self.current_rect = QRect(self.start_point, event.pos()).normalized()
            self.update_image_display()

    def mouse_release_event(self, event):
        if self.drawing and self.start_point:
            self.drawing = False
            self.rect = QRect(self.start_point, event.pos()).normalized()
            self.update_coordinates()
            self.update_image_display()

    def update_image_display(self):
        if not self.image_label.pixmap():
            return

        pixmap = self.original_pixmap.copy()

        scaled_pixmap = pixmap.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        if self.current_rect:
            painter = QPainter(scaled_pixmap)
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.drawRect(self.current_rect)
            painter.end()

        self.image_label.setPixmap(scaled_pixmap)

    def update_coordinates(self):
        if self.rect.isValid():
            scale_x = self.original_pixmap.width() / self.image_label.pixmap().width()
            scale_y = self.original_pixmap.height() / self.image_label.pixmap().height()

            scaled_rect = QRect(
                int(self.rect.x() * scale_x),
                int(self.rect.y() * scale_y),
                int(self.rect.width() * scale_x),
                int(self.rect.height() * scale_y)
            )

            self.center_x_edit.setText(str(scaled_rect.center().x()))
            self.center_y_edit.setText(str(scaled_rect.center().y()))
            self.width_edit.setText(str(scaled_rect.width()))
            self.height_edit.setText(str(scaled_rect.height()))

    def get_data(self):
        return {
            "image_path": self.image_path,
            "image_name": self.name_edit.text(),
            "center_x": self.center_x_edit.text(),
            "center_y": self.center_y_edit.text(),
            "width": self.width_edit.text(),
            "height": self.height_edit.text()
        }
    def accept(self):
        data = self.get_data()
        create_image(experiment_id=data['experiment_id'], accuracy=data['accuracy'], flagged=data['flagged'])

        super().accept()
        print("Данные эксперимента:", self.get_data())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главное окно")
        self.setFixedSize(300, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        btn = QPushButton("Вставить данные")
        btn.clicked.connect(self.open_dialog)

        layout.addWidget(btn)

    def open_dialog(self):
        dialog = ChoiceDialog(self)
        dialog.exec()
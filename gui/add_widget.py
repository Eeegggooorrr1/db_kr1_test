import os
from datetime import datetime

from PySide6.QtCore import QRect, Qt, QPoint
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor
from PySide6.QtWidgets import (QMainWindow, QPushButton, QWidget, QVBoxLayout,
                               QDialog, QLabel, QLineEdit, QTextEdit, QDialogButtonBox, QDoubleSpinBox, QCheckBox,
                               QHBoxLayout, QFileDialog, QMessageBox, QComboBox, QTableWidget, QTableWidgetItem,
                               QHeaderView)
from typing import Optional

from db.database import SessionLocal
from db.models import AttackTypeEnum
from db.requests import create_experiment, get_experiment_max_id, get_run_max_id, create_run, create_image

class ChoiceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выберите действие")
        self.setFixedSize(500, 350)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
        """)

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
        try:
            create_experiment(name=data['name'], description=data['description'])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать эксперимент: {str(e)}")

        super().accept()


class RunForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создать прогон")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Номер прогона:"))
        self.number_edit = QLineEdit(str(get_run_max_id()))
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
            'experiment_id': int(self.experiment_id_edit.text()) if self.experiment_id_edit.text() else None,
            'accuracy': self.accuracy_spin.value() if self.accuracy_spin.value() else None,
            'flagged': self.verified_checkbox.isChecked() if self.verified_checkbox.isChecked() else None
        }

    def accept(self):
        data = self.get_data()
        try:
            create_run(experiment_id=data['experiment_id'], accuracy=data['accuracy'], flagged=data['flagged'])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать прогон: {str(e)}")

        super().accept()



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

        attack_layout = QHBoxLayout()
        attack_layout.addWidget(QLabel("Тип атаки:"))
        self.attack_type_combo = QComboBox()
        for attack_type in AttackTypeEnum:
            self.attack_type_combo.addItem(attack_type.value, attack_type)
        attack_layout.addWidget(self.attack_type_combo)

        attack_layout.addWidget(QLabel("Номер прогона*:"))
        self.run_id_edit = QLineEdit()
        attack_layout.addWidget(self.run_id_edit)

        main_layout.addLayout(attack_layout)

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
            # Преобразуем координаты мыши к координатам исходного изображения
            scaled_pos = self.scale_point_to_original(event.pos())
            if scaled_pos is None:
                return

            self.drawing = True
            self.start_point = scaled_pos
            self.current_rect = QRect(self.start_point, self.start_point)

    def mouse_move_event(self, event):
        if self.drawing and self.start_point:
            scaled_pos = self.scale_point_to_original(event.pos())
            if scaled_pos is None:
                return

            self.current_rect = QRect(self.start_point, scaled_pos).normalized()
            self.update_image_display()

    def mouse_release_event(self, event):
        if self.drawing and self.start_point:
            scaled_pos = self.scale_point_to_original(event.pos())
            if scaled_pos is None:
                return

            self.drawing = False
            self.rect = QRect(self.start_point, scaled_pos).normalized()
            self.update_coordinates()
            self.update_image_display()

    def scale_point_to_original(self, point):
        """Преобразует точку из координат виджета в координаты исходного изображения"""
        if not self.original_pixmap:
            return None

        # Получаем текущий pixmap из label
        label_pixmap = self.image_label.pixmap()
        if not label_pixmap:
            return None

        # Определяем область отображения изображения внутри label
        pixmap_rect = self.get_image_rect()

        # Проверяем, находится ли точка внутри области изображения
        if not pixmap_rect.contains(point):
            return None

        # Масштабируем координаты к исходному изображению
        scale_x = self.original_pixmap.width() / pixmap_rect.width()
        scale_y = self.original_pixmap.height() / pixmap_rect.height()

        scaled_x = (point.x() - pixmap_rect.x()) * scale_x
        scaled_y = (point.y() - pixmap_rect.y()) * scale_y

        return QPoint(int(scaled_x), int(scaled_y))

    def get_image_rect(self):
        """Возвращает прямоугольник с фактическими координатами изображения внутри label"""
        label_size = self.image_label.size()
        pixmap = self.image_label.pixmap()

        if not pixmap:
            return QRect()

        # Вычисляем размер изображения с сохранением пропорций
        pixmap_size = pixmap.size()
        pixmap_size.scale(label_size, Qt.AspectRatioMode.KeepAspectRatio)

        # Вычисляем позицию для центрирования изображения
        x = (label_size.width() - pixmap_size.width()) // 2
        y = (label_size.height() - pixmap_size.height()) // 2

        return QRect(x, y, pixmap_size.width(), pixmap_size.height())

    def update_image_display(self):
        if not self.image_label.pixmap():
            return

        pixmap = self.original_pixmap.copy()
        painter = QPainter(pixmap)
        painter.setPen(QPen(QColor(255, 0, 0), 2))

        if self.current_rect:
            painter.drawRect(self.current_rect)

        painter.end()

        # Масштабируем pixmap для отображения в label
        scaled_pixmap = pixmap.scaled(
            self.image_label.width(),
            self.image_label.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

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
            'run_id': int(self.run_id_edit.text()) if self.run_id_edit.text() else  None,
            "image_path": self.image_path,
            "image_name": self.name_edit.text(),
            "center_x": int(self.center_x_edit.text()) if self.center_x_edit.text() else  None,
            "center_y": int(self.center_y_edit.text()) if self.center_y_edit.text() else None,
            "width": int(self.center_y_edit.text()) if self.center_y_edit.text() else None,
            "height": int(self.height_edit.text()) if self.height_edit.text() else None,
            "attack_type": self.attack_type_combo.currentText()
        }
    def accept(self):
        try:
            data = self.get_data()
            create_image(run_id=data['run_id'],
                         file_path=data['image_path'],
                         attack_type=data['attack_type'],
                         original_name=data['image_name'],
                         coordinates=[data['center_x'], data['center_y'],data['width'],data['height']])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить изображение: {str(e)}")

        super().accept()

from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QCheckBox,
    QPushButton, QTableWidget, QTableWidgetItem, QScrollArea, QLabel, QMessageBox, QSizePolicy, QDialog, QHeaderView,
    QAbstractItemView, QDateEdit, QTextEdit, QLineEdit, QDoubleSpinBox, QComboBox
)
from PySide6.QtCore import Qt

from db.models import AttackTypeEnum
from db.requests import get_all_experiments, update_experiment, delete_experiment, get_experiment_by_id, get_all_runs, \
    delete_run, update_run, get_run_by_id, delete_image, update_image, get_all_images, get_image_by_id, \
    get_all_images_filtered


class ViewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Просмотр данных")
        self.setFixedSize(350, 180)

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
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.btn_experiments = QPushButton("Посмотреть эксперименты")
        self.btn_runs = QPushButton("Посмотреть прогоны")
        self.btn_images = QPushButton("Посмотреть изображения")

        layout.addWidget(self.btn_experiments)
        layout.addWidget(self.btn_runs)
        layout.addWidget(self.btn_images)

        self.setLayout(layout)

        self.btn_experiments.clicked.connect(self.show_experiments)
        self.btn_runs.clicked.connect(self.show_runs)
        self.btn_images.clicked.connect(self.show_images)

    def show_experiments(self):
        self.exp_dialog = ExperimentsTableDialog(self)
        self.exp_dialog.show()
    def show_runs(self):
        self.exp_dialog = RunsTableDialog(self)
        self.exp_dialog.show()
    def show_images(self):
        self.exp_dialog = ImagesTableDialog(self)
        self.exp_dialog.show()

class BaseTableDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        layout.addWidget(self.table)
        self.setLayout(layout)

    def add_edit_button(self, row, item_id):
        edit_btn = QPushButton("Редактировать")
        edit_btn.clicked.connect(lambda checked, id=item_id: self.edit_item(id))
        self.table.setCellWidget(row, self.table.columnCount()-1, edit_btn)


class BaseEditDialog(QDialog):

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item
        self.setFixedSize(500, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Принять изменения")
        self.delete_btn = QPushButton("Удалить")
        self.cancel_btn = QPushButton("Отмена")

        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.save_btn.clicked.connect(self.save_changes)
        self.delete_btn.clicked.connect(self.delete_item)
        self.cancel_btn.clicked.connect(self.reject)


class ExperimentsTableDialog(BaseTableDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Таблица экспериментов")
        self.load_data()

    def get_columns(self):
        return ["ID", "Название", "Описание", "Дата создания", "Действия"]

    def load_data(self):
        result = get_all_experiments()

        self.table.setColumnCount(len(self.get_columns()))
        self.table.setHorizontalHeaderLabels(self.get_columns())

        self.table.setRowCount(len(result))

        for row, exp in enumerate(result):
            id_item = QTableWidgetItem(str(exp.experiment_id))
            name_item = QTableWidgetItem(exp.name or "")
            desc_item = QTableWidgetItem(exp.description or "")
            date_item = QTableWidgetItem(str(exp.created_date))

            for item in [id_item, name_item, desc_item, date_item]:
                item.setFlags(Qt.ItemIsEnabled)

            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, name_item)
            self.table.setItem(row, 2, desc_item)
            self.table.setItem(row, 3, date_item)

            self.add_edit_button(row, exp.experiment_id)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)

    def edit_item(self, experiment_id):
        experiment = get_experiment_by_id(experiment_id)
        dialog = EditExperimentDialog(experiment, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()


class EditExperimentDialog(BaseEditDialog):
    def __init__(self, experiment, parent=None):
        super().__init__(experiment, parent)
        self.setWindowTitle("Редактирование эксперимента")
        self.setup_fields()

    def setup_fields(self):
        main_layout = self.layout()

        fields_layout = QVBoxLayout()

        fields_layout.addWidget(QLabel("ID:"))
        self.id_label = QLabel(str(self.item.experiment_id))
        fields_layout.addWidget(self.id_label)

        fields_layout.addWidget(QLabel("Дата создания:"))
        self.date_label = QLabel(str(self.item.created_date))
        fields_layout.addWidget(self.date_label)

        fields_layout.addWidget(QLabel("Название:"))
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.item.name or "")
        fields_layout.addWidget(self.name_edit)

        fields_layout.addWidget(QLabel("Описание:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlainText(self.item.description or "")
        fields_layout.addWidget(self.desc_edit)

        main_layout.insertLayout(0, fields_layout)

    def save_changes(self):
        name = self.name_edit.text()
        description = self.desc_edit.toPlainText()

        try:
            update_experiment(self.item.experiment_id, name, description)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить эксперимент: {str(e)}")

    def delete_item(self):
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить этот эксперимент?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                delete_experiment(self.item.experiment_id)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить эксперимент: {str(e)}")


class RunsTableDialog(BaseTableDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Таблица прогонов")
        self.load_data()

    def get_columns(self):
        return ["ID", "ID эксперимента", "Время запуска", "Точность", "Проверен", "Действия"]

    def load_data(self):
        result = get_all_runs()

        self.table.setColumnCount(len(self.get_columns()))
        self.table.setHorizontalHeaderLabels(self.get_columns())

        self.table.setRowCount(len(result))

        for row, run in enumerate(result):
            id_item = QTableWidgetItem(str(run.run_id))
            exp_id_item = QTableWidgetItem(str(run.experiment_id))
            time_item = QTableWidgetItem(str(run.run_date))
            accuracy_item = QTableWidgetItem(str(run.accuracy))
            flagged_item = QTableWidgetItem("Да" if run.flagged else "Нет")

            for item in [id_item, exp_id_item, time_item, accuracy_item, flagged_item]:
                item.setFlags(Qt.ItemIsEnabled)

            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, exp_id_item)
            self.table.setItem(row, 2, time_item)
            self.table.setItem(row, 3, accuracy_item)
            self.table.setItem(row, 4, flagged_item)

            self.add_edit_button(row, run.run_id)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)

    def edit_item(self, run_id):
        run = get_run_by_id(run_id)
        dialog = EditRunDialog(run, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()


class EditRunDialog(BaseEditDialog):
    def __init__(self, run, parent=None):
        super().__init__(run, parent)
        self.setWindowTitle("Редактирование прогона")
        self.setup_fields()

    def setup_fields(self):
        main_layout = self.layout()

        fields_layout = QVBoxLayout()

        fields_layout.addWidget(QLabel("ID:"))
        self.id_label = QLabel(str(self.item.run_id))
        fields_layout.addWidget(self.id_label)

        fields_layout.addWidget(QLabel("ID эксперимента:"))
        self.exp_id_label = QLabel(str(self.item.experiment_id))
        fields_layout.addWidget(self.exp_id_label)

        fields_layout.addWidget(QLabel("Время запуска:"))
        self.time_label = QLabel(str(self.item.run_date))
        fields_layout.addWidget(self.time_label)

        fields_layout.addWidget(QLabel("Точность:"))
        self.accuracy_spin = QDoubleSpinBox()
        self.accuracy_spin.setRange(0.0, 1.0)
        self.accuracy_spin.setSingleStep(0.01)
        self.accuracy_spin.setDecimals(4)
        self.accuracy_spin.setValue(self.item.accuracy)
        fields_layout.addWidget(self.accuracy_spin)

        fields_layout.addWidget(QLabel("Проверен:"))
        self.verified_checkbox = QCheckBox()
        self.verified_checkbox.setText("Да")
        self.verified_checkbox.setChecked(self.item.flagged if self.item.flagged else False)
        fields_layout.addWidget(self.verified_checkbox)

        main_layout.insertLayout(0, fields_layout)

    def save_changes(self):
        accuracy = self.accuracy_spin.value()
        flagged = self.verified_checkbox.isChecked()

        try:
            update_run(self.item.run_id, accuracy, flagged)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить прогон: {str(e)}")

    def delete_item(self):
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить этот прогон?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                delete_run(self.item.run_id)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить прогон: {str(e)}")


class ImagesTableDialog(BaseTableDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Таблица изображений")
        self.filters = {
            'sort_id': None,
            'sort_run_id': None,
            'sort_experiment_id': None,
            'attack_type': None
        }
        self.init_filters()
        self.load_data()

    def init_filters(self):
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)

        filter_layout.addWidget(QLabel("Сортировка ID:"))
        self.sort_id_combo = QComboBox()
        self.sort_id_combo.addItem("Не сортировать", None)
        self.sort_id_combo.addItem("По возрастанию", 'asc')
        self.sort_id_combo.addItem("По убыванию", 'desc')
        self.sort_id_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.sort_id_combo)

        filter_layout.addWidget(QLabel("Сортировка ID прогона:"))
        self.sort_run_id_combo = QComboBox()
        self.sort_run_id_combo.addItem("Не сортировать", None)
        self.sort_run_id_combo.addItem("По возрастанию", 'asc')
        self.sort_run_id_combo.addItem("По убыванию", 'desc')
        self.sort_run_id_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.sort_run_id_combo)

        filter_layout.addWidget(QLabel("Сортировка ID эксперимента:"))
        self.sort_experiment_id_combo = QComboBox()
        self.sort_experiment_id_combo.addItem("Не сортировать", None)
        self.sort_experiment_id_combo.addItem("По возрастанию", 'asc')
        self.sort_experiment_id_combo.addItem("По убыванию", 'desc')
        self.sort_experiment_id_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.sort_experiment_id_combo)

        filter_layout.addWidget(QLabel("Тип атаки:"))
        self.attack_type_combo = QComboBox()
        self.attack_type_combo.addItem("Все типы", None)
        for attack_type in AttackTypeEnum:
            self.attack_type_combo.addItem(attack_type.value, attack_type.value)
        self.attack_type_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.attack_type_combo)

        self.reset_btn = QPushButton("Сбросить фильтры")
        self.reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.reset_btn)

        main_layout = self.layout()
        main_layout.insertWidget(0, filter_widget)

    def apply_filters(self):
        self.filters['sort_id'] = self.sort_id_combo.currentData()
        self.filters['sort_run_id'] = self.sort_run_id_combo.currentData()
        self.filters['sort_experiment_id'] = self.sort_experiment_id_combo.currentData()
        self.filters['attack_type'] = self.attack_type_combo.currentData()

        self.load_data()

    def reset_filters(self):
        self.sort_id_combo.setCurrentIndex(0)
        self.sort_run_id_combo.setCurrentIndex(0)
        self.sort_experiment_id_combo.setCurrentIndex(0)
        self.attack_type_combo.setCurrentIndex(0)
        self.filters = {
            'sort_id': None,
            'sort_run_id': None,
            'sort_experiment_id': None,
            'attack_type': None
        }
        self.load_data()

    def get_columns(self):
        return ["ID", "ID прогона", "ID эксперимента", "Путь к файлу", "Оригинальное имя", "Дата добавления", "Координаты", "Тип атаки",
                "Действия"]

    def load_data(self):
        result = get_all_images_filtered(self.filters)

        self.table.setColumnCount(len(self.get_columns()))
        self.table.setHorizontalHeaderLabels(self.get_columns())

        self.table.setRowCount(len(result))

        for row, image in enumerate(result):
            id_item = QTableWidgetItem(str(image.image_id))
            run_id_item = QTableWidgetItem(str(image.run_id))
            experiment_item = QTableWidgetItem(str(getattr(image, 'experiment_id', '')))
            path_item = QTableWidgetItem(image.file_path)
            name_item = QTableWidgetItem(image.original_name)
            date_item = QTableWidgetItem(str(image.added_date))
            coords_item = QTableWidgetItem(str(image.coordinates))
            attack_item = QTableWidgetItem(image.attack_type)

            for item in [id_item, run_id_item, experiment_item, path_item, name_item, date_item, coords_item,
                         attack_item]:
                item.setFlags(Qt.ItemIsEnabled)

            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, run_id_item)
            self.table.setItem(row, 2, experiment_item)
            self.table.setItem(row, 3, path_item)
            self.table.setItem(row, 4, name_item)
            self.table.setItem(row, 5, date_item)
            self.table.setItem(row, 6, coords_item)
            self.table.setItem(row, 7, attack_item)

            self.add_edit_button(row, image.image_id)

        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)

    def edit_item(self, image_id):
        image = get_image_by_id(image_id)
        dialog = EditImageDialog(image, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_data()


class EditImageDialog(BaseEditDialog):
    def __init__(self, image, parent=None):
        super().__init__(image, parent)
        self.setWindowTitle("Редактирование изображения")
        self.setMinimumSize(500, 500)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setup_fields()

        self.adjustSize()

    def setup_fields(self):
        main_layout = self.layout()

        fields_layout = QVBoxLayout()

        fields_layout.addWidget(QLabel("ID:"))
        self.id_label = QLabel(str(self.item.image_id))
        fields_layout.addWidget(self.id_label)

        fields_layout.addWidget(QLabel("ID прогона:"))
        self.run_id_label = QLabel(str(self.item.run_id))
        fields_layout.addWidget(self.run_id_label)

        fields_layout.addWidget(QLabel("Путь к файлу:"))
        self.path_label = QLabel(self.item.file_path)
        fields_layout.addWidget(self.path_label)

        fields_layout.addWidget(QLabel("Оригинальное имя:"))
        self.name_label = QLabel(self.item.original_name)
        fields_layout.addWidget(self.name_label)

        fields_layout.addWidget(QLabel("Дата добавления:"))
        self.date_label = QLabel(str(self.item.added_date))
        fields_layout.addWidget(self.date_label)

        fields_layout.addWidget(QLabel("Координаты:"))
        self.coords_label = QLabel(str(self.item.coordinates))
        fields_layout.addWidget(self.coords_label)

        fields_layout.addWidget(QLabel("Тип атаки:"))
        self.attack_type_combo = QComboBox()
        for attack_type in AttackTypeEnum:
            self.attack_type_combo.addItem(attack_type.value, attack_type)
        current_index = self.attack_type_combo.findData(AttackTypeEnum(self.item.attack_type))
        if current_index >= 0:
            self.attack_type_combo.setCurrentIndex(current_index)
        fields_layout.addWidget(self.attack_type_combo)

        main_layout.insertLayout(0, fields_layout)

    def save_changes(self):
        attack_type = self.attack_type_combo.currentData()

        try:
            update_image(self.item.image_id, attack_type)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить изображение: {str(e)}")

    def delete_item(self):
        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            "Вы уверены, что хотите удалить это изображение?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                delete_image(self.item.image_id)
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить изображение: {str(e)}")
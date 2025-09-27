from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QPushButton, QWidget, QVBoxLayout,
                               )
from gui.add_widget import ChoiceDialog, MergeAddWindows
from gui.connect_widget import ConnectionDialog
from gui.styles import styles
from gui.view_widget import ViewDialog, MergeViewWindows


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.logger_window = None
        self.setWindowTitle("Главное окно")
        self.setFixedSize(400, 300)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.setStyleSheet(styles)

        layout = QVBoxLayout(central_widget)

        self.connect_btn = QPushButton("Подключиться к БД")
        self.connect_btn.clicked.connect(self.open_connection)
        layout.addWidget(self.connect_btn)

        self.add_btn = QPushButton("Вставить данные")
        self.add_btn.clicked.connect(self.open_dialog)
        layout.addWidget(self.add_btn)

        self.view_btn = QPushButton("Посмотреть данные")
        self.view_btn.clicked.connect(self.open_view)
        layout.addWidget(self.view_btn)

        self._update_ui_state()

    def _update_ui_state(self):

        ever_connected = False
        try:
            ever_connected = bool(getattr(ConnectionDialog, "_ever_connected", False))
        except Exception:
            ever_connected = False

        self.add_btn.setEnabled(ever_connected)
        self.view_btn.setEnabled(ever_connected)
        self.connect_btn.setEnabled(True)

    def open_connection(self):
        dialog = ConnectionDialog(self)
        dialog.connected.connect(self._on_db_connected)
        dialog.exec()
        self._update_ui_state()

    def _on_db_connected(self, connection_info):
        self._update_ui_state()

    def open_dialog(self):
        dialog = MergeAddWindows()
        dialog.show()

    def open_view(self):
        dialog = MergeViewWindows()
        dialog.show()
import logging
from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout,
                               QWidget, QPushButton, QHBoxLayout, QLabel)
from PySide6.QtCore import Qt, QObject, Signal
from typing import Optional
from datetime import datetime


class LogEmitter(QObject):
    log_signal = Signal(str)


class LoggerWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Validation Logger")
        self.setGeometry(100, 100, 800, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("Логгер запущен. Ожидание ошибок валидации...")
        layout.addWidget(self.status_label)

        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setPlaceholderText("Здесь будут отображаться ошибки валидации...")
        layout.addWidget(self.log_text_edit)

        button_layout = QHBoxLayout()

        clear_btn = QPushButton("Очистить")
        clear_btn.clicked.connect(self.clear_logs)
        button_layout.addWidget(clear_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        self.log_emitter = LogEmitter()
        self.log_emitter.log_signal.connect(self.append_log)

        self.add_startup_message()

    def add_startup_message(self):
        startup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        welcome_message = f"Логгер запущен {startup_time}"
        self.log_text_edit.append(welcome_message)
        self.status_label.setText("Логгер активен. Ожидание ошибок")

    def append_log(self, message: str):
        self.log_text_edit.append(message)
        self.status_label.setText("Обнаружены ошибки валидации")
        self.log_text_edit.verticalScrollBar().setValue(
            self.log_text_edit.verticalScrollBar().maximum()
        )

    def clear_logs(self):
        self.log_text_edit.clear()
        self.add_startup_message()
        self.status_label.setText("Логи очищены. Ожидание ошибок...")

    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()


class QtLoggerHandler(logging.Handler):
    def __init__(self, log_window: LoggerWindow):
        super().__init__()
        self.log_window = log_window
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    def emit(self, record):
        try:
            log_message = self.format(record)
            self.log_window.log_emitter.log_signal.emit(log_message)
        except Exception:
            pass


_logger_window: Optional[LoggerWindow] = None
_qt_handler: Optional[QtLoggerHandler] = None


def initialize_qt_logger() -> LoggerWindow:
    global _logger_window, _qt_handler

    if _logger_window is None:
        _logger_window = LoggerWindow()

        _qt_handler = QtLoggerHandler(_logger_window)
        _qt_handler.setLevel(logging.ERROR)

        root_logger = logging.getLogger()

        for handler in root_logger.handlers[:]:
            if isinstance(handler, QtLoggerHandler):
                root_logger.removeHandler(handler)

        root_logger.addHandler(_qt_handler)
        root_logger.setLevel(logging.ERROR)

        validation_logger = logging.getLogger('validation')
        validation_logger.addHandler(_qt_handler)
        validation_logger.setLevel(logging.ERROR)

        _logger_window.show()
        _logger_window.raise_()
        _logger_window.activateWindow()

    return _logger_window


def get_qt_logger() -> LoggerWindow:
    if _logger_window is None:
        return initialize_qt_logger()
    return _logger_window
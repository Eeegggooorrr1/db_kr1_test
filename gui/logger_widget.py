import logging
from PySide6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout,
                               QWidget, QPushButton, QHBoxLayout, QLabel)
from PySide6.QtCore import Qt, QObject, Signal
from typing import Optional
from datetime import datetime

from gui.styles import styles


class LogEmitter(QObject):
    log_signal = Signal(str)


class LoggerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
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
        self.setStyleSheet(styles)

    def add_startup_message(self):
        startup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        welcome_message = f"Логгер запущен {startup_time}"
        self.log_text_edit.append(welcome_message)

    def append_log(self, message: str):
        self.log_text_edit.append(message)
        self.log_text_edit.verticalScrollBar().setValue(
            self.log_text_edit.verticalScrollBar().maximum()
        )

    def clear_logs(self):
        self.log_text_edit.clear()
        self.add_startup_message()


class QtLoggerHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_emitter = LogEmitter()
        self.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self._log_buffer = []

    def set_log_widget(self, log_widget: LoggerWidget):
        self.log_widget = log_widget
        self.log_emitter.log_signal.connect(self.log_widget.append_log)
        for log_message in self._log_buffer:
            self.log_emitter.log_signal.emit(log_message)
        self._log_buffer.clear()

    def emit(self, record):
        try:
            log_message = self.format(record)
            if hasattr(self, 'log_widget') and self.log_widget:
                self.log_emitter.log_signal.emit(log_message)
            else:
                self._log_buffer.append(log_message)
        except Exception:
            pass


logger_widget = None
_qt_handler = None
def initialize_qt_logger():
    global _qt_handler

    if _qt_handler is None:
        _qt_handler = QtLoggerHandler()
        _qt_handler.setLevel(logging.INFO)
        root_logger = logging.getLogger()

        for logger in (root_logger, logging.getLogger('validation')):
            for handler in logger.handlers[:]:
                if isinstance(handler, QtLoggerHandler):
                    logger.removeHandler(handler)

        root_logger.addHandler(_qt_handler)
        root_logger.setLevel(logging.INFO)

        validation_logger = logging.getLogger('validation')
        validation_logger.setLevel(logging.INFO)

    return _qt_handler


def get_qt_logger_widget(parent_widget=None):
    global logger_widget

    if logger_widget is None:
        logger_widget = LoggerWidget(parent_widget)
        if _qt_handler:
            _qt_handler.set_log_widget(logger_widget)

    return logger_widget


def setup_logging():
    initialize_qt_logger()


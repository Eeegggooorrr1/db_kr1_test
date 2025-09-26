import sys
from PySide6.QtWidgets import QApplication

from gui.logger_widget import setup_logging
from gui.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    setup_logging()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


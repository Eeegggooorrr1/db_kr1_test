styles = """
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
    QPushButton:disabled {
        background-color: #c0c0c0;
        color: #888888;
    }

    QComboBox {
        background-color: white;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        padding: 5px 10px;
        min-width: 100px;
        min-height: 20px;
    }
    
    QComboBox QAbstractItemView {
        background-color: white;
        border: 1px solid #d0d0d0;
        selection-background-color: #e0e0e0;
        outline: 0;
    }
    QTableView {
        background-color: white;
        alternate-background-color: #f8f8f8;
        border: 1px solid #d0d0d0;
        gridline-color: #e0e0e0;
        border-radius: 4px;
    }
    QTableView::item {
        padding: 5px;
        border-bottom: 1px solid #f0f0f0;
    }
    QTableView::item:selected {
        background-color: #e0e0e0;
        color: black;
    }
    QHeaderView::section {
        background-color: #e8e8e8;
        padding: 8px;
        border: none;
        border-right: 1px solid #d0d0d0;
        border-bottom: 1px solid #d0d0d0;
        font-weight: bold;
    }

    QScrollBar:vertical {
        background-color: #f0f0f0;
        width: 12px;
        margin: 0px;
    }
    QScrollBar::handle:vertical {
        background-color: #c0c0c0;
        border-radius: 6px;
        min-height: 20px;
        margin: 3px;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #a0a0a0;
    }
    QScrollBar::add-line:vertical, 
    QScrollBar::sub-line:vertical {
        height: 0px;
    }

    QScrollBar:horizontal {
        background-color: #f0f0f0;
        height: 12px;
        margin: 0px;
    }
    QScrollBar::handle:horizontal {
        background-color: #c0c0c0;
        border-radius: 6px;
        min-width: 20px;
        margin: 3px;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #a0a0a0;
    }

    QLineEdit {
        background-color: white;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        padding: 5px 8px;
        font-size: 14px;
    }
    QLabel {
        color: #333333;
        font-size: 14px;
    }
    QProgressBar {
        background-color: #e0e0e0;
        border-radius: 4px;
        text-align: center;
        color: #333333;
    }
    QProgressBar::chunk {
        background-color: #4a86e8;
        border-radius: 4px;
    }
    QDoubleSpinBox {
        background-color: white;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        padding: 5px 8px;
        font-size: 14px;
        min-width: 80px;
    }
    QDoubleSpinBox:focus {
        border: 1px solid #4a86e8;
    }
    QDoubleSpinBox::up-button {
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid #d0d0d0;
        border-top-right-radius: 3px;
        background-color: #e8e8e8;
    }
    QDoubleSpinBox::up-button:hover {
        background-color: #d8d8d8;
    }
    QDoubleSpinBox::up-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-bottom: 5px solid #666666;
        width: 0px;
        height: 0px;
    }
    QDoubleSpinBox::down-button {
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 20px;
        border-left: 1px solid #d0d0d0;
        border-bottom-right-radius: 3px;
        background-color: #e8e8e8;
    }
    QDoubleSpinBox::down-button:hover {
        background-color: #d8d8d8;
    }
    QDoubleSpinBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid #666666;
        width: 0px;
        height: 0px;
    }
    
    QCheckBox {
        spacing: 8px;
        color: #333333;
        font-size: 14px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #d0d0d0;
        border-radius: 3px;
        background-color: white;
    }
    QCheckBox::indicator:hover {
        border: 1px solid #b0b0b0;
    }
    QCheckBox::indicator:checked {
        background-color: #4a86e8;
        border: 1px solid #4a86e8;
    }
    QCheckBox::indicator:checked:hover {
        background-color: #3a76d8;
        border: 1px solid #3a76d8;
    }
    QCheckBox::indicator:checked:pressed {
        background-color: #2a66c8;
        border: 1px solid #2a66c8;
    }
    QCheckBox::indicator:checked:disabled {
        background-color: #c0c0c0;
        border: 1px solid #c0c0c0;
    }
    QCheckBox::indicator:unchecked:disabled {
        background-color: #f0f0f0;
        border: 1px solid #e0e0e0;
    }

    
    QTextEdit {
        background-color: white;
        border: 1px solid #d0d0d0;
        border-radius: 4px;
        padding: 8px;
        font-size: 14px;
        selection-background-color: #4a86e8;
        color: #333333;
    }
    QTextEdit:focus {
        border: 1px solid #4a86e8;
    }
    QTextEdit:disabled {
        background-color: #f8f8f8;
        color: #888888;
    }
    
"""

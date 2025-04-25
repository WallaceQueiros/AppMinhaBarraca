light_theme = """
    QWidget {
        background-color: #ffffff;
        color: #222;
        font-family: "Helvetica";
        font-size: 14px;
    }
    QLineEdit, QComboBox {
        background-color: white;
        padding: 6px;
        border: 1px solid #ccc;
        border-radius: 6px;
    }
    QPushButton {
        background-color: #3f80ff;
        color: white;
        padding: 10px;
        border-radius: 8px;
    }
    QPushButton:hover {
        background-color: #5a95ff;
    }
    QTableWidget {
        background-color: #ffffff;
        color: #222;
        gridline-color: #ccc;
        border: 1px solid #aaa;
        selection-background-color: #d0e1ff;
        selection-color: #000;
    }
    QHeaderView::section {
        background-color: #f0f0f0;
        color: #222;
        font-weight: bold;
        border: 1px solid #ccc;
        padding: 5px;
    }
"""

dark_theme = """
    QWidget {
        background-color: #121212;
        color: #eee;
        font-family: "Helvetica";
        font-size: 14px;
    }
    QLineEdit, QComboBox {
        background-color: #2c2c2c;
        padding: 6px;
        border: 1px solid #444;
        border-radius: 6px;
        color: white;
    }
    QPushButton {
        background-color: #3f80ff;
        color: white;
        padding: 10px;
        border-radius: 8px;
    }
    QPushButton:hover {
        background-color: #5a95ff;
    }

    QTableWidget {
        background-color: #1e1e1e;
        color: #fff;
        gridline-color: #444;
        border: 1px solid #444;
    }
    QTableWidget QTableCornerButton::section {
        background-color: #2c2c2c;
        border: 1px solid #444;
    }
    QHeaderView::section {
        background-color: #3f80ff;
        color: #fff;
        padding: 4px;
        border: 1px solid #444;
    }
    QScrollBar:vertical {
        background-color: #2c2c2c;
        width: 12px;
    }
    QScrollBar::handle:vertical {
        background-color: #555;
        border-radius: 6px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        background: none;
    }
"""


from enum import Enum

class Theme(Enum):
    DEFAULT = "default"
    RETRO = "retro"
    WIN98 = "win98"

DEFAULT_STYLE = """
/* Стандартная тема Qt */

/* Декоративные элементы для стандартной темы */
.default-border {
    border: 1px solid #a0a0a0;
    border-radius: 5px;
    padding: 10px;
    margin: 5px;
}

.default-led {
    background-color: #4CAF50;
    border-radius: 3px;
    min-height: 6px;
    max-height: 6px;
    margin: 3px;
}

.default-display {
    background-color: #f5f5f5;
    border: 1px solid #a0a0a0;
    border-radius: 3px;
    color: #333333;
    padding: 8px;
    font-family: Arial;
}

.retro-display, .win98-display {
    /* Сброс стилей для других тем */
    background-color: transparent;
    border: none;
    color: inherit;
    padding: 5px;
    font-family: inherit;
    font-weight: normal;
}

.retro-led, .win98-led {
    /* Сброс стилей для других тем */
    background-color: transparent;
    border-radius: 0;
    min-height: 0;
    max-height: none;
    margin: 0;
}
"""

RETRO_STYLE = """
QMainWindow {
    background-color: #2F3437;
    color: #E8DDB5;
}

QWidget {
    background-color: #2F3437;
    color: #E8DDB5;
    font-family: "Courier New";
}

QPushButton {
    background-color: #1C1F22;
    border: 2px solid #E8DDB5;
    border-radius: 5px;
    color: #E8DDB5;
    padding: 5px;
    font-weight: bold;
    min-height: 30px;
}

QPushButton:hover {
    background-color: #4A5459;
}

QPushButton:pressed {
    background-color: #E8DDB5;
    color: #1C1F22;
}

QLabel {
    color: #E8DDB5;
    font-family: "Courier New";
}

QListWidget {
    background-color: #1C1F22;
    border: 2px solid #E8DDB5;
    border-radius: 5px;
    color: #E8DDB5;
    padding: 5px;
}

QListWidget::item {
    padding: 5px;
    border-radius: 3px;
}

QListWidget::item:selected {
    background-color: #4A5459;
}

QProgressBar {
    border: 2px solid #E8DDB5;
    border-radius: 5px;
    text-align: center;
    background-color: #1C1F22;
}

QProgressBar::chunk {
    background-color: #E8DDB5;
}

QComboBox {
    background-color: #1C1F22;
    border: 2px solid #E8DDB5;
    border-radius: 5px;
    color: #E8DDB5;
    padding: 5px;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #E8DDB5;
    width: 0;
    height: 0;
    margin-right: 5px;
}

QSpinBox, QDoubleSpinBox {
    background-color: #1C1F22;
    border: 2px solid #E8DDB5;
    border-radius: 5px;
    color: #E8DDB5;
    padding: 5px;
}

QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #4A5459;
    border: none;
}

QMessageBox {
    background-color: #2F3437;
    color: #E8DDB5;
}

QMessageBox QPushButton {
    min-width: 80px;
}

/* Декоративные элементы */
.retro-border {
    border: 3px solid #E8DDB5;
    border-radius: 10px;
    padding: 15px;
    margin: 10px;
}

.retro-display {
    background-color: #1C1F22;
    border: 2px solid #E8DDB5;
    border-radius: 5px;
    color: #E8DDB5;
    padding: 10px;
    font-family: "Courier New";
    font-weight: bold;
}

.retro-led {
    background-color: #E8DDB5;
    border-radius: 5px;
    min-height: 10px;
    max-height: 10px;
    margin: 5px;
}
"""

WIN98_STYLE = """
QMainWindow, QWidget {
    background-color: #c0c0c0;
    color: #000000;
    font-family: "MS Sans Serif";
}

QPushButton {
    background-color: #c0c0c0;
    border: 2px solid #808080;
    border-style: solid;
    border-width: 2px;
    border-top-color: #ffffff;
    border-left-color: #ffffff;
    border-right-color: #000000;
    border-bottom-color: #000000;
    padding: 5px;
    min-height: 25px;
    color: #000000;
}

QPushButton:hover {
    background-color: #d4d4d4;
}

QPushButton:pressed {
    border-top-color: #000000;
    border-left-color: #000000;
    border-right-color: #ffffff;
    border-bottom-color: #ffffff;
    background-color: #c0c0c0;
}

QLabel {
    color: #000000;
}

QListWidget {
    background-color: #ffffff;
    border: 2px solid #808080;
    border-style: solid;
    border-width: 2px;
    border-top-color: #000000;
    border-left-color: #000000;
    border-right-color: #ffffff;
    border-bottom-color: #ffffff;
}

QListWidget::item:selected {
    background-color: #000080;
    color: #ffffff;
}

QProgressBar {
    border: 2px solid #808080;
    border-style: solid;
    text-align: center;
    background-color: #ffffff;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #000080;
}

QComboBox {
    background-color: #ffffff;
    border: 2px solid #808080;
    border-style: solid;
    border-width: 2px;
    border-top-color: #000000;
    border-left-color: #000000;
    border-right-color: #ffffff;
    border-bottom-color: #ffffff;
    padding: 5px;
}

QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 2px solid #808080;
    border-style: solid;
    border-width: 2px;
    border-top-color: #000000;
    border-left-color: #000000;
    border-right-color: #ffffff;
    border-bottom-color: #ffffff;
    padding: 5px;
}

QMessageBox {
    background-color: #c0c0c0;
}

/* Windows 98 специфичные стили */
.title-bar {
    background-color: #000080;
    color: #ffffff;
    padding: 2px;
    font-weight: bold;
}

.window-body {
    background-color: #c0c0c0;
    padding: 8px;
}

.win98-border {
    border: 2px solid #808080;
    border-style: solid;
    border-width: 2px;
    border-top-color: #ffffff;
    border-left-color: #ffffff;
    border-right-color: #000000;
    border-bottom-color: #000000;
    padding: 10px;
    margin: 5px;
}

.win98-led {
    background-color: #00aa00;
    border: 1px solid #008800;
    border-radius: 2px;
    min-height: 8px;
    max-height: 8px;
    margin: 5px;
}

.win98-display {
    background-color: #ffffff;
    border: 2px solid #808080;
    border-style: solid;
    border-width: 2px;
    border-top-color: #000000;
    border-left-color: #000000;
    border-right-color: #ffffff;
    border-bottom-color: #ffffff;
    padding: 5px;
    color: #000000;
}

/* Мобильные стили */
@media screen and (max-width: 768px) {
    QMainWindow {
        background: #008080;
    }

    .window {
        width: 100%;
        margin: 0;
        border: none;
        box-shadow: none;
    }

    .title-bar {
        top: 20;
        left: 0;
        right: 0;
        z-index: 100;
    }

    .window-body {
        margin-top: 40px;
        padding: 8px;
    }

    QPushButton {
        width: 100%;
        margin: 4px 0;
        padding: 12px;
    }

    QComboBox, QSpinBox, QDoubleSpinBox {
        width: 100%;
    }
}
""" 
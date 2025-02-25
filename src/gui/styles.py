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
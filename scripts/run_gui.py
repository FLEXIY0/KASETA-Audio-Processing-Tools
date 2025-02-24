import os
import sys
import signal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QPushButton, QLabel)
from PyQt5.QtCore import Qt, QTimer

# Добавляем корневую директорию проекта в путь поиска модулей
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from src.gui.converter_window import ConverterWindow
from src.gui.merger_window import MergerWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Аудио Инструменты')
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Заголовок
        title = QLabel('Выберите режим работы:')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Кнопка конвертера
        converter_button = QPushButton('Конвертер аудио файлов')
        converter_button.clicked.connect(self.open_converter)
        layout.addWidget(converter_button)

        # Кнопка сшивателя
        merger_button = QPushButton('Объединение аудио файлов')
        merger_button.clicked.connect(self.open_merger)
        layout.addWidget(merger_button)

        self.show()

    def open_converter(self):
        """Открытие окна конвертации"""
        self.converter = ConverterWindow(self)
        self.converter.show()
        self.hide()

    def open_merger(self):
        """Открытие окна сшивания"""
        self.merger = MergerWindow(self)
        self.merger.show()
        self.hide()

    def closeEvent(self, event):
        """Обработчик закрытия главного окна"""
        # Закрываем все дочерние окна
        if hasattr(self, 'converter'):
            self.converter.close()
        if hasattr(self, 'merger'):
            self.merger.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Обработка CTRL+C
    def signal_handler(signum, frame):
        print("\nПолучен сигнал завершения. Закрываем приложение...")
        window.close()
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Таймер для обработки системных сигналов
    def process_signals():
        import time
        time.sleep(0.01)
    
    timer = QTimer()
    timer.timeout.connect(process_signals)
    timer.start(100)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 
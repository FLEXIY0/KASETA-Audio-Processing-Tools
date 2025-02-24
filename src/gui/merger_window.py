import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton, QFileDialog, QListWidget,
                           QListWidgetItem, QSpinBox, QDoubleSpinBox,
                           QProgressBar, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

# Добавляем корневую директорию проекта в путь поиска модулей
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

from src.core.audio_processor import AudioProcessor
from src.utils.translations import get_translator
from src.utils.paths import MUSIC_INPUT_DIR, MUSIC_OUTPUT_DIR, ensure_dirs_exist
from src.gui.confetti import ConfettiWidget

class MergeWorker(QThread):
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(bool, str)
    status = pyqtSignal(str)

    def __init__(self, input_files, output_file, pause_duration, fade_duration):
        super().__init__()
        self.input_files = input_files
        self.output_file = output_file
        self.pause_duration = pause_duration
        self.fade_duration = fade_duration
        self.translate, _ = get_translator()
        self.processor = AudioProcessor(self.translate)

    def run(self):
        try:
            self.status.emit("Подготовка к объединению файлов...")
            success = self.processor.merge_audio(
                self.input_files,
                self.output_file,
                pause_duration=self.pause_duration,
                fade_duration=self.fade_duration
            )
            
            if success:
                self.finished.emit(True, "")
            else:
                self.finished.emit(False, "Ошибка при объединении файлов")
                
        except Exception as e:
            self.finished.emit(False, str(e))

class MergerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        ensure_dirs_exist()
        self.translate, _ = get_translator()
        self.selected_files = []
        self.parent = parent
        
        # Добавляем виджет конфетти
        self.confetti = ConfettiWidget(self)
        self.confetti.hide()
        
        # Добавляем обработчик для graceful shutdown
        self.worker = None
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Объединение аудио файлов')
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Создаем все элементы интерфейса
        self.create_file_selection(layout)
        self.create_files_list(layout)
        self.create_settings_section(layout)
        self.create_progress_section(layout)
        self.create_merge_button(layout)

        # Информация о директориях
        info_label = QLabel(f"Входная директория: {MUSIC_INPUT_DIR}\nВыходная директория: {MUSIC_OUTPUT_DIR}")
        layout.addWidget(info_label)

        # Добавляем кнопку перехода к конвертации
        switch_button = QPushButton('Перейти к конвертации файлов')
        switch_button.clicked.connect(self.switch_to_converter)
        layout.addWidget(switch_button)

        # Устанавливаем размер конфетти
        self.confetti.setGeometry(0, 0, self.width(), self.height())
        
        self.show()

    def create_file_selection(self, layout):
        file_layout = QHBoxLayout()
        
        select_button = QPushButton('Выбрать файлы')
        select_button.clicked.connect(self.select_files)
        
        clear_button = QPushButton('Очистить список')
        clear_button.clicked.connect(self.clear_files)
        
        file_layout.addWidget(select_button)
        file_layout.addWidget(clear_button)
        layout.addLayout(file_layout)

    def create_files_list(self, layout):
        list_label = QLabel("Выбранные файлы (перетащите для изменения порядка):")
        layout.addWidget(list_label)
        
        self.files_list = QListWidget()
        self.files_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.files_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        layout.addWidget(self.files_list)

        # Кнопки управления списком
        buttons_layout = QHBoxLayout()
        
        remove_button = QPushButton('Удалить выбранные')
        remove_button.clicked.connect(self.remove_selected_files)
        
        move_up_button = QPushButton('↑ Вверх')
        move_up_button.clicked.connect(self.move_files_up)
        
        move_down_button = QPushButton('↓ Вниз')
        move_down_button.clicked.connect(self.move_files_down)
        
        buttons_layout.addWidget(remove_button)
        buttons_layout.addWidget(move_up_button)
        buttons_layout.addWidget(move_down_button)
        layout.addLayout(buttons_layout)

    def create_settings_section(self, layout):
        settings_layout = QHBoxLayout()
        
        # Настройка паузы
        pause_layout = QVBoxLayout()
        pause_layout.addWidget(QLabel('Пауза между треками (сек):'))
        self.pause_spin = QDoubleSpinBox()
        self.pause_spin.setRange(0, 10)
        self.pause_spin.setValue(2)
        self.pause_spin.setSingleStep(0.5)
        pause_layout.addWidget(self.pause_spin)
        settings_layout.addLayout(pause_layout)
        
        # Настройка затухания
        fade_layout = QVBoxLayout()
        fade_layout.addWidget(QLabel('Длительность затухания (сек):'))
        self.fade_spin = QDoubleSpinBox()
        self.fade_spin.setRange(0, 5)
        self.fade_spin.setValue(1)
        self.fade_spin.setSingleStep(0.5)
        fade_layout.addWidget(self.fade_spin)
        settings_layout.addLayout(fade_layout)
        
        layout.addLayout(settings_layout)

    def create_progress_section(self, layout):
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel('')
        layout.addWidget(self.status_label)

    def create_merge_button(self, layout):
        self.merge_button = QPushButton('Объединить файлы')
        self.merge_button.clicked.connect(self.start_merge)
        self.merge_button.setEnabled(False)
        layout.addWidget(self.merge_button)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            'Выберите аудио файлы',
            MUSIC_INPUT_DIR,
            'Аудио файлы (*.mp3 *.wav *.ogg *.flac *.aac)'
        )
        
        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    item = QListWidgetItem(os.path.basename(file))
                    item.setToolTip(file)
                    self.files_list.addItem(item)
            
            self.merge_button.setEnabled(len(self.selected_files) > 1)

    def clear_files(self):
        self.selected_files.clear()
        self.files_list.clear()
        self.merge_button.setEnabled(False)

    def remove_selected_files(self):
        selected_items = self.files_list.selectedItems()
        for item in selected_items:
            file_path = item.toolTip()
            self.selected_files.remove(file_path)
            self.files_list.takeItem(self.files_list.row(item))
        
        self.merge_button.setEnabled(len(self.selected_files) > 1)

    def move_files_up(self):
        current_row = self.files_list.currentRow()
        if current_row > 0:
            item = self.files_list.takeItem(current_row)
            self.files_list.insertItem(current_row - 1, item)
            self.files_list.setCurrentRow(current_row - 1)
            # Обновляем порядок в selected_files
            file_path = self.selected_files.pop(current_row)
            self.selected_files.insert(current_row - 1, file_path)

    def move_files_down(self):
        current_row = self.files_list.currentRow()
        if current_row < self.files_list.count() - 1:
            item = self.files_list.takeItem(current_row)
            self.files_list.insertItem(current_row + 1, item)
            self.files_list.setCurrentRow(current_row + 1)
            # Обновляем порядок в selected_files
            file_path = self.selected_files.pop(current_row)
            self.selected_files.insert(current_row + 1, file_path)

    def start_merge(self):
        if len(self.selected_files) < 2:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Выберите как минимум два файла для объединения'
            )
            return

        # Запрашиваем имя выходного файла
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            'Сохранить объединенный файл',
            os.path.join(MUSIC_OUTPUT_DIR, 'merged.mp3'),
            'MP3 файл (*.mp3)'
        )
        
        if not output_file:
            return

        self.worker = MergeWorker(
            self.selected_files,
            output_file,
            self.pause_spin.value(),
            self.fade_spin.value()
        )
        
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.merge_finished)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.merge_button.setEnabled(False)
        
        self.worker.start()

    def update_progress(self, current, total):
        self.progress_bar.setValue(int(current * 100 / total))

    def update_status(self, message):
        self.status_label.setText(message)

    def merge_finished(self, success, error_message=""):
        self.progress_bar.setVisible(False)
        self.merge_button.setEnabled(True)
        
        if success:
            self.confetti.raise_()
            self.confetti.start_animation()
            
            QTimer.singleShot(500, lambda: QMessageBox.information(
                self,
                'Успех',
                'Файлы успешно объединены!'
            ))
            
            self.clear_files()
        else:
            QMessageBox.critical(
                self,
                'Ошибка',
                f'Произошла ошибка при объединении файлов:\n{error_message}'
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.confetti.setGeometry(0, 0, self.width(), self.height())

    def showEvent(self, event):
        super().showEvent(event)
        self.confetti.setGeometry(0, 0, self.width(), self.height())

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                'Подтверждение',
                'Объединение файлов в процессе. Вы уверены, что хотите выйти?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.worker:
                    self.worker.terminate()
                    self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            if self.parent and not hasattr(self, 'converter'):
                self.parent.show()
            event.accept()

    def switch_to_converter(self):
        """Переключение на окно конвертации"""
        # Импортируем здесь, чтобы избежать циклических импортов
        from src.gui.converter_window import ConverterWindow
        self.converter = ConverterWindow(self.parent)
        self.converter.show()
        if self.parent:
            self.parent.show()
        self.close()

def main():
    app = QApplication(sys.argv)
    window = MergerWindow()
    sys.exit(app.exec()) 
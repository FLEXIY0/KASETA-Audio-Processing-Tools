import os
import sys
import signal
import traceback
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QComboBox, 
                           QFileDialog, QProgressBar, QMessageBox, QListWidget,
                           QListWidgetItem, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon

# Добавляем корневую директорию проекта в путь поиска модулей
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

from src.core.audio_processor import AudioProcessor
from src.utils.translations import get_translator
from src.utils.paths import MUSIC_INPUT_DIR, MUSIC_OUTPUT_DIR, ensure_dirs_exist
from src.gui.confetti import ConfettiWidget
from src.utils.settings import load_settings

SUPPORTED_FORMATS = {
    'MP3': {'ext': '.mp3', 'ffmpeg_codec': 'libmp3lame'},
    'OGG': {'ext': '.ogg', 'ffmpeg_codec': 'libvorbis'},
    'WAV': {'ext': '.wav', 'ffmpeg_codec': 'pcm_s16le'},
    'FLAC': {'ext': '.flac', 'ffmpeg_codec': 'flac'},
    'AAC': {'ext': '.aac', 'ffmpeg_codec': 'aac'}
}

class ConversionWorker(QThread):
    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(bool, str)
    status = pyqtSignal(str)

    def __init__(self, input_files, output_format, translate_func):
        super().__init__()
        self.input_files = input_files
        self.output_format = output_format
        self.processor = AudioProcessor(lambda x: x)
        self.translate = translate_func

    def run(self):
        try:
            total_files = len(self.input_files)
            for i, input_file in enumerate(self.input_files, 1):
                # Проверяем существование входного файла
                if not os.path.exists(input_file):
                    raise FileNotFoundError(self.translate('common.file_not_found', input_file))

                # Проверяем доступ к директории вывода
                if not os.path.exists(MUSIC_OUTPUT_DIR):
                    os.makedirs(MUSIC_OUTPUT_DIR)
                elif not os.access(MUSIC_OUTPUT_DIR, os.W_OK):
                    raise PermissionError(self.translate('converter_window.dialog.no_write_permissions', MUSIC_OUTPUT_DIR))

                output_file = os.path.join(
                    MUSIC_OUTPUT_DIR,
                    os.path.splitext(os.path.basename(input_file))[0] + 
                    SUPPORTED_FORMATS[self.output_format]['ext']
                )
                
                self.status.emit(self.translate('converter_window.dialog.converting_file', i, total_files, os.path.basename(input_file)))
                self.progress.emit(i-1, total_files)
                
                success, error = self.processor.convert_audio(
                    input_file, 
                    output_file,
                    SUPPORTED_FORMATS[self.output_format]['ffmpeg_codec']
                )
                
                if not success:
                    self.finished.emit(False, f"{self.translate('converter_window.dialog.error_conversion_file', os.path.basename(input_file))}\n{error}")
                    return

            self.progress.emit(total_files, total_files)
            self.finished.emit(True, "")
                
        except FileNotFoundError as e:
            error_msg = f"{self.translate('common.error')}: {str(e)}"
            self.status.emit(error_msg)
            self.finished.emit(False, error_msg)
        except PermissionError as e:
            error_msg = f"{self.translate('converter_window.dialog.permission_error')}: {str(e)}"
            self.status.emit(error_msg)
            self.finished.emit(False, error_msg)
        except Exception as e:
            error_msg = f"{self.translate('common.error_unexpected', str(e))}\n{traceback.format_exc()}"
            self.status.emit(error_msg)
            self.finished.emit(False, error_msg)

class ConverterWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Устанавливаем флаг для отображения в панели задач
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Window)
        
        # Флаг для контроля показа главного окна при закрытии
        self.show_main_on_close = True
        
        # Устанавливаем иконку
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets', '749.ico'))
        self.setWindowIcon(QIcon(icon_path))
        
        # Включаем поддержку перетаскивания
        self.setAcceptDrops(True)
        
        ensure_dirs_exist()
        self.translate, _ = get_translator()
        self.selected_files = []
        self.parent = parent
        
        # Добавляем виджет конфетти до init_ui
        self.confetti = ConfettiWidget(self)
        self.confetti.hide()  # Изначально скрыт
        
        # Добавляем обработчик для graceful shutdown
        self.worker = None
        
        # Инициализируем UI после создания всех атрибутов
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.translate('converter_window.title'))
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        # Создаем центральный виджет и главный layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Создаем рамку в ретро-стиле
        main_frame = QFrame()
        main_frame.setProperty('class', 'retro-border')
        main_layout = QVBoxLayout(main_frame)

        # Добавляем декоративный LED-индикатор
        led = QFrame()
        led.setProperty('class', 'retro-led')
        main_layout.addWidget(led)

        # Добавляем "дисплей" для статуса
        self.status_display = QLabel(self.translate('converter_window.status_ready'))
        self.status_display.setProperty('class', 'retro-display')
        self.status_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_display)

        # Создаем и добавляем элементы интерфейса в рамку
        self.create_file_selection(main_layout)
        self.create_files_list(main_layout)
        self.create_format_selection(main_layout)
        self.create_progress_section(main_layout)
        self.create_convert_button(main_layout)

        # Добавляем информацию о директориях
        info_label = QLabel(f"{self.translate('converter_window.input_dir')} {MUSIC_INPUT_DIR}\n{self.translate('converter_window.output_dir')} {MUSIC_OUTPUT_DIR}")
        info_label.setProperty('class', 'retro-display')
        main_layout.addWidget(info_label)

        # Добавляем кнопку перехода к сшиванию
        switch_button = QPushButton(self.translate('converter_window.switch_to_merger'))
        main_layout.addWidget(switch_button)
        switch_button.clicked.connect(self.switch_to_merger)

        # Добавляем основную рамку в layout
        layout.addWidget(main_frame)

        # Устанавливаем начальный размер конфетти
        self.confetti.setGeometry(0, 0, self.width(), self.height())
        
        self.show()

    def create_file_selection(self, layout):
        file_layout = QHBoxLayout()
        
        select_button = QPushButton(self.translate('converter_window.select_files'))
        select_button.clicked.connect(self.select_files)
        
        clear_button = QPushButton(self.translate('converter_window.clear_list'))
        clear_button.clicked.connect(self.clear_files)
        
        file_layout.addWidget(select_button)
        file_layout.addWidget(clear_button)
        layout.addLayout(file_layout)

    def create_files_list(self, layout):
        self.files_list = QListWidget()
        self.files_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        layout.addWidget(self.files_list)

        # Добавляем кнопку для удаления выбранных файлов
        remove_button = QPushButton(self.translate('converter_window.remove_selected'))
        remove_button.clicked.connect(self.remove_selected_files)
        layout.addWidget(remove_button)

    def create_format_selection(self, layout):
        format_layout = QHBoxLayout()
        
        format_layout.addWidget(QLabel(self.translate('converter_window.convert_to')))
        self.format_combo = QComboBox()
        self.format_combo.addItems(SUPPORTED_FORMATS.keys())
        
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

    def create_progress_section(self, layout):
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel('')
        layout.addWidget(self.status_label)

    def create_convert_button(self, layout):
        self.convert_button = QPushButton(self.translate('converter_window.convert_button'))
        self.convert_button.clicked.connect(self.start_conversion)
        self.convert_button.setEnabled(False)
        layout.addWidget(self.convert_button)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            self.translate('converter_window.dialog.select_files_title'),
            MUSIC_INPUT_DIR,
            'Аудио файлы (*.mp3 *.wav *.ogg *.flac *.aac)'
        )
        
        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    item = QListWidgetItem(os.path.basename(file))
                    item.setToolTip(file)  # Полный путь в подсказке
                    self.files_list.addItem(item)
            
            self.convert_button.setEnabled(bool(self.selected_files))

    def clear_files(self):
        self.selected_files.clear()
        self.files_list.clear()
        self.convert_button.setEnabled(False)

    def remove_selected_files(self):
        selected_items = self.files_list.selectedItems()
        for item in selected_items:
            file_path = item.toolTip()
            self.selected_files.remove(file_path)
            self.files_list.takeItem(self.files_list.row(item))
        
        self.convert_button.setEnabled(bool(self.selected_files))

    def start_conversion(self):
        self.worker = ConversionWorker(
            self.selected_files,
            self.format_combo.currentText(),
            self.translate
        )
        
        self.worker.progress.connect(self.update_progress)
        self.worker.status.connect(self.update_status)
        self.worker.finished.connect(self.conversion_finished)
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.convert_button.setEnabled(False)
        
        self.worker.start()

    def update_progress(self, current, total):
        self.progress_bar.setValue(int(current * 100 / total))

    def update_status(self, message):
        """Обновляет статус в дисплее"""
        self.status_label.setText(message)
        self.status_display.setText(message)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Обновляем размер конфетти при изменении размера окна
        self.confetti.setGeometry(0, 0, self.width(), self.height())

    def showEvent(self, event):
        super().showEvent(event)
        # Устанавливаем размер конфетти при первом показе окна
        self.confetti.setGeometry(0, 0, self.width(), self.height())

    def conversion_finished(self, success, error_message=""):
        self.progress_bar.setVisible(False)
        self.convert_button.setEnabled(True)
        
        if success:
            # Сначала показываем конфетти
            self.confetti.raise_()  # Поднимаем конфетти наверх
            self.confetti.start_animation()
            
            # Небольшая задержка перед показом сообщения
            QTimer.singleShot(500, lambda: QMessageBox.information(
                self,
                self.translate('converter_window.dialog.success'),
                self.translate('converter_window.dialog.conversion_complete')
            ))
            
            # Очищаем список после успешной конвертации
            self.clear_files()
        else:
            QMessageBox.critical(
                self,
                self.translate('converter_window.dialog.error'),
                f'{self.translate("converter_window.dialog.error_conversion")}\n{error_message}'
            )

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                self.translate('converter_window.dialog.confirmation'),
                self.translate('converter_window.dialog.exit_confirmation'),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Останавливаем конвертацию
                if self.worker:
                    self.worker.terminate()
                    self.worker.wait()
                event.accept()
            else:
                event.ignore()
                return

        # Показываем главное окно при закрытии только если установлен флаг
        if self.show_main_on_close:
            for widget in QApplication.topLevelWidgets():
                if widget.__class__.__name__ == 'MainWindow':
                    widget.show()
                    break

        event.accept()

    def switch_to_merger(self):
        """Переключение на окно сшивания"""
        # Отключаем показ главного окна при закрытии
        self.show_main_on_close = False
        # Импортируем здесь, чтобы избежать циклических импортов
        from src.gui.merger_window import MergerWindow

        self.merger = MergerWindow(None)  # Убираем parent
        
        # Проверяем, нужно ли применить флаг "всегда поверх"
        settings = load_settings()
        if settings.get('always_on_top', False):
            self.merger.setWindowFlags(self.merger.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        self.merger.show()
        self.close()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Обработчик начала перетаскивания файлов"""
        if event.mimeData().hasUrls():
            # Проверяем, что все файлы имеют поддерживаемые расширения
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.mp3', '.wav', '.ogg', '.flac', '.aac']:
                    event.acceptProposedAction()
                    return
    
    def dropEvent(self, event: QDropEvent):
        """Обработчик сброса файлов в окно"""
        urls = event.mimeData().urls()
        files = []
        for url in urls:
            file_path = url.toLocalFile()
            ext = os.path.splitext(file_path)[1].lower()
            if ext in ['.mp3', '.wav', '.ogg', '.flac', '.aac']:
                files.append(file_path)
        
        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    item = QListWidgetItem(os.path.basename(file))
                    item.setToolTip(file)
                    self.files_list.addItem(item)
            
            self.convert_button.setEnabled(bool(self.selected_files))

def main():
    app = QApplication(sys.argv)
    window = ConverterWindow()
    
    # Обработка CTRL+C
    def signal_handler(signum, frame):
        print("\nПолучен сигнал завершения. Закрываем приложение...")
        window.close()
        app.quit()
    
    # Регистрируем обработчик сигнала CTRL+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Таймер для обработки системных сигналов
    import time
    from PyQt5.QtCore import QTimer
    
    def process_signals():
        time.sleep(0.01)  # Небольшая задержка для снижения нагрузки на CPU
    
    timer = QTimer()
    timer.timeout.connect(process_signals)
    timer.start(100)  # Проверка каждые 100 мс
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 
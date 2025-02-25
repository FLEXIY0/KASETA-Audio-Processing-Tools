import os
import sys
from collections import Counter
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton, QFileDialog, QListWidget,
                           QListWidgetItem, QSpinBox, QDoubleSpinBox,
                           QProgressBar, QMessageBox, QComboBox, QApplication,
                           QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QDragEnterEvent, QDropEvent, QIcon

# Добавляем корневую директорию проекта в путь поиска модулей
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

from src.core.audio_processor import AudioProcessor
from src.utils.translations import get_translator
from src.utils.paths import MUSIC_INPUT_DIR, MUSIC_OUTPUT_DIR, ensure_dirs_exist
from src.gui.confetti import ConfettiWidget
from src.utils.settings import load_settings

# Поддерживаемые форматы
SUPPORTED_FORMATS = {
    'MP3': {'ext': '.mp3', 'ffmpeg_codec': 'libmp3lame'},
    'OGG': {'ext': '.ogg', 'ffmpeg_codec': 'libvorbis'},
    'WAV': {'ext': '.wav', 'ffmpeg_codec': 'pcm_s16le'},
    'FLAC': {'ext': '.flac', 'ffmpeg_codec': 'flac'},
    'AAC': {'ext': '.aac', 'ffmpeg_codec': 'aac'}
}

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
            total_steps = 100
            current_step = 0
            
            # Этап 1: Подготовка файлов (10%)
            self.status.emit("Подготовка файлов к объединению...")
            self.progress.emit(current_step, total_steps)
            
            # Создаем абсолютные пути
            input_files = [os.path.abspath(os.path.normpath(f)) for f in self.input_files]
            output_file = os.path.abspath(os.path.normpath(self.output_file))
            
            # Проверяем существование входных файлов
            for file in input_files:
                if not os.path.exists(file):
                    raise FileNotFoundError(f"Файл не найден: {file}")
            
            # Этап 2: Создание временной директории (15%)
            current_step = 15
            self.status.emit("Создание временной директории...")
            self.progress.emit(current_step, total_steps)
            
            temp_dir = os.path.abspath(os.path.join(os.path.dirname(output_file), ".temp_merge"))
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Этап 3: Применение эффектов затухания (50%)
            total_files = len(input_files)
            for i, file in enumerate(input_files):
                file_percent = 30 * (i + 1) / total_files
                current_step = 15 + int(file_percent)
                self.status.emit(f"Обработка файла {i+1} из {total_files}: {os.path.basename(file)}")
                self.progress.emit(current_step, total_steps)
                
                # Пауза для наглядности обновления в интерфейсе
                QThread.msleep(100)
            
            # Этап 4: Объединение файлов (70%)
            current_step = 70
            self.status.emit("Объединение аудио файлов...")
            self.progress.emit(current_step, total_steps)
            
            success = self.processor.merge_audio(
                self.input_files,
                self.output_file,
                pause_duration=self.pause_duration,
                fade_duration=self.fade_duration
            )
            
            # Этап 5: Финальная проверка (90%)
            current_step = 90
            self.status.emit("Проверка результата...")
            self.progress.emit(current_step, total_steps)
            
            if not success:
                raise Exception("Ошибка при объединении файлов")
                
            if not os.path.exists(output_file):
                raise FileNotFoundError(f"Выходной файл не был создан: {output_file}")
            
            # Завершение (100%)
            current_step = 100
            self.status.emit("Объединение успешно завершено!")
            self.progress.emit(current_step, total_steps)
            
            self.finished.emit(True, "")
                
        except FileNotFoundError as e:
            self.finished.emit(False, str(e))
        except Exception as e:
            self.finished.emit(False, str(e))

class MergerWindow(QMainWindow):
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
        # Получаем функцию перевода
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
        self.setWindowTitle(self.translate('merger_window.title'))
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

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
        self.status_display = QLabel(self.translate('merger_window.status_ready'))
        self.status_display.setProperty('class', 'retro-display')
        self.status_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_display)

        # Создаем все элементы интерфейса в рамке
        self.create_file_selection(main_layout)
        self.create_files_list(main_layout)
        self.create_settings_section(main_layout)
        self.create_progress_section(main_layout)
        self.create_merge_button(main_layout)
        self.create_convert_button(main_layout)

        # Информация о директориях
        info_label = QLabel(f"{self.translate('merger_window.input_dir')} {MUSIC_INPUT_DIR}\n{self.translate('merger_window.output_dir')} {MUSIC_OUTPUT_DIR}")
        info_label.setProperty('class', 'retro-display')
        main_layout.addWidget(info_label)

        # Добавляем кнопку перехода к конвертации
        switch_button = QPushButton(self.translate('merger_window.switch_to_converter'))
        switch_button.clicked.connect(self.switch_to_converter)
        main_layout.addWidget(switch_button)

        # Добавляем основную рамку в layout
        layout.addWidget(main_frame)

        # Устанавливаем размер конфетти
        self.confetti.setGeometry(0, 0, self.width(), self.height())
        
        self.show()

    def create_file_selection(self, layout):
        file_layout = QHBoxLayout()
        
        select_button = QPushButton(self.translate('merger_window.select_files'))
        select_button.clicked.connect(self.select_files)
        
        clear_button = QPushButton(self.translate('merger_window.clear_list'))
        clear_button.clicked.connect(self.clear_files)
        
        file_layout.addWidget(select_button)
        file_layout.addWidget(clear_button)
        layout.addLayout(file_layout)

    def create_files_list(self, layout):
        list_label = QLabel(self.translate('merger_window.files_list_label'))
        layout.addWidget(list_label)
        
        self.files_list = QListWidget()
        self.files_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.files_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        layout.addWidget(self.files_list)

        # Кнопки управления списком
        buttons_layout = QHBoxLayout()
        
        remove_button = QPushButton(self.translate('merger_window.remove_selected'))
        remove_button.clicked.connect(self.remove_selected_files)
        
        remove_minority_button = QPushButton(self.translate('merger_window.remove_minority'))
        remove_minority_button.clicked.connect(self.remove_minority_files)
        
        move_up_button = QPushButton(self.translate('merger_window.move_up'))
        move_up_button.clicked.connect(self.move_files_up)
        
        move_down_button = QPushButton(self.translate('merger_window.move_down'))
        move_down_button.clicked.connect(self.move_files_down)
        
        buttons_layout.addWidget(remove_button)
        buttons_layout.addWidget(remove_minority_button)
        buttons_layout.addWidget(move_up_button)
        buttons_layout.addWidget(move_down_button)
        layout.addLayout(buttons_layout)

    def create_settings_section(self, layout):
        settings_layout = QHBoxLayout()
        
        # Настройка формата
        format_layout = QVBoxLayout()
        format_layout.addWidget(QLabel(self.translate('merger_window.output_format')))
        self.format_combo = QComboBox()
        self.format_combo.addItems(SUPPORTED_FORMATS.keys())
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo)
        settings_layout.addLayout(format_layout)
        
        # Настройка паузы
        pause_layout = QVBoxLayout()
        pause_layout.addWidget(QLabel(self.translate('merger_window.pause_duration')))
        self.pause_spin = QDoubleSpinBox()
        self.pause_spin.setRange(0, 10)
        self.pause_spin.setValue(2)
        self.pause_spin.setSingleStep(0.5)
        pause_layout.addWidget(self.pause_spin)
        settings_layout.addLayout(pause_layout)
        
        # Настройка затухания
        fade_layout = QVBoxLayout()
        fade_layout.addWidget(QLabel(self.translate('merger_window.fade_duration')))
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
        self.merge_button = QPushButton(self.translate('merger_window.merge_button'))
        self.merge_button.clicked.connect(self.start_merge)
        self.merge_button.setEnabled(False)
        layout.addWidget(self.merge_button)

    def create_convert_button(self, layout):
        """Создает кнопку для конвертации файлов в единый формат"""
        self.convert_button = QPushButton(self.translate('merger_window.convert_button'))
        self.convert_button.clicked.connect(self.convert_to_main_format)
        self.convert_button.setEnabled(False)
        self.convert_button.hide()  # Изначально скрыта
        layout.addWidget(self.convert_button)

    def on_format_changed(self, new_format):
        """Обработчик изменения формата в комбобоксе"""
        self.update_file_colors(new_format)

    def get_file_format(self, file_path):
        """Получает формат файла"""
        ext = os.path.splitext(file_path)[1].lower()
        for format_name, format_info in SUPPORTED_FORMATS.items():
            if format_info['ext'] == ext:
                return format_name
        return None

    def detect_main_format(self):
        """Определяет основной формат на основе большинства файлов"""
        if not self.selected_files:
            return None
        
        formats = [self.get_file_format(f) for f in self.selected_files]
        format_counter = Counter(formats)
        main_format = format_counter.most_common(1)[0][0]
        
        # Устанавливаем основной формат в комбобокс
        index = self.format_combo.findText(main_format)
        if index >= 0:
            self.format_combo.setCurrentIndex(index)
        
        return main_format

    def update_file_colors(self, target_format=None):
        """Обновляет цвета файлов в списке"""
        if not target_format:
            target_format = self.detect_main_format()
        if not target_format:
            return

        has_different_formats = False
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            file_path = item.toolTip()
            file_format = self.get_file_format(file_path)
            
            if file_format != target_format:
                item.setBackground(QColor(255, 200, 200))  # Светло-красный для файлов другого формата
                has_different_formats = True
            else:
                item.setBackground(QColor(255, 255, 255))  # Белый для файлов основного формата

        # Показываем/скрываем кнопку конвертации
        self.convert_button.setVisible(has_different_formats)
        self.convert_button.setEnabled(has_different_formats)
        
        # Обновляем состояние кнопки объединения
        self.update_merge_button(has_different_formats)

    def update_merge_button(self, has_different_formats=None):
        """Обновляет состояние кнопки объединения в зависимости от количества файлов и их форматов"""
        # Кнопка доступна, если файлов больше 1 и все они одного формата
        files_count = len(self.selected_files)
        
        if files_count <= 1:
            self.merge_button.setEnabled(False)
            self.merge_button.setToolTip(self.translate('merger_window.merge_tooltips.disabled_not_enough_files'))
            return
        
        # Если нам уже передали результат проверки форматов, используем его
        if has_different_formats is None:
            # Иначе проверяем, все ли файлы одного формата
            first_format = self.get_file_format(self.selected_files[0])
            has_different_formats = not all(self.get_file_format(file) == first_format for file in self.selected_files)
        
        # Кнопка активна только если форматы одинаковые
        self.merge_button.setEnabled(not has_different_formats)
        
        if has_different_formats:
            self.merge_button.setToolTip(self.translate('merger_window.merge_tooltips.disabled_different_formats'))
        else:
            self.merge_button.setToolTip(self.translate('merger_window.merge_tooltips.enabled'))

    def convert_to_main_format(self):
        """Конвертирует все файлы в основной формат"""
        main_format = self.detect_main_format()
        if not main_format:
            return

        # Создаем директорию для конвертированных файлов с абсолютным путем
        converted_dir = os.path.abspath(os.path.join(MUSIC_OUTPUT_DIR, "converted_files"))
        try:
            os.makedirs(converted_dir, exist_ok=True)
            print(f"Создана директория для конвертации: {converted_dir}")  # Отладочный вывод
        except Exception as e:
            QMessageBox.critical(self, 
                self.translate('merger_window.dialog.error'), 
                f"{self.translate('merger_window.dialog.error_conversion')}\n{str(e)}")
            return

        # Показываем прогресс бар
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.convert_button.setEnabled(False)
        
        total_files = self.files_list.count()
        converted_count = 0
        converted_files = []  # Список для хранения успешно конвертированных файлов
        
        # Начальные значения для progressbar
        total_progress = total_files * 2  # Первый проход - анализ файлов, второй - конвертация
        current_progress = 0

        try:
            # Анализ файлов - первый проход
            files_to_convert = []
            for i in range(total_files):
                item = self.files_list.item(i)
                file_path = item.toolTip()
                file_format = self.get_file_format(file_path)
                
                # Обновляем UI
                self.status_label.setText(f"{self.translate('merger_window.dialog.processing_file', i+1, total_files, os.path.basename(file_path))}")
                current_progress += 1
                self.progress_bar.setValue(int(current_progress * 100 / total_progress))
                QApplication.processEvents()  # Позволяет UI обновиться
                
                # Если формат отличается от целевого, добавляем в список для конвертации
                if file_format != main_format:
                    files_to_convert.append((i, file_path))
                else:
                    # Для файлов правильного формата сразу добавляем в список
                    converted_files.append((i, file_path, os.path.basename(file_path)))
            
            # Конвертация файлов - второй проход
            if files_to_convert:
                self.status_label.setText(f"Найдено {len(files_to_convert)} файлов для конвертации")
                QApplication.processEvents()
                
                for idx, (i, file_path) in enumerate(files_to_convert):
                    # Обновляем статус
                    filename = os.path.basename(file_path)
                    self.status_label.setText(f"{self.translate('merger_window.dialog.processing_file', idx+1, len(files_to_convert), filename)}")
                    self.status_display.setText(f"{self.translate('merger_window.dialog.processing_file', idx+1, len(files_to_convert), filename)}")
                    
                    # Создаем новое имя файла с абсолютным путем
                    new_basename = os.path.splitext(filename)[0] + SUPPORTED_FORMATS[main_format]['ext']
                    new_file = os.path.abspath(os.path.join(converted_dir, new_basename))
                    
                    # Конвертируем файл
                    processor = AudioProcessor(lambda x: x)
                    success, error = processor.convert_audio(
                        file_path,
                        new_file,
                        SUPPORTED_FORMATS[main_format]['ffmpeg_codec']
                    )
                    
                    # Проверяем результат конвертации и существование файла
                    if success and os.path.exists(new_file):
                        converted_files.append((i, new_file, new_basename))
                        converted_count += 1
                    else:
                        error_msg = error if error else f"{self.translate('common.file_not_found', new_file)}"
                        raise Exception(error_msg)
                    
                    # Обновляем прогресс
                    current_progress += 1
                    self.progress_bar.setValue(int(current_progress * 100 / total_progress))
                    QApplication.processEvents()
            else:
                self.status_label.setText('Все файлы уже в нужном формате')
                QApplication.processEvents()
                # Завершаем прогресс-бар, так как конвертация не нужна
                self.progress_bar.setValue(100)

            # Обновляем пути в списке только после успешной конвертации всех файлов
            self.status_label.setText(f"{self.translate('merger_window.dialog.checking_result')}")
            QApplication.processEvents()
            
            for i, new_file, new_basename in converted_files:
                if os.path.exists(new_file):  # Дополнительная проверка
                    self.selected_files[i] = new_file
                    item = self.files_list.item(i)
                    item.setToolTip(new_file)
                    item.setText(new_basename)
                    item.setBackground(QColor(255, 255, 255))
                else:
                    raise Exception(f"{self.translate('common.file_not_found', new_file)}")

            # Скрываем прогресс
            self.progress_bar.hide()
            self.status_label.clear()
            self.status_display.setText(self.translate('merger_window.status_ready'))
            
            # Скрываем кнопку конвертации
            self.convert_button.hide()
            
            # Обновляем состояние кнопки объединения - теперь все файлы одного формата
            self.update_merge_button(False)
            
            QMessageBox.information(
                self,
                self.translate('merger_window.dialog.success'),
                self.translate('merger_window.dialog.files_converted')
            )

        except Exception as e:
            self.progress_bar.hide()
            self.status_label.clear()
            self.status_display.setText(self.translate('merger_window.status_ready'))
            QMessageBox.critical(
                self,
                self.translate('merger_window.dialog.error'),
                f"{self.translate('merger_window.dialog.error_conversion')}\n{str(e)}"
            )
            self.convert_button.setEnabled(True)

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
            
            # Обновляем цвета и состояние кнопок
            self.update_file_colors()  # Это также вызовет update_merge_button

    def clear_files(self):
        self.selected_files.clear()
        self.files_list.clear()
        self.merge_button.setEnabled(False)
        self.convert_button.hide()

    def remove_selected_files(self):
        selected_items = self.files_list.selectedItems()
        for item in selected_items:
            file_path = item.toolTip()
            self.selected_files.remove(file_path)
            self.files_list.takeItem(self.files_list.row(item))
        
        # Обновляем цвета и состояние кнопок
        self.update_file_colors()  # Это также вызовет update_merge_button

    def move_files_up(self):
        current_row = self.files_list.currentRow()
        if current_row > 0:
            item = self.files_list.takeItem(current_row)
            self.files_list.insertItem(current_row - 1, item)
            self.files_list.setCurrentRow(current_row - 1)
            # Обновляем порядок в selected_files
            file_path = self.selected_files.pop(current_row)
            self.selected_files.insert(current_row - 1, file_path)
            self.update_file_colors()  # Добавляем обновление цветов и состояния кнопок

    def move_files_down(self):
        current_row = self.files_list.currentRow()
        if current_row < self.files_list.count() - 1:
            item = self.files_list.takeItem(current_row)
            self.files_list.insertItem(current_row + 1, item)
            self.files_list.setCurrentRow(current_row + 1)
            # Обновляем порядок в selected_files
            file_path = self.selected_files.pop(current_row)
            self.selected_files.insert(current_row + 1, file_path)
            self.update_file_colors()  # Добавляем обновление цветов и состояния кнопок

    def start_merge(self):
        if len(self.selected_files) < 2:
            QMessageBox.warning(
                self,
                'Предупреждение',
                'Выберите как минимум два файла для объединения'
            )
            return

        # Получаем выбранный формат
        selected_format = SUPPORTED_FORMATS[self.format_combo.currentText()]
        
        # Запрашиваем имя выходного файла
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            'Сохранить объединенный файл',
            os.path.join(MUSIC_OUTPUT_DIR, f'merged{selected_format["ext"]}'),
            f'{self.format_combo.currentText()} файл (*{selected_format["ext"]})'
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
        """Обновляет статус в дисплее"""
        self.status_label.setText(message)
        self.status_display.setText(message)

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
        """Обработчик закрытия окна"""
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
                return

        # Показываем главное окно при закрытии только если установлен флаг
        if self.show_main_on_close:
            for widget in QApplication.topLevelWidgets():
                if widget.__class__.__name__ == 'MainWindow':
                    widget.show()
                    break

        event.accept()

    def switch_to_converter(self):
        """Переключение на окно конвертации"""
        # Отключаем показ главного окна при закрытии
        self.show_main_on_close = False
        # Импортируем здесь, чтобы избежать циклических импортов
        from src.gui.converter_window import ConverterWindow

        self.converter = ConverterWindow(None)  # Убираем parent
        
        # Проверяем, нужно ли применить флаг "всегда поверх"
        settings = load_settings()
        if settings.get('always_on_top', False):
            self.converter.setWindowFlags(self.converter.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        self.converter.show()
        self.close()

    def remove_minority_files(self):
        """Удаляет файлы, формат которых отличается от основного"""
        if not self.selected_files:
            return

        target_format = self.format_combo.currentText()
        if not target_format:
            target_format = self.detect_main_format()
        if not target_format:
            return

        # Создаем список файлов для удаления
        files_to_remove = []
        for i in range(self.files_list.count()):
            item = self.files_list.item(i)
            file_path = item.toolTip()
            file_format = self.get_file_format(file_path)
            
            if file_format != target_format:
                files_to_remove.append((i, file_path))

        # Удаляем файлы в обратном порядке, чтобы не нарушить индексы
        for index, file_path in reversed(files_to_remove):
            self.selected_files.remove(file_path)
            self.files_list.takeItem(index)

        # Обновляем состояние кнопок
        self.update_file_colors()  # Это также вызовет update_merge_button

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
            
            # Обновляем цвета и состояние кнопок
            self.update_file_colors()  # Это также вызовет update_merge_button

def main():
    app = QApplication(sys.argv)
    window = MergerWindow()
    sys.exit(app.exec()) 
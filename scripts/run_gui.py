import os
import sys
import signal
import argparse
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QPushButton, QLabel, QFrame, QComboBox, QHBoxLayout, 
                           QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from src.gui.converter_window import ConverterWindow
from src.gui.merger_window import MergerWindow
from src.gui.themes import Theme, DEFAULT_STYLE, RETRO_STYLE, WIN98_STYLE
from src.utils.settings import load_settings, save_settings
from src.utils.translations import initialize_translations, get_translator, get_supported_languages, set_language


# Обработка аргументов командной строки
parser = argparse.ArgumentParser(description='KASETA Audio Processing Tools')
parser.add_argument('--lang', dest='language', choices=['ru', 'en'], 
                    help='Interface language (ru or en)')
args = parser.parse_args()

settings = load_settings()

# Установка языка из аргументов командной строки, если указан
if args.language:
    settings['language'] = args.language
    save_settings(settings)

theme_name = settings.get('theme', 'retro')
always_on_top = settings.get('always_on_top', False)


current_language = initialize_translations(settings)
translate, _ = get_translator()


if theme_name == 'default':
    current_theme = Theme.DEFAULT
elif theme_name == 'retro':
    current_theme = Theme.RETRO
else:
    current_theme = Theme.WIN98

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(translate('main_window.title'))
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        self.setWindowFlags(Qt.WindowType.Window)
        
        
        global always_on_top
        if always_on_top:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        
        
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', '749.ico'))
        self.setWindowIcon(QIcon(icon_path))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(5)  
        layout.setContentsMargins(10, 10, 10, 10)  

        self.frame = QFrame()
        self.frame.setProperty('class', 'win98-border')  
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setSpacing(8) 
        frame_layout.setContentsMargins(10, 10, 10, 10) 

        
        self.image_container = QFrame()
        image_layout = QVBoxLayout(self.image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)  
        
        self.image_label = QLabel()
        self.image_label.setMinimumHeight(150)  
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'Group 15.png'))
        self.original_pixmap = QPixmap(image_path)
        self.image_label.setPixmap(self.original_pixmap.scaled(
            QSize(350, 150), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))
        
        image_layout.addWidget(self.image_label)
        frame_layout.addWidget(self.image_container)

        
        theme_layout = QHBoxLayout()
        theme_layout.setContentsMargins(0, 0, 0, 0)  
        theme_layout.addWidget(QLabel(translate('main_window.theme_label')))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            translate('main_window.themes.default'),
            translate('main_window.themes.retro'),
            translate('main_window.themes.win98')
        ])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo)
        frame_layout.addLayout(theme_layout)
        
        
        lang_layout = QHBoxLayout()
        lang_layout.setContentsMargins(0, 0, 0, 0)  
        lang_layout.addWidget(QLabel("Язык / Language:"))
        self.lang_combo = QComboBox()
        
        
        self.languages = get_supported_languages()
        self.lang_combo.addItems(self.languages.values())
        
        
        current_lang_index = list(self.languages.keys()).index(current_language)
        self.lang_combo.setCurrentIndex(current_lang_index)
        
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_combo)
        frame_layout.addLayout(lang_layout)
        
        
        self.always_on_top_checkbox = QCheckBox(translate('main_window.always_on_top'))
        self.always_on_top_checkbox.setChecked(always_on_top)
        self.always_on_top_checkbox.stateChanged.connect(self.toggle_always_on_top)
        frame_layout.addWidget(self.always_on_top_checkbox)

        
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(5)  
        buttons_layout.setContentsMargins(0, 0, 0, 0)  

        
        self.converter_button = QPushButton(translate('main_window.converter_button'))
        self.converter_button.clicked.connect(self.open_converter)
        buttons_layout.addWidget(self.converter_button)

        self.merger_button = QPushButton(translate('main_window.merger_button'))
        self.merger_button.clicked.connect(self.open_merger)
        buttons_layout.addWidget(self.merger_button)

        frame_layout.addLayout(buttons_layout)
        layout.addWidget(self.frame)
        
        self.show()

    def change_language(self, index):
        """Изменение языка интерфейса"""
        global settings
        language_code = list(self.languages.keys())[index]
        
        
        settings['language'] = language_code
        save_settings(settings)
        
        
        if set_language(language_code):
            QMessageBox.information(
                self,
                "Язык интерфейса / Interface language",
                "Язык изменен. Перезапустите приложение для применения изменений.\n\n"
                "Language changed. Restart the application to apply changes."
            )

    def toggle_always_on_top(self, state):
        """Включение/выключение режима 'Всегда поверх'"""
        global always_on_top, settings
        always_on_top = bool(state)
        settings['always_on_top'] = always_on_top
        save_settings(settings)
        
        
        flags = self.windowFlags()
        if always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        
        
        self.setWindowFlags(flags)
        self.show()

    def change_theme(self, index):
        """Изменение темы оформления"""
        global current_theme, settings
        app = QApplication.instance()
        
        if index == 0:  
            app.setStyleSheet(DEFAULT_STYLE)
            self.update_frame_style('default-border')
            current_theme = Theme.DEFAULT
            settings['theme'] = 'default'
        elif index == 1:  
            app.setStyleSheet(RETRO_STYLE)
            self.update_frame_style('retro-border')
            current_theme = Theme.RETRO
            settings['theme'] = 'retro'
        else:  
            app.setStyleSheet(WIN98_STYLE)
            self.update_frame_style('win98-border')
            current_theme = Theme.WIN98
            settings['theme'] = 'win98'
            
        
        save_settings(settings)

    def update_frame_style(self, style_class):
        """Обновление стиля рамки и других элементов"""
        
        self.frame.setProperty('class', style_class)
        
        
        self.frame.style().unpolish(self.frame)
        self.frame.style().polish(self.frame)
        
        
        self.image_label.setPixmap(self.original_pixmap.scaled(
            QSize(350, 150), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        ))

    def open_converter(self):
        """Открытие окна конвертации"""
        self.converter = ConverterWindow(None)
        
        self.apply_theme_to_window(self.converter)
        
        self.apply_always_on_top(self.converter)
        self.converter.show()
        self.hide()

    def open_merger(self):
        """Открытие окна сшивания"""
        self.merger = MergerWindow(None)
        
        self.apply_theme_to_window(self.merger)
        
        self.apply_always_on_top(self.merger)
        self.merger.show()
        self.hide()
        
    def apply_theme_to_window(self, window):
        """Применяет текущую тему к окну"""
        global current_theme
        if current_theme == Theme.DEFAULT:
            window.setProperty('theme', 'default')
        elif current_theme == Theme.RETRO:
            window.setProperty('theme', 'retro')
        else:
            window.setProperty('theme', 'win98')
    
    def apply_always_on_top(self, window):
        """Применяет настройку 'всегда поверх' к окну"""
        global always_on_top
        if always_on_top:
            window.setWindowFlags(window.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

    def closeEvent(self, event):
        """Обработчик закрытия главного окна"""
        
        if hasattr(self, 'converter'):
            self.converter.close()
        if hasattr(self, 'merger'):
            self.merger.close()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', '749.ico'))
    app.setWindowIcon(QIcon(icon_path))
    
    
    global current_theme
    if current_theme == Theme.DEFAULT:
        app.setStyleSheet(DEFAULT_STYLE)
    elif current_theme == Theme.RETRO:
        app.setStyleSheet(RETRO_STYLE)
    else:
        app.setStyleSheet(WIN98_STYLE)
    
    window = MainWindow()
    
    
    if current_theme == Theme.DEFAULT:
        window.theme_combo.setCurrentIndex(0)
    elif current_theme == Theme.RETRO:
        window.theme_combo.setCurrentIndex(1)
    else:
        window.theme_combo.setCurrentIndex(2)
    
    
    def signal_handler(signum, frame):
        print("\nПолучен сигнал завершения. Закрываем приложение...")
        window.close()
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    
    def process_signals():
        import time
        time.sleep(0.01)
    
    timer = QTimer()
    timer.timeout.connect(process_signals)
    timer.start(100)
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 

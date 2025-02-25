import os
import json

# Путь к файлу настроек
SETTINGS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'settings.json'))

def save_settings(settings):
    """Сохраняет настройки в файл"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении настроек: {str(e)}")
        return False

def load_settings():
    """Загружает настройки из файла"""
    default_settings = {
        'theme': 'win98',  # По умолчанию тема Windows 98
        'always_on_top': False,  # По умолчанию окна не поверх всех
        'language': 'ru'  # По умолчанию русский язык
    }
    
    if not os.path.exists(SETTINGS_FILE):
        return default_settings
    
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            
        # Добавляем новые параметры, если их нет в существующих настройках
        if 'always_on_top' not in settings:
            settings['always_on_top'] = default_settings['always_on_top']
            
        if 'language' not in settings:
            settings['language'] = default_settings['language']
            
        return settings
    except Exception as e:
        print(f"Ошибка при загрузке настроек: {str(e)}")
        return default_settings 
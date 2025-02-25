import os
import json
import logging
from functools import lru_cache

# Получаем корневую директорию проекта
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

# Директория с файлами переводов
TRANSLATIONS_DIR = os.path.join(project_root, 'src', 'translations')

# Поддерживаемые языки
SUPPORTED_LANGUAGES = {
    'ru': 'Русский',
    'en': 'English'
}

# Текущий язык (по умолчанию - русский)
CURRENT_LANGUAGE = 'ru'

# Кеш для загруженных переводов
_translations_cache = {}

def load_translation(language_code):
    """Загрузка перевода для указанного языка"""
    global _translations_cache
    
    if language_code in _translations_cache:
        return _translations_cache[language_code]
    
    try:
        translation_file = os.path.join(TRANSLATIONS_DIR, f"{language_code}.json")
        if not os.path.exists(translation_file):
            logging.warning(f"Файл перевода не найден: {translation_file}")
            # Если запрошенный язык не найден, возвращаем русский
            if language_code != 'ru' and os.path.exists(os.path.join(TRANSLATIONS_DIR, "ru.json")):
                return load_translation('ru')
            return {}
        
        with open(translation_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            _translations_cache[language_code] = translations
            return translations
    
    except Exception as e:
        logging.error(f"Ошибка при загрузке перевода ({language_code}): {str(e)}")
        return {}

def set_language(language_code):
    """Установка текущего языка"""
    global CURRENT_LANGUAGE
    
    if language_code in SUPPORTED_LANGUAGES:
        CURRENT_LANGUAGE = language_code
        return True
    
    return False

def get_supported_languages():
    """Получение списка поддерживаемых языков"""
    return SUPPORTED_LANGUAGES.copy()

@lru_cache(maxsize=128)
def resolve_key(key_path, language_code=None):
    """Получение значения перевода по пути ключа"""
    if language_code is None:
        language_code = CURRENT_LANGUAGE
    
    translations = load_translation(language_code)
    
    parts = key_path.split('.')
    current = translations
    
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            # Ключ не найден, возвращаем сам ключ
            return key_path
    
    return current

def get_translator():
    """Получение функции перевода и текущего языка"""
    def translate(key, *args):
        """
        Переводит ключ с возможностью подстановки аргументов
        Например: translate("common.file_not_found", "file.mp3")
        """
        text = resolve_key(key, CURRENT_LANGUAGE)
        
        # Подстановка аргументов, если они есть
        if args:
            for i, arg in enumerate(args, 1):
                text = text.replace(f"%{i}", str(arg))
        
        return text
    
    return translate, CURRENT_LANGUAGE

def initialize_translations(settings):
    """Инициализация системы переводов из настроек"""
    global CURRENT_LANGUAGE
    
    # Если в настройках есть язык, устанавливаем его
    if 'language' in settings:
        language = settings.get('language')
        if language in SUPPORTED_LANGUAGES:
            CURRENT_LANGUAGE = language
    
    # Предзагружаем все переводы в кеш
    for lang in SUPPORTED_LANGUAGES.keys():
        load_translation(lang)
    
    return CURRENT_LANGUAGE 
from googletrans import Translator
import locale
import sys

# Базовые строки на английском
BASE_TRANSLATIONS = {
    'welcome_audio_converter': "\n=== Audio File Converter ===",
    'welcome_desc_converter': "This script will help you convert audio files between different formats",
    'welcome_merger': "\n=== Слияние аудио файлов ===",
    'welcome_desc_merger': "Этот скрипт поможет объединить несколько аудио файлов в один\nс паузами между треками и плавными переходами",
    'welcome_installer': "\n=== Audio Scripts Dependencies Installer ===",
    'supported_formats': "\nSupported formats:",
    'available_formats': "\nAvailable formats:",
    'select_source_format': "\nSelect source file format (enter number): ",
    'select_target_format': "Select target format (enter number): ",
    'select_output_format': "Select output file format (enter number): ",
    'enter_pause_duration': "\nEnter pause duration between tracks (in seconds): ",
    'enter_fade_duration': "\nEnter fade duration (in seconds): ",
    'positive_number_error': "Duration must be a positive number",
    'enter_number_error': "Please enter a number",
    'select_format_error': "Please select a valid format number",
    'files_not_found': "Файлы формата {format} не найдены в папке input",
    'found_files': "\nНайдено файлов: {count}",
    'source_format': "Исходный формат: {format}",
    'target_format': "Целевой формат: {format}",
    'pause_duration': "Пауза между треками: {duration:.1f} сек",
    'fade_duration': "Длительность затухания: {duration:.1f} сек",
    'start_merge': "\nНачать слияние? (y/n): ",
    'merge_cancelled': "Слияние отменено",
    'processing_files': "Обработка файлов",
    'processing_file': "Обработка: {filename}",
    'export_final': "\nЭкспорт финального файла...",
    'audio_size': "Размер аудио: {size:.2f} минут",
    'exporting': "Экспорт",
    'done': "\nГотово! Сохранено в: {filename}",
    'press_enter': "\nНажмите Enter для выхода...",
    'installation_components': "\nThis script will install the following components:",
    'python_packages': "1. Python packages:",
    'check_ffmpeg': "2. Check FFmpeg installation",
    'requirements': "\nRequirements:",
    'python_version': "- Python 3.6 or higher",
    'internet_access': "- Internet access",
    'install_rights': "- Installation rights",
    'continue_install': "\nContinue installation? (yes/no): ",
    'install_cancelled': "\nInstallation cancelled.",
    'starting_install': "\nStarting package installation...",
    'found_packages': "Found {count} packages to install",
    'installing_packages': "Installing packages",
    'installing': "Installing {package}",
    'all_packages_installed': "\nAll packages successfully installed!",
    'ffmpeg_installed': "FFmpeg is already installed",
    'ffmpeg_not_found': "\nWARNING: FFmpeg not found!",
    'install_ffmpeg': "Please install FFmpeg:",
    'windows_ffmpeg': "1. Windows: download from https://www.gyan.dev/ffmpeg/builds/ and add to PATH",
    'linux_ffmpeg': "2. Linux: sudo apt-get install ffmpeg",
    'macos_ffmpeg': "3. macOS: brew install ffmpeg",
    'install_success': "\nInstallation completed successfully!",
    'can_use_scripts': "Now you can use convert_audio.py and merge_music.py",
    'install_error': "\nAn error occurred during installation.",
    'yes_variants': ['yes', 'y'],
    'no_variants': ['no', 'n'],
    'interrupted': '\nProgram interrupted by user.',
    'usage_convert': 'Usage:',
    'conversion_success': 'Conversion completed successfully',
    'conversion_failed': 'Conversion failed',
    'input_file_not_found': 'Input file not found',
    'conversion_error': 'Error converting file',
    'usage_merge': 'Usage:',
    'merge_success': 'Files merged successfully',
    'merge_failed': 'Error merging files',
    'no_input_files': 'No input files specified',
    'file_not_found': 'File {file} not found',
    'merge_error': 'Error merging files',
    'found_files_list': "\nДоступные файлы:",
    'convert_all_files': "Конвертировать все файлы",
    'exit_option': "0 - выход",
    'select_file_number': "\nВыберите номер файла (0 - выход): ",
    'invalid_number': "Неверный номер. Попробуйте снова.",
    'please_enter_number': "Пожалуйста, введите число.",
    'start_conversion': "\nНачать конвертацию? (y/n): ",
    'conversion_cancelled': "Конвертация отменена",
    'converting_file': "Конвертация файла: {filename}",
    'conversion_complete': "Конвертация завершена. Результат сохранен в: {directory}",
    'selected_files_count': "Выбрано файлов: {count}",
    'available_files_list': "Доступные файлы (✓ - выбран):",
    'selection_options': "Опции:",
    'select_file_option': "+N - выбрать файл номер N",
    'deselect_file_option': "-N - отменить выбор файла номер N",
    'select_all_option': "a - выбрать все файлы",
    'clear_selection_option': "c - очистить выбор",
    'continue_option': "f - продолжить слияние",
    'enter_choice': "Введите команду: ",
    'not_enough_files': "Нужно выбрать минимум 2 файла для слияния",
    'invalid_choice': "Неверная команда",
    'no_audio_files': "Аудио файлы не найдены в папке input",
    'enter_output_name': "Введите имя выходного файла: ",
    'invalid_filename': "Неверное имя файла",
    'merge_summary': "\nПараметры слияния:",
    'files_to_merge': "Файлы для объединения ({count}):",
    'output_file': "Выходной файл: {file}",
    'saved_to': "Сохранено в: {file}",
    'enter_pause': "Введите продолжительность паузы между треками (в секундах): ",
    'enter_fade': "Введите продолжительность затухания (в секундах): ",
    'different_formats_detected': "Обнаружены файлы разных форматов!",
    'formats_found': "Найдены форматы: {formats}",
    'select_target_format_merge': "Выберите формат для конвертации:",
    'enter_format_number': "Введите номер формата: ",
    'conversion_failed_for_file': "Ошибка конвертации файла: {file}",
    'converting_files': "Конвертация файлов в единый формат...",
    'temp_files_cleanup': "Очистка временных файлов...",
    'preparing_files': "Подготовка файлов...",
    'merging_files': "Объединение файлов",
    'merging_step_1': "Этап 1: Объединение файлов",
    'adding_effects': "Этап 2: Добавление эффектов",
    'cleaning_temp_files': "Очистка временных файлов",
    'total_duration': "Итоговая длина записи: {minutes} мин {seconds} сек",
    'merge_complete': "Объединение файлов успешно завершено!",
    'merging_progress': "Объединение: {percent}%",
    'effects_progress': "Обработка эффектов: {percent}%",
    'merging_start': "Начинаю объединение файлов...",
    'processing_please_wait': "Идет обработка, пожалуйста подождите...",
    'processing_start': "Начинаю обработку",
    'processing': "Обработка",  # Будет дополнено точками
    'processing_percent': "Выполнено: {percent}",  # Будет показывать проценты
    'step_concat': "Шаг 1: Объединение файлов...",
    'step_convert': "Шаг 2: Конвертация в MP3...",
}

ENGLISH_TRANSLATIONS = {
    'usage_convert': 'Usage:',
    'conversion_success': 'Conversion completed successfully',
    'conversion_failed': 'Conversion failed',
    'input_file_not_found': 'Input file not found',
    'conversion_error': 'Error converting file',
    'usage_merge': 'Usage:',
    'merge_success': 'Files merged successfully',
    'merge_failed': 'Error merging files',
    'no_input_files': 'No input files specified',
    'file_not_found': 'File {file} not found',
    'merge_error': 'Error merging files',
    'processing_files': 'Processing files...',
    'processing_file': 'Processing file {filename}...',
    'done': 'Done! Result saved to {filename}',
    'files_not_found': 'No files with extension {format} found',
    'found_files': 'Found {count} files',
    'source_format': 'Source format: {format}',
    'target_format': 'Target format: {format}',
    'start_merge': 'Start processing? (y/n): ',
    'merge_cancelled': 'Operation cancelled by user',
    'total_duration': "Expected duration: {minutes} min {seconds} sec",
    'merge_complete': "Merge completed successfully!",
    'merging_progress': "Merge progress: {percent}%",
    'effects_progress': "Adding effects: {percent}%",
    'processing_start': "Starting processing",
    'processing': "Processing",  # Will be followed by dots
    'processing_percent': "Completed: {percent}",  # Will show percentage
}

def get_language():
    """Определяет язык системы"""
    try:
        system_lang = locale.getdefaultlocale()[0]
        if system_lang:
            return system_lang.split('_')[0]  # Получаем только код языка (например, 'ru' из 'ru_RU')
    except:
        pass
    return 'en'

def get_translator(lang=None):
    """Возвращает функцию-переводчик для указанного языка"""
    if lang is None:
        lang = get_language()
    
    if lang == 'en':
        # Для английского используем оригинальные строки
        return lambda key, **kwargs: BASE_TRANSLATIONS[key].format(**kwargs) if kwargs else BASE_TRANSLATIONS[key], BASE_TRANSLATIONS
    
    try:
        # Создаем переводчик
        translator = Translator()
        
        # Кэш для переводов
        translations = {}
        
        def translate(key, **kwargs):
            if key not in translations:
                # Переводим строку, сохраняя плейсхолдеры
                text = BASE_TRANSLATIONS[key]
                # Заменяем плейсхолдеры на временные метки
                placeholders = {}
                for k in kwargs.keys():
                    placeholder = "{" + k + "}"
                    temp_mark = f"____{k}____"
                    text = text.replace(placeholder, temp_mark)
                
                # Переводим текст
                translated = translator.translate(text, dest=lang).text
                
                # Возвращаем плейсхолдеры обратно
                for k in kwargs.keys():
                    temp_mark = f"____{k}____"
                    placeholder = "{" + k + "}"
                    translated = translated.replace(temp_mark, placeholder)
                
                translations[key] = translated
            
            # Возвращаем переведенную строку с подставленными параметрами
            text = translations[key]
            if kwargs:
                return text.format(**kwargs)
            return text
        
        # Переводим yes/no варианты
        yes_translated = translator.translate("yes", dest=lang).text.lower()
        no_translated = translator.translate("no", dest=lang).text.lower()
        translations['yes_variants'] = [yes_translated, yes_translated[0]]
        translations['no_variants'] = [no_translated, no_translated[0]]
        
        return translate, translations
        
    except Exception as e:
        print(f"Warning: Could not initialize translator ({str(e)}). Using English.")
        return lambda key, **kwargs: BASE_TRANSLATIONS[key].format(**kwargs) if kwargs else BASE_TRANSLATIONS[key], BASE_TRANSLATIONS

def signal_handler(sig, frame):
    translate, _ = get_translator()
    print(translate('interrupted'))
    sys.exit(0) 
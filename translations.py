from googletrans import Translator
import locale
import sys

# Базовые строки на английском
BASE_TRANSLATIONS = {
    'welcome_audio_converter': "\n=== Audio File Converter ===",
    'welcome_desc_converter': "This script will help you convert audio files between different formats",
    'welcome_merger': "\n=== Audio File Merger ===",
    'welcome_desc_merger': "This script will combine all audio files from the current folder into one file\nwith pauses between tracks and smooth transitions",
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
    'files_not_found': "\nNo {format} files found in current directory",
    'found_files': "\nFound {count} files",
    'source_format': "Source format: {format}",
    'target_format': "Target format: {format}",
    'pause_duration': "Pause between tracks: {duration:.1f} sec",
    'fade_duration': "Fade duration: {duration:.1f} sec",
    'start_merge': "\nStart merging? (yes/no): ",
    'merge_cancelled': "Merging cancelled",
    'processing_files': "Processing files",
    'processing_file': "Processing: {filename}",
    'export_final': "\nExporting final file...",
    'audio_size': "Audio size: {size:.2f} minutes",
    'exporting': "Exporting",
    'done': "\nDone! Saved to: {filename}",
    'press_enter': "\nPress Enter to exit...",
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
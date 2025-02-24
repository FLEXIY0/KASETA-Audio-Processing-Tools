import os
import sys

# Добавляем корневую директорию проекта в путь поиска модулей
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

import subprocess
import glob
from tqdm import tqdm
from src.utils.translations import get_translator
import signal
from src.utils.progress import SmoothProgress
from src.core.audio_processor import AudioProcessor
from src.utils.paths import MUSIC_INPUT_DIR, MUSIC_OUTPUT_DIR, ensure_dirs_exist

SUPPORTED_FORMATS = {
    '1': {'name': 'MP3', 'ext': '.mp3', 'ffmpeg_codec': 'libmp3lame'},
    '2': {'name': 'OGG', 'ext': '.ogg', 'ffmpeg_codec': 'libvorbis'},
    '3': {'name': 'WAV', 'ext': '.wav', 'ffmpeg_codec': 'pcm_s16le'},
    '4': {'name': 'FLAC', 'ext': '.flac', 'ffmpeg_codec': 'flac'},
    '5': {'name': 'AAC', 'ext': '.aac', 'ffmpeg_codec': 'aac'}
}

def signal_handler(sig, frame):
    print('\nПрограмма прервана пользователем.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def show_welcome(t):
    print(t('welcome_audio_converter'))
    print(t('welcome_desc_converter'))

def get_format_choice(t, prompt):
    while True:
        print(t('available_formats'))
        for key, format_info in SUPPORTED_FORMATS.items():
            print(f"{key}. {format_info['name']}")
        choice = input(prompt)
        if choice in SUPPORTED_FORMATS:
            return SUPPORTED_FORMATS[choice]
        print(t('select_format_error'))

def convert_audio(input_path, output_path, output_codec, quality="192k"):
    """Конвертирует один аудио файл"""
    try:
        command = f'ffmpeg -i "{input_path}" -c:a {output_codec} -b:a {quality} "{output_path}"'
        subprocess.run(command, shell=True, check=True, 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nОшибка при конвертации {os.path.basename(input_path)}: {str(e)}")
        return False

def convert_files(directory, source_ext, target_format, t):
    """Конвертирует все файлы указанного формата в директории"""
    files = glob.glob(os.path.join(directory, f"*{source_ext}"))
    
    if not files:
        print(t('files_not_found', format=source_ext))
        return
    
    print(t('found_files', count=len(files)))
    print(t('source_format', format=source_ext))
    print(t('target_format', format=target_format['name']))
    
    if not input(t('start_merge')).lower().startswith(t('yes_variants')[0][0]):
        print(t('merge_cancelled'))
        return
    
    progress = SmoothProgress(len(files), desc=t('processing_files'))
    progress.start()
    
    try:
        for input_file in files:
            progress.set_description(t('processing_file', filename=os.path.basename(input_file)))
            output_file = os.path.splitext(input_file)[0] + target_format['ext']
            if convert_audio(input_file, output_file, target_format['ffmpeg_codec']):
                progress.update(1)
    finally:
        progress.close()
            
    print(t('done', filename=output_file))

def main():
    ensure_dirs_exist()
    translate, _ = get_translator()
    processor = AudioProcessor(translate)
    
    show_welcome(translate)
    
    # Выбор исходного формата
    source_format = get_format_choice(translate, translate('select_source_format'))
    print()
    
    # Поиск файлов указанного формата
    files = glob.glob(os.path.join(MUSIC_INPUT_DIR, f"*{source_format['ext']}"))
    
    if not files:
        print(translate('files_not_found', format=source_format['ext']))
        input(translate('press_enter'))
        return
    
    # Показываем список найденных файлов
    print(translate('found_files', count=len(files)))
    print(translate('found_files_list'))
    for i, file in enumerate(files, 1):
        print(f"{i}. {os.path.basename(file)}")
    print(f"{len(files) + 1}. {translate('convert_all_files')}")
    print(f"0. {translate('exit_option')}")
    
    # Выбор файла
    while True:
        try:
            choice = int(input(translate('select_file_number')))
            if choice == 0:
                return
            elif choice == len(files) + 1:
                selected_files = files
                break
            elif 1 <= choice <= len(files):
                selected_files = [files[choice-1]]
                break
            else:
                print(translate('invalid_number'))
        except ValueError:
            print(translate('please_enter_number'))
    
    # Выбор целевого формата
    target_format = get_format_choice(translate, translate('select_target_format'))
    print()
    
    # Подтверждение
    print(translate('source_format', format=source_format['name']))
    print(translate('target_format', format=target_format['name']))
    if not input(translate('start_conversion')).lower().startswith('y'):
        print(translate('conversion_cancelled'))
        return
    
    # Конвертация файлов
    progress = SmoothProgress(len(selected_files), desc=translate('processing_files'))
    progress.start()
    
    try:
        for input_file in selected_files:
            filename = os.path.basename(input_file)
            progress.set_description(translate('converting_file', filename=filename))
            
            output_file = os.path.join(
                MUSIC_OUTPUT_DIR,
                os.path.splitext(filename)[0] + target_format['ext']
            )
            
            if processor.convert_audio(input_file, output_file):
                progress.update(1)
    finally:
        progress.close()
    
    print(translate('conversion_complete', directory=MUSIC_OUTPUT_DIR))
    input(translate('press_enter'))

if __name__ == "__main__":
    main() 
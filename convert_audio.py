import os
import subprocess
import glob
from tqdm import tqdm
from translations import get_translator
import signal
import sys
from smooth_progress import SmoothProgress

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
    print(t('supported_formats'))
    for key, format_info in SUPPORTED_FORMATS.items():
        print(f"{key}. {format_info['name']}")

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
    # Получаем переводчик
    translate, _ = get_translator()
    
    show_welcome(translate)
    
    # Получаем формат исходных файлов
    source_format = get_format_choice(translate, translate('select_source_format'))
    
    # Получаем целевой формат
    while True:
        target_format = get_format_choice(translate, translate('select_target_format'))
        if target_format['ext'] != source_format['ext']:
            break
        print(translate('select_format_error'))
    
    # Получаем путь к текущей директории скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Запускаем конвертацию
    convert_files(script_dir, source_format['ext'], target_format, translate)
    
    input(translate('press_enter'))

if __name__ == "__main__":
    main() 
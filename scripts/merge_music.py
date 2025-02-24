import os
import sys
import glob
import signal

# Добавляем корневую директорию проекта в путь поиска модулей
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from src.utils.translations import get_translator
from src.core.audio_processor import AudioProcessor
from src.utils.paths import MUSIC_INPUT_DIR, MUSIC_OUTPUT_DIR, ensure_dirs_exist
from src.utils.progress import SmoothProgress

def signal_handler(sig, frame):
    print('\nПрограмма прервана пользователем.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def show_welcome(t):
    print(t('welcome_merger'))
    print(t('welcome_desc_merger'))

def select_files(files, t):
    selected_files = []
    while True:
        print("\n" + t('selected_files_count', count=len(selected_files)))
        print(t('available_files_list'))
        
        # Показываем доступные файлы
        for i, file in enumerate(files, 1):
            mark = "✓" if file in selected_files else " "
            print(f"{i}. [{mark}] {os.path.basename(file)}")
        
        print("\n" + t('selection_options'))
        print(t('select_file_option'))
        print(t('deselect_file_option'))
        print(t('select_all_option'))
        print(t('clear_selection_option'))
        print(t('continue_option'))
        print(t('exit_option'))
        
        try:
            choice = input(t('enter_choice')).strip()
            
            if choice == '0':
                return None  # Выход
            elif choice == 'a':
                selected_files = files.copy()  # Выбрать все
            elif choice == 'c':
                selected_files = []  # Очистить выбор
            elif choice == 'f':
                if len(selected_files) < 2:
                    print(t('not_enough_files'))
                    continue
                return selected_files  # Продолжить со слиянием
            elif choice.startswith('+'):
                try:
                    idx = int(choice[1:]) - 1
                    if 0 <= idx < len(files) and files[idx] not in selected_files:
                        selected_files.append(files[idx])
                except ValueError:
                    print(t('invalid_number'))
            elif choice.startswith('-'):
                try:
                    idx = int(choice[1:]) - 1
                    if 0 <= idx < len(files) and files[idx] in selected_files:
                        selected_files.remove(files[idx])
                except ValueError:
                    print(t('invalid_number'))
            else:
                print(t('invalid_choice'))
        except ValueError:
            print(t('invalid_choice'))

def main():
    ensure_dirs_exist()
    translate, _ = get_translator()
    processor = AudioProcessor(translate)
    
    show_welcome(translate)
    
    # Поиск всех аудио файлов
    files = []
    for ext in ['.mp3', '.wav', '.ogg', '.flac', '.aac']:
        files.extend(glob.glob(os.path.join(MUSIC_INPUT_DIR, f"*{ext}")))
    
    if not files:
        print(translate('no_audio_files'))
        input(translate('press_enter'))
        return
    
    # Выбор файлов для слияния
    selected_files = select_files(files, translate)
    if not selected_files:
        print(translate('merge_cancelled'))
        return
    
    # Запрос имени выходного файла
    while True:
        output_name = input(translate('enter_output_name'))
        if output_name:
            output_file = os.path.join(MUSIC_OUTPUT_DIR, output_name)
            if not output_file.lower().endswith('.mp3'):
                output_file += '.mp3'
            break
        print(translate('invalid_filename'))
    
    # Запрос параметров
    while True:
        try:
            pause = float(input(translate('enter_pause')))
            if pause >= 0:
                break
            print(translate('positive_number_error'))
        except ValueError:
            print(translate('enter_number_error'))
    
    while True:
        try:
            fade = float(input(translate('enter_fade')))
            if fade >= 0:
                break
            print(translate('positive_number_error'))
        except ValueError:
            print(translate('enter_number_error'))
    
    # Подтверждение
    print(translate('merge_summary'))
    print(translate('files_to_merge', count=len(selected_files)))
    for file in selected_files:
        print(f"  - {os.path.basename(file)}")
    print(translate('output_file', file=output_file))
    print(translate('pause_duration', duration=pause))
    print(translate('fade_duration', duration=fade))
    
    if not input(translate('start_merge')).lower().startswith('y'):
        print(translate('merge_cancelled'))
        return
    
    # Слияние файлов
    if processor.merge_audio(selected_files, output_file, pause_duration=pause, fade_duration=fade):
        print(translate('merge_success'))
        print(translate('saved_to', file=output_file))
    else:
        print(translate('merge_failed'))
    
    input(translate('press_enter'))

if __name__ == "__main__":
    main() 
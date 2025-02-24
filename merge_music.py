import os
import subprocess
from pydub import AudioSegment
import glob
from tqdm import tqdm
from other.translations import get_translator
import signal
import sys
from other.smooth_progress import SmoothProgress

def signal_handler(sig, frame):
    print('\nПрограмма прервана пользователем.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

SUPPORTED_FORMATS = {
    '1': {'name': 'MP3', 'ext': '.mp3', 'pydub_format': 'mp3'},
    '2': {'name': 'OGG', 'ext': '.ogg', 'pydub_format': 'ogg'},
    '3': {'name': 'WAV', 'ext': '.wav', 'pydub_format': 'wav'},
    '4': {'name': 'FLAC', 'ext': '.flac', 'pydub_format': 'flac'},
    '5': {'name': 'AAC', 'ext': '.aac', 'pydub_format': 'aac'}
}

def show_welcome(t):
    print(t('welcome_merger'))
    print(t('welcome_desc_merger'))
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

def get_pause_duration(t):
    while True:
        try:
            duration = float(input(t('enter_pause_duration')))
            if duration >= 0:
                return int(duration * 1000)
            print(t('positive_number_error'))
        except ValueError:
            print(t('enter_number_error'))

def get_fade_duration(t):
    while True:
        try:
            duration = float(input(t('enter_fade_duration')))
            if duration >= 0:
                return int(duration * 1000)
            print(t('positive_number_error'))
        except ValueError:
            print(t('enter_number_error'))

def create_silence(duration_ms):
    """Создает паузу заданной длительности"""
    return AudioSegment.silent(duration=duration_ms)

def fade_audio(audio, fade_duration):
    """Добавляет плавное начало и затухание"""
    return audio.fade_in(fade_duration).fade_out(fade_duration)

def merge_music_files(input_dir, output_file, source_format, target_format, pause_duration, fade_duration, t):
    music_files = glob.glob(os.path.join(input_dir, f"*{source_format['ext']}"))
    
    if not music_files:
        print(t('files_not_found', format=source_format['ext']))
        return
    
    print(t('found_files', count=len(music_files)))
    print(t('source_format', format=source_format['name']))
    print(t('target_format', format=target_format['name']))
    print(t('pause_duration', duration=pause_duration/1000))
    print(t('fade_duration', duration=fade_duration/1000))
    
    if not input(t('start_merge')).lower().startswith(t('yes_variants')[0][0]):
        print(t('merge_cancelled'))
        return
    
    combined = AudioSegment.empty()
    silence = create_silence(pause_duration)
    
    progress = SmoothProgress(len(music_files), desc=t('processing_files'))
    progress.start()
    
    try:
        for i, file_path in enumerate(music_files):
            try:
                progress.set_description(t('processing_file', filename=os.path.basename(file_path)))
                audio = AudioSegment.from_file(file_path, format=source_format['pydub_format'])
                audio = fade_audio(audio, fade_duration)
                combined += audio
                if i < len(music_files) - 1:
                    combined += silence
                progress.update(1)
            except Exception as e:
                print(f"\n{t('error_processing')}: {str(e)}")
    finally:
        progress.close()
    
    print(t('export_final'))
    print(t('audio_size', size=len(combined)/1000/60))
    
    export_progress = SmoothProgress(100, desc=t('exporting'), unit="%")
    export_progress.start()
    
    try:
        combined.export(
            output_file,
            format=target_format['pydub_format'],
            bitrate="192k"
        )
        export_progress.update(100)
    finally:
        export_progress.close()
    
    print(t('done', filename=output_file))

def main():
    translate, _ = get_translator()
    
    show_welcome(translate)
    source_format = get_format_choice(translate, translate('select_source_format'))
    target_format = get_format_choice(translate, translate('select_output_format'))
    pause_duration = get_pause_duration(translate)
    fade_duration = get_fade_duration(translate)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, f"combined_music{target_format['ext']}")
    
    merge_music_files(script_dir, output_file, source_format, target_format, 
                     pause_duration, fade_duration, translate)
    
    input(translate('press_enter'))

if __name__ == "__main__":
    main() 
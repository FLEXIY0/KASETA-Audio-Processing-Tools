import subprocess
import os
from ..utils.progress import SmoothProgress
import time

# Поддерживаемые форматы
SUPPORTED_FORMATS = {
    'MP3': {'ext': '.mp3', 'ffmpeg_codec': 'libmp3lame', 'quality': '-q:a 0'},
    'OGG': {'ext': '.ogg', 'ffmpeg_codec': 'libvorbis', 'quality': '-q:a 10'},
    'WAV': {'ext': '.wav', 'ffmpeg_codec': 'pcm_s16le', 'quality': ''},
    'FLAC': {'ext': '.flac', 'ffmpeg_codec': 'flac', 'quality': ''},
    'AAC': {'ext': '.aac', 'ffmpeg_codec': 'aac', 'quality': '-q:a 2'}
}

class AudioProcessor:
    def __init__(self, translator):
        self.t = translator

    def convert_audio(self, input_file, output_file, codec=None):
        """
        Конвертирует аудио файл в указанный формат с использованием указанного кодека
        """
        input_file = os.path.abspath(os.path.normpath(input_file))
        output_file = os.path.abspath(os.path.normpath(output_file))
        
        if not os.path.exists(input_file):
            error = self.t('input_file_not_found')
            print(error)
            return False, error

        try:
            # Создаем директорию для выходного файла, если её нет
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Определяем формат выходного файла
            output_ext = os.path.splitext(output_file)[1].lower()
            quality_param = ''
            
            for format_info in SUPPORTED_FORMATS.values():
                if format_info['ext'] == output_ext:
                    quality_param = format_info['quality']
                    break
            
            # Базовые параметры FFmpeg
            cmd = [
                "ffmpeg",
                "-i", input_file,  # Убираем кавычки
                "-y",  # Перезаписывать файл если существует
                "-threads", str(os.cpu_count() or 2),  # Используем все доступные ядра
                "-ar", "44100",  # Частота дискретизации
                "-ac", "2"       # Стерео
            ]

            # Добавляем параметры кодека если указан
            if codec:
                cmd.extend(["-c:a", codec])
                if quality_param:
                    cmd.extend(quality_param.split())

            # Добавляем выходной файл
            cmd.append(output_file)  # Убираем кавычки

            # Запускаем процесс с выводом ошибок
            process = subprocess.Popen(
                cmd,  # Передаем список аргументов
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                shell=False  # Отключаем shell
            )

            # Получаем вывод процесса
            stdout, stderr = process.communicate()

            # Проверяем результат
            if process.returncode != 0:
                error = f"FFmpeg error:\n{stderr}"
                print(error)
                return False, error

            return True, None

        except subprocess.CalledProcessError as e:
            error = f"FFmpeg error: {str(e)}\nOutput: {e.output if hasattr(e, 'output') else 'No output'}"
            print(error)
            return False, error
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            print(error)
            return False, error

    def prepare_files_for_merge(self, input_files, output_file):
        """
        Подготавливает файлы для слияния:
        - Проверяет форматы
        - Предлагает конвертацию если нужно
        """
        # Нормализуем входные пути
        input_files = [os.path.abspath(os.path.normpath(f)) for f in input_files]
        output_file = os.path.abspath(os.path.normpath(output_file))
        
        # Создаем временную директорию в папке output с абсолютным путем
        temp_dir = os.path.abspath(os.path.join(os.path.dirname(output_file), ".temp"))
        if os.path.exists(temp_dir):
            # Очищаем старые временные файлы
            for file in os.listdir(temp_dir):
                try:
                    os.remove(os.path.join(temp_dir, file))
                except:
                    pass
        else:
            os.makedirs(temp_dir)
        
        # Проверяем существование всех входных файлов
        for file in input_files:
            if not os.path.exists(file):
                print(f"Файл не найден: {file}")
                return None
        
        # Если все файлы одного формата, используем их как есть
        prepared_files = input_files
        
        # Проверяем, что все файлы существуют после подготовки
        for file in prepared_files:
            if not os.path.exists(file):
                print(f"Подготовленный файл не найден: {file}")
                return None
        
        return prepared_files

    def get_audio_duration(self, file_path):
        """Получает длительность аудио файла в секундах"""
        try:
            result = subprocess.check_output([
                'ffprobe', 
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ], stderr=subprocess.STDOUT)
            return float(result)
        except:
            return 0

    def merge_audio(self, input_files, output_file, pause_duration=2, fade_duration=3, fast_mode=True):
        if not input_files:
            print(self.t('no_input_files'))
            return False

        try:
            # Нормализуем пути и делаем их абсолютными
            input_files = [os.path.abspath(os.path.normpath(f)) for f in input_files]
            output_file = os.path.abspath(os.path.normpath(output_file))
            
            # Создаем директорию для выходного файла, если её нет
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            # Определяем формат выходного файла по расширению
            output_ext = os.path.splitext(output_file)[1].lower()
            output_codec = None
            quality_param = ''
            
            # Ищем соответствующий кодек и параметры качества
            for format_info in SUPPORTED_FORMATS.values():
                if format_info['ext'] == output_ext:
                    output_codec = format_info['ffmpeg_codec']
                    quality_param = format_info['quality']
                    break
            
            if not output_codec:
                print(f"Неподдерживаемый формат выходного файла: {output_ext}")
                return False

            # Подготавливаем файлы
            print(self.t('preparing_files'))
            prepared_files = self.prepare_files_for_merge(input_files, output_file)
            if prepared_files is None:
                return False

            # Создаем временные файлы с fade эффектами
            temp_dir = os.path.abspath(os.path.join(os.path.dirname(output_file), ".temp_merge"))  # Используем другую временную директорию
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Применяем fade эффекты к каждому файлу
            processed_files = []
            for i, file in enumerate(prepared_files):
                if not os.path.exists(file):
                    print(f"Файл не найден: {file}")
                    return False

                temp_file = os.path.join(temp_dir, f"temp_fade_{i}{output_ext}")
                temp_file = os.path.abspath(temp_file)
                
                # Базовые параметры для высокого качества
                fade_cmd = [
                    'ffmpeg',
                    '-i', file,
                    '-ar', '44100',
                    '-ac', '2'
                ]
                
                # Формируем цепочку аудио фильтров для fade эффектов
                if fade_duration > 0:
                    if i == 0:  # Первый файл - только fade in
                        fade_cmd.extend(['-af', f'afade=t=in:st=0:d={fade_duration}'])
                    elif i == len(prepared_files) - 1:  # Последний файл - только fade out
                        duration = self.get_audio_duration(file)
                        fade_cmd.extend(['-af', f'afade=t=out:st={duration-fade_duration}:d={fade_duration}'])
                    else:  # Остальные файлы - оба эффекта
                        duration = self.get_audio_duration(file)
                        fade_cmd.extend(['-af', f'afade=t=in:st=0:d={fade_duration},afade=t=out:st={duration-fade_duration}:d={fade_duration}'])
                
                # Добавляем параметры кодека и качества
                fade_cmd.extend(['-c:a', output_codec])
                if quality_param:
                    fade_cmd.extend(quality_param.split())
                
                fade_cmd.extend(['-y', temp_file])
                
                try:
                    subprocess.run(fade_cmd, check=True, capture_output=True, text=True)
                    if os.path.exists(temp_file):  # Проверяем, что файл создан
                        processed_files.append(temp_file)
                    else:
                        print(f"Не удалось создать временный файл: {temp_file}")
                        return False
                except subprocess.CalledProcessError as e:
                    print(f"Ошибка при обработке файла {file}:\n{e.stderr}")
                    return False

            # Создаем файл с тишиной
            silence_file = os.path.join(temp_dir, f"silence{output_ext}")
            silence_file = os.path.abspath(silence_file)
            if pause_duration > 0:
                silence_cmd = [
                    'ffmpeg',
                    '-f', 'lavfi',
                    '-i', f'anullsrc=r=44100:cl=stereo:d={pause_duration}',
                    '-c:a', output_codec
                ]
                if quality_param:
                    silence_cmd.extend(quality_param.split())
                silence_cmd.extend(['-y', silence_file])
                
                try:
                    subprocess.run(silence_cmd, check=True, capture_output=True, text=True)
                    if not os.path.exists(silence_file):  # Проверяем, что файл создан
                        print(f"Не удалось создать файл тишины: {silence_file}")
                        return False
                except subprocess.CalledProcessError as e:
                    print(f"Ошибка при создании тишины:\n{e.stderr}")
                    return False

            # Создаем список файлов для конкатенации
            concat_list = os.path.join(temp_dir, "concat_list.txt")
            concat_list = os.path.abspath(concat_list)
            with open(concat_list, 'w', encoding='utf-8') as f:
                for i, processed_file in enumerate(processed_files):
                    f.write(f"file '{processed_file}'\n")
                    if i < len(processed_files) - 1 and pause_duration > 0:
                        f.write(f"file '{silence_file}'\n")

            # Объединяем все файлы
            print("Начинаю объединение файлов...")
            concat_cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_list,
                '-ar', '44100',
                '-ac', '2',
                '-c:a', output_codec
            ]
            
            if quality_param:
                concat_cmd.extend(quality_param.split())
            
            concat_cmd.extend(['-y', output_file])

            try:
                subprocess.run(concat_cmd, check=True, capture_output=True, text=True)
                if not os.path.exists(output_file):  # Проверяем, что файл создан
                    print(f"Не удалось создать выходной файл: {output_file}")
                    return False
            except subprocess.CalledProcessError as e:
                print(f"Ошибка при объединении файлов:\n{e.stderr}")
                return False

            # Очистка временных файлов
            if os.path.exists(temp_dir):
                print(self.t('cleaning_temp_files'))
                for file in os.listdir(temp_dir):
                    try:
                        os.remove(os.path.join(temp_dir, file))
                    except:
                        pass
                try:
                    os.rmdir(temp_dir)
                except:
                    pass

            print(self.t('merge_complete'))
            return True

        except Exception as e:
            print(f"Неожиданная ошибка: {str(e)}")
            import traceback
            print(f"Подробности:\n{traceback.format_exc()}")
            return False 
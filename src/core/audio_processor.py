import subprocess
import os
from ..utils.progress import SmoothProgress
import time

class AudioProcessor:
    def __init__(self, translator):
        self.t = translator

    def convert_audio(self, input_file, output_file, codec=None):
        """
        Конвертирует аудио файл в указанный формат с использованием указанного кодека
        """
        if not os.path.exists(input_file):
            error = self.t('input_file_not_found')
            print(error)
            return False, error

        try:
            # Базовые параметры FFmpeg
            cmd = [
                "ffmpeg",
                "-i", input_file,
                "-y",  # Перезаписывать файл если существует
                "-threads", str(os.cpu_count() or 2),  # Используем все доступные ядра
                "-ar", "44100",  # Частота дискретизации
                "-ab", "320k",   # Битрейт
                "-ac", "2"       # Стерео
            ]

            # Добавляем параметры кодека если указан
            if codec:
                cmd.extend(["-c:a", codec])

            # Добавляем выходной файл
            cmd.append(output_file)

            # Запускаем процесс с выводом ошибок
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
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
        # Создаем временную директорию в папке output
        temp_dir = os.path.join(os.path.dirname(output_file), ".temp")
        if os.path.exists(temp_dir):
            # Очищаем старые временные файлы
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
        else:
            os.makedirs(temp_dir)
        
        prepared_files = []
        
        # Проверяем форматы всех файлов
        formats = set()
        for file in input_files:
            ext = os.path.splitext(file)[1].lower()
            formats.add(ext)
        
        # Если форматы разные, предлагаем конвертацию
        if len(formats) > 1:
            print(self.t('different_formats_detected'))
            print(self.t('formats_found', formats=", ".join(formats)))
            
            while True:
                print(self.t('select_target_format_merge'))
                for i, fmt in enumerate(formats, 1):
                    print(f"{i}. {fmt}")
                
                try:
                    choice = int(input(self.t('enter_format_number')))
                    if 1 <= choice <= len(formats):
                        target_format = list(formats)[choice-1]
                        break
                except ValueError:
                    print(self.t('invalid_number'))
            
            # Конвертируем файлы в выбранный формат
            for file in input_files:
                ext = os.path.splitext(file)[1].lower()
                if ext != target_format:
                    # Создаем временный файл в папке temp
                    temp_file = os.path.join(
                        temp_dir,
                        os.path.splitext(os.path.basename(file))[0] + target_format
                    )
                    if self.convert_audio(file, temp_file):
                        prepared_files.append(temp_file)
                    else:
                        print(self.t('conversion_failed_for_file', file=file))
                        return None
                else:
                    # Оставляем оригинальный файл
                    prepared_files.append(file)
        else:
            # Если все файлы одного формата, используем их как есть
            prepared_files = input_files
        
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
            # Подготавливаем файлы
            print(self.t('preparing_files'))
            prepared_files = self.prepare_files_for_merge(input_files, output_file)
            if prepared_files is None:
                return False

            # Отладочная информация
            print("\nПодготовленные файлы:")
            for f in prepared_files:
                print(f"  {f}")
            print(f"Выходной файл: {output_file}\n")

            # Рассчитываем общую длительность
            total_duration = sum(self.get_audio_duration(f) for f in prepared_files)
            print(f"Итоговая длина записи: {int(total_duration // 60)} мин {int(total_duration % 60)} сек")

            # Создаем временные файлы с fade эффектами
            temp_dir = os.path.join(os.path.dirname(output_file), ".temp")
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            # Применяем fade эффекты к каждому файлу
            processed_files = []
            for i, file in enumerate(prepared_files):
                temp_file = os.path.join(temp_dir, f"temp_fade_{i}.mp3")
                fade_cmd = ['ffmpeg', '-i', file]
                
                if fade_duration > 0:
                    if i == 0:  # Первый файл - только fade in
                        fade_cmd.extend(['-af', f'afade=t=in:st=0:d={fade_duration}'])
                    elif i == len(prepared_files) - 1:  # Последний файл - только fade out
                        duration = self.get_audio_duration(file)
                        fade_cmd.extend(['-af', f'afade=t=out:st={duration-fade_duration}:d={fade_duration}'])
                    else:  # Остальные файлы - оба эффекта
                        duration = self.get_audio_duration(file)
                        fade_cmd.extend(['-af', f'afade=t=in:st=0:d={fade_duration},afade=t=out:st={duration-fade_duration}:d={fade_duration}'])
                
                fade_cmd.extend(['-y', temp_file])
                
                try:
                    subprocess.run(fade_cmd, check=True, capture_output=True, text=True)
                    processed_files.append(temp_file)
                except subprocess.CalledProcessError as e:
                    print(f"Ошибка при обработке файла {file}:\n{e.stderr}")
                    return False

            # Создаем файл с тишиной
            silence_file = os.path.join(temp_dir, "silence.mp3")
            if pause_duration > 0:
                silence_cmd = [
                    'ffmpeg', '-f', 'lavfi', 
                    '-i', f'anullsrc=r=44100:cl=stereo:d={pause_duration}',
                    '-acodec', 'libmp3lame', '-y', silence_file
                ]
                try:
                    subprocess.run(silence_cmd, check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError as e:
                    print(f"Ошибка при создании тишины:\n{e.stderr}")
                    return False

            # Создаем список файлов для конкатенации
            concat_list = os.path.join(temp_dir, "concat_list.txt")
            with open(concat_list, 'w', encoding='utf-8') as f:
                for i, processed_file in enumerate(processed_files):
                    f.write(f"file '{processed_file}'\n")
                    if i < len(processed_files) - 1 and pause_duration > 0:
                        f.write(f"file '{silence_file}'\n")

            # Объединяем все файлы
            print("Начинаю объединение файлов...")
            concat_cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', concat_list,
                '-c', 'copy',
                '-y', output_file
            ]

            try:
                process = subprocess.run(concat_cmd, capture_output=True, text=True, check=True)
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
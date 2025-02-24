import os

# Получаем путь к корневой директории проекта
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Пути к папкам с музыкой
MUSIC_DIR = os.path.join(PROJECT_ROOT, 'music')
MUSIC_INPUT_DIR = os.path.join(MUSIC_DIR, 'input')
MUSIC_OUTPUT_DIR = os.path.join(MUSIC_DIR, 'output')

def ensure_dirs_exist():
    """Создает необходимые директории, если они не существуют"""
    for dir_path in [MUSIC_DIR, MUSIC_INPUT_DIR, MUSIC_OUTPUT_DIR]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path) 
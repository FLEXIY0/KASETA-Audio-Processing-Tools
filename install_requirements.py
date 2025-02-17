import subprocess
import sys
import os
from tqdm import tqdm
from translations import get_translator
import signal
from smooth_progress import SmoothProgress

def signal_handler(sig, frame):
    print('\nПрограмма прервана пользователем.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def ask_confirmation(t):
    print(t('installation_components'))
    print(t('python_packages'))
    with open(os.path.join(os.path.dirname(__file__), 'requirements.txt'), 'r') as f:
        for line in f:
            if line.strip():
                print(f"   - {line.strip()}")
    print(t('check_ffmpeg'))
    
    print(t('requirements'))
    print(t('python_version'))
    print(t('internet_access'))
    print(t('install_rights'))
    
    while True:
        response = input(t('continue_install')).lower()
        if response in t('yes_variants'):
            return True
        elif response in t('no_variants'):
            return False
        else:
            print(t('select_format_error'))

def install_requirements(t):
    # Проверяем наличие pip
    try:
        import pip
    except ImportError:
        print("Pip не установлен. Пожалуйста, установите pip сначала.")
        return False

    # Читаем requirements.txt
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    
    if not os.path.exists(requirements_path):
        print("Файл requirements.txt не найден!")
        return False

    with open(requirements_path, 'r') as f:
        requirements = [line.strip() for line in f if line.strip()]

    print(t('found_packages', count=len(requirements)))

    # Устанавливаем каждый пакет с плавным прогресс баром
    progress = SmoothProgress(len(requirements), desc=t('installing_packages'))
    progress.start()
    
    try:
        for package in requirements:
            try:
                progress.set_description(t('installing', package=package))
                subprocess.check_call([sys.executable, "-m", "pip", "install", package],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                progress.update(1)
            except subprocess.CalledProcessError as e:
                print(f"\n{t('install_error')}: {str(e)}")
                return False
    finally:
        progress.close()

    print(t('all_packages_installed'))
    
    # Проверяем наличие ffmpeg
    try:
        subprocess.check_call(["ffmpeg", "-version"],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
        print(t('ffmpeg_installed'))
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(t('ffmpeg_not_found'))
        print(t('install_ffmpeg'))
        print(t('windows_ffmpeg'))
        print(t('linux_ffmpeg'))
        print(t('macos_ffmpeg'))
        return False

    return True

if __name__ == "__main__":
    # Получаем переводчик
    translate, _ = get_translator()
    
    print(translate('welcome_installer'))
    
    if not ask_confirmation(translate):
        print(translate('install_cancelled'))
        sys.exit(0)
        
    print(translate('starting_install'))
    if install_requirements(translate):
        print(translate('install_success'))
        print(translate('can_use_scripts'))
        input(translate('press_enter'))
    else:
        print(translate('install_error'))
        input(translate('press_enter')) 
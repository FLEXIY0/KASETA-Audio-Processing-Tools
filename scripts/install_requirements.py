import sys
import os
import signal
from src.utils.translations import get_translator
from src.core.installer import Installer

def signal_handler(sig, frame):
    print('\nПрограмма прервана пользователем.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def ask_confirmation(t):
    print(t('installation_components'))
    print(t('python_packages'))
    
    requirements_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    with open(requirements_path, 'r') as f:
        for line in f:
            if line.strip():
                print(f"   - {line.strip()}")
    print(t('check_ffmpeg'))
    
    print(t('requirements'))
    print(t('python_version'))
    print(t('internet_access'))
    print(t('install_rights'))
    
    while True:
        response = input(t('continue_install') + " (y/n): ").lower()
        if response == 'y':
            return True
        elif response == 'n':
            return False
        else:
            print(t('select_format_error'))

def main():
    translate, _ = get_translator()
    installer = Installer(translate)
    
    print(translate('welcome_installer'))
    
    if not ask_confirmation(translate):
        print(translate('install_cancelled'))
        sys.exit(0)
        
    print(translate('starting_install'))
    
    if not installer.check_pip():
        sys.exit(1)
        
    requirements_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
    if installer.install_packages(requirements_path) and installer.check_ffmpeg():
        print(translate('install_success'))
        print(translate('can_use_scripts'))
        input(translate('press_enter'))
    else:
        print(translate('install_error'))
        input(translate('press_enter'))

if __name__ == "__main__":
    main() 
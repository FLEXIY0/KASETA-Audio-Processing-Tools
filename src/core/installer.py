import subprocess
import sys
import os
from ..utils.progress import SmoothProgress

class Installer:
    def __init__(self, translator):
        self.t = translator
        
    def check_pip(self):
        try:
            import pip
            return True
        except ImportError:
            print(self.t('pip_not_found'))
            return False
            
    def check_ffmpeg(self):
        try:
            subprocess.check_call(["ffmpeg", "-version"],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
            print(self.t('ffmpeg_installed'))
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(self.t('ffmpeg_not_found'))
            print(self.t('install_ffmpeg'))
            print(self.t('windows_ffmpeg'))
            print(self.t('linux_ffmpeg'))
            print(self.t('macos_ffmpeg'))
            return False
            
    def install_packages(self, requirements_path):
        if not os.path.exists(requirements_path):
            print(self.t('requirements_not_found'))
            return False
            
        with open(requirements_path, 'r') as f:
            requirements = [line.strip() for line in f if line.strip()]
            
        print(self.t('found_packages', count=len(requirements)))
        
        progress = SmoothProgress(len(requirements), desc=self.t('installing_packages'))
        progress.start()
        
        try:
            for package in requirements:
                try:
                    progress.set_description(self.t('installing', package=package))
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package],
                                       stdout=subprocess.DEVNULL,
                                       stderr=subprocess.DEVNULL)
                    progress.update(1)
                except subprocess.CalledProcessError as e:
                    print(f"\n{self.t('install_error')}: {str(e)}")
                    return False
        finally:
            progress.close()
            
        print(self.t('all_packages_installed'))
        return True 
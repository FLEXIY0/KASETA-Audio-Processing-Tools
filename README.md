# KASETA - Audio Processing Tools
<p align="center">
  <img src="https://github.com/user-attachments/assets/7c0bd2ba-7f10-4af9-bce7-d55ad94279c2" alt="KASETA Logo" width="400">
</p>




<p align="center">
  <a href="https://github.com/FLEXIY0/Lotus-Smart-Markdown-Editor-for-Android/stargazers"><img src="https://img.shields.io/github/stars/FLEXIY0/Lotus-Smart-Markdown-Editor-for-Android?style=for-the-badge&logo=github&color=gold" alt="GitHub stars"></a>
  <a href="https://discord.com/users/1170835455755964469"><img src="https://img.shields.io/badge/Discord-Join-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="https://x.com/FLEXIY0"><img src="https://img.shields.io/badge/Twitter-Follow-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white" alt="Twitter Follow"></a>
  <a href="https://www.donationalerts.com/r/nedoedal"><img src="https://img.shields.io/badge/Donate-Support_Project-ED1C24?style=for-the-badge&logo=heart&logoColor=white" alt="Donate"></a>
  <a href="https://github.com/FLEXIY0/KASETA-Audio-Processing-Tools/releases/tag/v1.0"><img src="https://img.shields.io/badge/Release-Latest-2ea44f?style=for-the-badge&logo=github" alt="Latest Release"></a>
</p>


## English | [Русский](#русский)

## Overview

KASETA is a powerful desktop application for audio file processing, developed with Python and PyQt5. The application provides a user-friendly interface for converting and merging audio files with a retro design inspired by classic operating systems.

## Features

- **Audio File Conversion**: Convert between various audio formats (MP3, WAV, OGG, FLAC, AAC)
- **Audio File Merging**: Combine multiple audio files into one with customizable fade effects
- **Visual Progress Tracking**: Real-time visual feedback during operations
- **Multi-language Support**: Interface available in multiple languages (English, Russian)
- **Themeable Interface**: Multiple visual themes including Modern, Retro, and Windows 98 style
- **Cross-platform**: Works on Windows, Linux, and macOS

## Requirements

- Python 3.6 or newer
- FFmpeg (must be installed on your system)
- Dependencies listed in requirements.txt

## Installation

### Windows

1. Install [Python 3.6+](https://www.python.org/downloads/) (make sure to check "Add Python to PATH")
2. Install [FFmpeg](https://ffmpeg.org/download.html) and add it to your PATH
3. Download or clone this repository
4. Run `run.bat` - it will set up a virtual environment and install dependencies automatically

### Linux

1. Install Python 3.6+ and FFmpeg:
   ```bash
   # For Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv ffmpeg
   
   # For Fedora
   sudo dnf install python3 python3-pip ffmpeg
   ```

2. Download or clone this repository
3. Make the launch script executable:
   ```bash
   sed -i 's/\r$//' run.sh
   chmod +x run.sh
   ```
4. Run the application:
   ```bash
   ./run.sh
   ```

### macOS

1. Install [Homebrew](https://brew.sh/) if you don't have it:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Install Python and FFmpeg:
   ```bash
   brew install python ffmpeg
   ```

3. Download or clone this repository
4. Make the launch script executable:
   ```bash
   chmod +x run_mac.sh
   ```
5. Run the application:
   ```bash
   ./run_mac.sh
   ```

## Usage

### Converting Audio Files

1. Launch the application and click on the "Audio Converter" button
2. Select the audio files you want to convert
3. Choose the output format from the dropdown menu
4. Click the "Convert" button
5. The converted files will be saved in the output directory

### Merging Audio Files

1. Launch the application and click on the "Audio Merger" button
2. Select the audio files you want to merge
3. Arrange them in the desired order using the "Up" and "Down" buttons
4. Adjust the fade settings if needed
5. Click the "Merge" button
6. The merged file will be saved in the output directory

## Tips and Troubleshooting

- For macOS users: If you encounter issues with PyQt5 installation, install it through Homebrew with `brew install pyqt5`
- The application automatically creates input and output directories in the music folder
- All files should be in the same format before merging; you can use the converter first if needed
- If the interface language displays incorrectly, try restarting the application after changing the language
- The "Always on top" option makes the application stay on top of other windows

## Project Structure

```
├── scripts/               # Launch scripts
│   └── run_gui.py         # Main application script
├── src/                   # Source code
│   ├── core/              # Core functionality
│   ├── gui/               # GUI components
│   ├── translations/      # Translation files (JSON)
│   └── utils/             # Utilities
├── music/                 # Directory for music files
│   ├── input/             # Input files
│   └── output/            # Output files
├── run.bat                # Windows launch script
├── run.sh                 # Linux launch script
├── run_mac.sh             # macOS launch script
└── requirements.txt       # Project dependencies
```

---

# <a name="русский"></a>KASETA - Инструменты обработки аудио

<p align="center">
  <img src="https://github.com/user-attachments/assets/7c0bd2ba-7f10-4af9-bce7-d55ad94279c2" alt="KASETA Logo" width="400">
</p>

## [English](#kaseta---audio-processing-tools) | Русский

## Обзор

KASETA - мощное настольное приложение для обработки аудио файлов, разработанное с использованием Python и PyQt5. Приложение предоставляет удобный интерфейс для конвертации и объединения аудио файлов с ретро-дизайном, вдохновленным классическими операционными системами.

## Возможности

- **Конвертация аудио файлов**: Преобразование между различными форматами (MP3, WAV, OGG, FLAC, AAC)
- **Объединение аудио файлов**: Комбинирование нескольких аудио файлов в один с настраиваемыми эффектами затухания
- **Визуальное отслеживание прогресса**: Отображение хода выполнения операций в реальном времени
- **Многоязычная поддержка**: Интерфейс доступен на нескольких языках (русский, английский)
- **Настраиваемый интерфейс**: Несколько визуальных тем, включая Современную, Ретро и стиль Windows 98
- **Кроссплатформенность**: Работает на Windows, Linux и macOS

## Требования

- Python 3.6 или новее
- FFmpeg (должен быть установлен в системе)
- Зависимости, перечисленные в requirements.txt

## Установка

### Windows

1. Установите [Python 3.6+](https://www.python.org/downloads/) (убедитесь, что отмечен пункт "Add Python to PATH")
2. Установите [FFmpeg](https://ffmpeg.org/download.html) и добавьте его в PATH
3. Скачайте или клонируйте этот репозиторий
4. Запустите `run.bat` - он автоматически настроит виртуальное окружение и установит зависимости

### Linux

1. Установите Python 3.6+ и FFmpeg:
   ```bash
   # Для Ubuntu/Debian
   sudo apt update
   sudo apt install python3 python3-pip python3-venv ffmpeg
   
   # Для Fedora
   sudo dnf install python3 python3-pip ffmpeg
   ```

2. Скачайте или клонируйте этот репозиторий
3. Сделайте скрипт запуска исполняемым:
   ```bash
   sed -i 's/\r$//' run.sh
   chmod +x run.sh
   ```
4. Запустите приложение:
   ```bash
   ./run.sh
   ```

### macOS

1. Установите [Homebrew](https://brew.sh/), если у вас его нет:
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Установите Python и FFmpeg:
   ```bash
   brew install python ffmpeg
   ```

3. Скачайте или клонируйте этот репозиторий
4. Сделайте скрипт запуска исполняемым:
   ```bash
   chmod +x run_mac.sh
   ```
5. Запустите приложение:
   ```bash
   ./run_mac.sh
   ```

## Использование

### Конвертация аудио файлов

1. Запустите приложение и нажмите кнопку "Конвертер аудио"
2. Выберите аудио файлы, которые хотите конвертировать
3. Выберите выходной формат из выпадающего меню
4. Нажмите кнопку "Конвертировать"
5. Конвертированные файлы будут сохранены в выходной директории

### Объединение аудио файлов

1. Запустите приложение и нажмите кнопку "Объединение аудио"
2. Выберите аудио файлы, которые хотите объединить
3. Расположите их в нужном порядке с помощью кнопок "Вверх" и "Вниз"
4. При необходимости настройте параметры затухания
5. Нажмите кнопку "Объединить"
6. Объединенный файл будет сохранен в выходной директории

## Советы и устранение проблем

- Для пользователей macOS: Если возникают проблемы с установкой PyQt5, установите его через Homebrew командой `brew install pyqt5`
- Приложение автоматически создает входную и выходную директории в папке music
- Все файлы должны быть в одном формате перед объединением; при необходимости сначала используйте конвертер
- Если язык интерфейса отображается некорректно, попробуйте перезапустить приложение после смены языка
- Опция "Всегда поверх" позволяет приложению оставаться поверх других окон

## Структура проекта

```
├── scripts/               # Скрипты запуска
│   └── run_gui.py         # Основной скрипт приложения
├── src/                   # Исходный код
│   ├── core/              # Основная функциональность
│   ├── gui/               # Компоненты GUI
│   ├── translations/      # Файлы переводов (JSON)
│   └── utils/             # Утилиты
├── music/                 # Директория для музыкальных файлов
│   ├── input/             # Входные файлы
│   └── output/            # Выходные файлы
├── run.bat                # Скрипт запуска для Windows
├── run.sh                 # Скрипт запуска для Linux
├── run_mac.sh             # Скрипт запуска для macOS
└── requirements.txt       # Зависимости проекта
``` 

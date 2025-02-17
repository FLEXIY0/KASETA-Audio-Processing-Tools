from PIL import Image
import numpy as np
import os

# Получаем текущую директорию скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))

def enhance_leather_color(img, target_color, mix_ratio=0.7):
    # Конвертируем в numpy массив
    data = np.array(img)
    
    # Сохраняем альфа-канал
    alpha = data[..., 3]
    
    # Применяем новый цветовой баланс для RGB каналов
    for i in range(3):
        data[..., i] = (data[..., i] * (1 - mix_ratio) + target_color[i] * mix_ratio).astype(np.uint8)
    
    # Восстанавливаем оригинальный альфа-канал
    data[..., 3] = alpha
    
    return Image.fromarray(data)

# Целевые цвета (R, G, B) - более насыщенные коричневые
leather1_color = (190, 100, 50)  # Более теплый коричневый для основной текстуры
leather2_color = (230, 140, 70)  # Более светлый теплый коричневый для оверлея

# Пути к файлам текстур
leather1_path = os.path.join(script_dir, 'armor', 'leather_1.png')
leather2_path = os.path.join(script_dir, 'armor', 'leather_2.png')

print(f"Ищу файлы по путям:\n{leather1_path}\n{leather2_path}")

# Обработка leather_1.png
img1 = Image.open(leather1_path).convert('RGBA')
new_img1 = enhance_leather_color(img1, leather1_color)
new_img1.save(leather1_path)

# Обработка leather_2.png
img2 = Image.open(leather2_path).convert('RGBA')
new_img2 = enhance_leather_color(img2, leather2_color)
new_img2.save(leather2_path)

print("Текстуры успешно перекрашены!") 
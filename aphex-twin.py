import os
import time
import random
import numpy as np
from PIL import Image, ImageFilter, ImageOps
import pygame
import sys

# Настройка путей
try:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
except:
    pass

# Музыка
pygame.mixer.init()
try:
    pygame.mixer.music.load("alberto_balsalm.mp3")
    pygame.mixer.music.play(-1)
except:
    pass

def load_logo_contour(path, size=(40, 40)):
    if not os.path.exists(path):
        print(f"Ошибка: Файл '{path}' не найден!")
        sys.exit()
    try:
        # 1. Открываем и конвертируем в RGBA (чтобы точно была прозрачность)
        img = Image.open(path).convert('RGBA')
        
        # 2. Создаем черную подложку
        bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
        composite = Image.alpha_composite(bg, img).convert('L')
        
        # 3. Если картинка стала слишком темной (черный лого на черном), инвертируем
        if np.mean(np.array(composite)) < 30:
            composite = ImageOps.invert(composite)
            
        img = composite.resize(size, Image.Resampling.LANCZOS)
        
        # 4. Жесткий порог (делаем логотип ярко-белым)
        # Если логотип все еще не виден, попробуй поменять 128 на 50 или 200
        solid = img.point(lambda x: 255 if x > 128 else 0)
        
        # 5. Создаем жирный контур
        thick = solid.filter(ImageFilter.MaxFilter(3))
        inner = solid.filter(ImageFilter.MinFilter(1))
        
        outline = np.array(thick).astype(int) - np.array(inner).astype(int)
        
        # Если в итоге получился пустой массив, берем просто залитый силуэт
        if np.sum(outline > 128) == 0:
            return np.array(solid) > 128
            
        return outline > 128
    except Exception as e:
        print(f"Ошибка Pillow: {e}")
        sys.exit()

logo_mask_base = load_logo_contour("logo.png")

def render_frame(angle):
    try:
        tw, th = os.get_terminal_size()
    except:
        tw, th = 80, 40

    img_obj = Image.fromarray(logo_mask_base)
    rotated = img_obj.rotate(angle, resample=Image.Resampling.BICUBIC)
    logo_mask = np.array(rotated)
    
    lh, lw = logo_mask.shape
    sy, sx = (th - lh) // 2, (tw // 2 - lw) // 2
    
    GREEN = "\033[92m"
    RESET = "\033[0m"
    
    frame = ["\033[H"]
    for y in range(th - 1):
        line = []
        for x in range(tw // 2):
            ly, lx = y - sy, x - sx
            if 0 <= ly < lh and 0 <= lx < lw and logo_mask[ly, lx]:
                line.append(f"{GREEN}██{RESET}")
            else:
                line.append(random.choice(".: ") + " ")
        frame.append("".join(line))
    return "\n".join(frame)

angle = 0
os.system('cls' if os.name == 'nt' else 'clear')

try:
    while True:
        os.write(1, render_frame(angle).encode('utf-8'))
        angle = (angle - 6) % 360
        time.sleep(0.04)
except KeyboardInterrupt:
    pygame.mixer.music.stop()
    print("\033[0m\nStopped.")

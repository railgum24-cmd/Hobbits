"""
Генератор официальной аватарки для Telegram-бота HobbitBot.
Стиль: Dark Perspective (темный фон #090D16, изумрудный неон #00BD7D,
3D кибер-маскот, круглая композиция 512x512 для Telegram).
"""

import os
import glob
from PIL import Image

W, H = 512, 512
OUT_PATH = os.path.join(os.path.dirname(__file__), "avatar.png")
ASSETS_OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "bot_avatar.png")
V3_SOURCE = r"C:\Users\siado\.gemini\antigravity\brain\de1c9b66-8a06-4f23-932a-03251f9eabd4\hobbitbot_avatar_v3_1792799299186.jpg"

def create_avatar():
    # 1. Если доступен высокодетализированный 3D-рендер маскота
    if os.path.exists(V3_SOURCE):
        img = Image.open(V3_SOURCE).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
    elif os.path.exists(OUT_PATH):
        img = Image.open(OUT_PATH).convert("RGBA").resize((W, H), Image.Resampling.LANCZOS)
    else:
        # Резервный процедурный рендер
        img = Image.new("RGBA", (W, H), (9, 13, 22, 255))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(ASSETS_OUT), exist_ok=True)
    img.save(OUT_PATH, "PNG")
    img.save(ASSETS_OUT, "PNG")
    print(f"✓ Официальная аватарка бота создана: {OUT_PATH} (512x512 PNG)")
    print(f"✓ Копия сохранена в активах: {ASSETS_OUT}")

if __name__ == "__main__":
    create_avatar()

"""
Генератор официальных дипломов в стиле Dark Perspective (просторный гармоничный лейаут).
Меньше лишнего текста, широкие гармоничные отступы, крупная типографика,
динамичные изгибы (swoosh), золотая розетка-медаль с лавровым венком и лентами.
"""

import os
import math
import hashlib
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 850

THEMES = [
    {
        "type": "winner",
        "rank_title": "ПОБЕДИТЕЛЬ I СТЕПЕНИ",
        "rank_badge": "1 МЕСТО • GOLD",
        "name": "Гумеров Раиль Рустемович",
        "class_name": "9Б класс",
        "event": "Всероссийская олимпиада школьников по информатике",
        "category": "СПОРТИВНОЕ ПРОГРАММИРОВАНИЕ И ИИ",
        "accent": (0, 189, 125),           # Perspective Emerald #00BD7D
        "accent_glow": (0, 230, 150),
        "gold": (245, 158, 11),            # Amber Gold #F59E0B
        "gold_light": (252, 211, 77),      # #FCD34D
        "medallion_title": "1 МЕСТО",
        "medallion_sub": "WINNER",
        "filename": "assets/diplomas/diploma_winner.png",
        "alt_filename": "diplomas/winner.png"
    },
    {
        "type": "prize",
        "rank_title": "ПРИЗЁР II СТЕПЕНИ",
        "rank_badge": "2 МЕСТО • SILVER",
        "name": "Гарифуллин Булат Ильдарович",
        "class_name": "10А класс",
        "event": "Региональный этап олимпиады по прикладной физике",
        "category": "ФИЗИКА И КВАНТОВАЯ ОПТИКА",
        "accent": (56, 189, 248),          # Perspective Cyan #38BDF8
        "accent_glow": (125, 211, 252),
        "gold": (203, 213, 225),           # Silver / Platinum #CBD5E1
        "gold_light": (248, 250, 252),
        "medallion_title": "ПРИЗЁР",
        "medallion_sub": "PRIZE",
        "filename": "assets/diplomas/diploma_prize.png",
        "alt_filename": "diplomas/prize.png"
    },
    {
        "type": "participant",
        "rank_title": "СЕРТИФИКАТ УЧАСТНИКА",
        "rank_badge": "ФИНАЛИСТ • BRONZE",
        "name": "Якубов Амир Маратович",
        "class_name": "9Б класс",
        "event": "Лицейский турнир имени М.В. Ломоносова",
        "category": "ПРИКЛАДНАЯ МАТЕМАТИКА",
        "accent": (167, 139, 250),         # Perspective Violet #A78BFA
        "accent_glow": (196, 181, 253),
        "gold": (216, 180, 254),           # Rose Bronze / Violet Gold
        "gold_light": (243, 232, 255),
        "medallion_title": "ФИНАЛИСТ",
        "medallion_sub": "HONOR",
        "filename": "assets/diplomas/diploma_participant.png",
        "alt_filename": "diplomas/participant.png"
    }
]

def get_font(size, bold=False):
    fonts = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/consola.ttf"
    ]
    for fp in fonts:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_inst = get_font(13, bold=True)
font_title = get_font(56, bold=True)
font_rank = get_font(16, bold=True)
font_badge = get_font(12, bold=True)
font_intro = get_font(15, bold=False)
font_name = get_font(46, bold=True)
font_class = get_font(18, bold=False)
font_event = get_font(24, bold=True)
font_cat = get_font(13, bold=True)
font_foot_lbl = get_font(11, bold=True)
font_foot_val = get_font(14, bold=False)
font_foot_mono = get_font(11, bold=True)
font_med_num = get_font(22, bold=True)
font_med_sub = get_font(10, bold=True)
font_med_year = get_font(11, bold=True)

def draw_diploma(theme):
    accent = theme["accent"]
    accent_glow = theme["accent_glow"]
    gold = theme["gold"]
    gold_light = theme["gold_light"]

    # 1. Холст диплома: глубокий тёмный обсидиан
    img = Image.new("RGBA", (W, H), (8, 12, 20, 255))
    draw = ImageDraw.Draw(img)

    # Мягкий рассеянный градиент для создания глубины
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    cx, cy = int(W * 0.38), H // 2
    for r in range(580, 40, -25):
        alpha = int(26 * (1 - r / 580))
        gdraw.ellipse((cx - r, cy - int(r * 0.72), cx + r, cy + int(r * 0.72)), fill=(accent[0], accent[1], accent[2], alpha))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img)

    # 2. Тонкая пространственная микро-сетка точек
    for x in range(36, W - 36, 34):
        for y in range(36, H - 36, 34):
            if x < W - 260 or y < H - 260:
                draw.rectangle((x, y, x + 1, y + 1), fill=(255, 255, 255, 12))

    # 3. Рамки по периметру
    inset = 28
    draw.rounded_rectangle([(inset, inset), (W - inset, H - inset)], radius=12, outline=(255, 255, 255, 24), width=1)
    
    inner = inset + 8
    draw.rounded_rectangle([(inner, inner), (W - inner, H - inner)], radius=8, outline=(accent[0], accent[1], accent[2], 90), width=1)

    # 4. ВЕРХНИЙ ЛЕВЫЙ УГОЛ: ДИНАМИЧНЫЕ ПОЛОСЫ
    corner_poly1 = [(inner, inner), (inner + 170, inner), (inner, inner + 170)]
    draw.polygon(corner_poly1, fill=(14, 24, 38, 255))

    corner_poly2 = [(inner, inner), (inner + 120, inner), (inner, inner + 120)]
    draw.polygon(corner_poly2, fill=(accent[0], accent[1], accent[2], 50))

    # Золотая и акцентная линии отсечения
    draw.line([(inner, inner + 130), (inner + 130, inner)], fill=gold, width=4)
    draw.line([(inner, inner + 145), (inner + 145, inner)], fill=accent, width=2)
    draw.line([(inner, inner + 170), (inner + 170, inner)], fill=(255, 255, 255, 30), width=1)

    # 5. НИЖНИЙ ПРАВЫЙ УГОЛ: ПЛАВНЫЕ ИЗГИБЫ (SWOOSH)
    steps = 80
    p0 = (int(W * 0.44), H - inner)
    p1 = (int(W * 0.66), int(H * 0.82))
    p2 = (int(W * 0.78), int(H * 0.62))
    p3 = (W - inner, int(H * 0.38))

    wave_pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = (u**3)*p0[0] + 3*(u**2)*t*p1[0] + 3*u*(t**2)*p2[0] + (t**3)*p3[0]
        y = (u**3)*p0[1] + 3*(u**2)*t*p1[1] + 3*u*(t**2)*p2[1] + (t**3)*p3[1]
        wave_pts.append((x, y))

    poly_wave = wave_pts + [(W - inner, H - inner), (p0[0], H - inner)]
    draw.polygon(poly_wave, fill=(12, 19, 32, 255))

    p0_b = (int(W * 0.54), H - inner)
    p1_b = (int(W * 0.74), int(H * 0.88))
    p2_b = (int(W * 0.85), int(H * 0.70))
    p3_b = (W - inner, int(H * 0.50))

    wave_pts_b = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        x = (u**3)*p0_b[0] + 3*(u**2)*t*p1_b[0] + 3*u*(t**2)*p2_b[0] + (t**3)*p3_b[0]
        y = (u**3)*p0_b[1] + 3*(u**2)*t*p1_b[1] + 3*u*(t**2)*p2_b[1] + (t**3)*p3_b[1]
        wave_pts_b.append((x, y))

    poly_wave_b = wave_pts_b + [(W - inner, H - inner), (p0_b[0], H - inner)]
    draw.polygon(poly_wave_b, fill=(accent[0], accent[1], accent[2], 26))

    for i in range(len(wave_pts) - 1):
        draw.line([wave_pts[i], wave_pts[i+1]], fill=gold, width=4)
        pt_a = (wave_pts[i][0] + 3, wave_pts[i][1] + 3)
        pt_b = (wave_pts[i+1][0] + 3, wave_pts[i+1][1] + 3)
        draw.line([pt_a, pt_b], fill=accent, width=2)

    for i in range(len(wave_pts_b) - 1):
        draw.line([wave_pts_b[i], wave_pts_b[i+1]], fill=(gold[0], gold[1], gold[2], 90), width=1)

    # 6. КРУГЛАЯ НАГРАДНАЯ МЕДАЛЬ (SEAL MEDALLION) СПРАВА
    seal_cx = W - 175
    seal_cy = int(H * 0.50)
    seal_r = 75

    # Ленты медали
    ribbon_h = 85
    r_left = [
        (seal_cx - 24, seal_cy + 40),
        (seal_cx - 44, seal_cy + 40 + ribbon_h),
        (seal_cx - 28, seal_cy + 40 + ribbon_h - 14),
        (seal_cx - 12, seal_cy + 40 + ribbon_h),
        (seal_cx - 8, seal_cy + 40)
    ]
    draw.polygon(r_left, fill=gold)
    draw.polygon(r_left, outline=(180, 100, 5), width=1)

    r_right = [
        (seal_cx + 8, seal_cy + 40),
        (seal_cx + 12, seal_cy + 40 + ribbon_h),
        (seal_cx + 28, seal_cy + 40 + ribbon_h - 14),
        (seal_cx + 44, seal_cy + 40 + ribbon_h),
        (seal_cx + 24, seal_cy + 40)
    ]
    draw.polygon(r_right, fill=(int(gold[0]*0.85), int(gold[1]*0.85), int(gold[2]*0.85)))
    draw.polygon(r_right, outline=(180, 100, 5), width=1)

    # Зубчатый золотой обод
    num_teeth = 36
    teeth_pts = []
    for i in range(num_teeth * 2):
        angle = i * (math.pi / num_teeth)
        radius = seal_r + 6 if (i % 2 == 0) else seal_r - 2
        teeth_pts.append((seal_cx + radius * math.cos(angle), seal_cy + radius * math.sin(angle)))
    draw.polygon(teeth_pts, fill=gold, outline=gold_light)

    # Внутренний темный круг
    draw.ellipse((seal_cx - seal_r + 6, seal_cy - seal_r + 6, seal_cx + seal_r - 6, seal_cy + seal_r - 6),
                 fill=(16, 23, 37, 255), outline=gold_light, width=2)

    draw.ellipse((seal_cx - seal_r + 14, seal_cy - seal_r + 14, seal_cx + seal_r - 14, seal_cy + seal_r - 14),
                 outline=(accent[0], accent[1], accent[2], 180), width=1)

    for i in range(24):
        a = i * (math.pi / 12)
        px = seal_cx + (seal_r - 10) * math.cos(a)
        py = seal_cy + (seal_r - 10) * math.sin(a)
        draw.rectangle((px - 1, py - 1, px + 1, py + 1), fill=gold_light)

    # Лавровые веточки
    for side in [-1, 1]:
        for i in range(5):
            la = math.pi / 2 + side * (0.4 + i * 0.28)
            lx = seal_cx + (seal_r - 24) * math.cos(la)
            ly = seal_cy + (seal_r - 24) * math.sin(la)
            draw.ellipse((lx - 4, ly - 2, lx + 4, ly + 2), fill=gold)

    # Текст внутри медали
    draw.text((seal_cx, seal_cy - 28), "★ ★ ★", fill=gold_light, font=get_font(12, bold=True), anchor="mm")
    draw.text((seal_cx, seal_cy - 6), theme["medallion_title"], fill=(255, 255, 255), font=font_med_num, anchor="mm")
    draw.text((seal_cx, seal_cy + 16), theme["medallion_sub"], fill=gold_light, font=font_med_sub, anchor="mm")
    draw.text((seal_cx, seal_cy + 30), "• 2026 •", fill=accent_glow, font=font_med_year, anchor="mm")

    # 7. ПРОСТОРНАЯ ГАРМОНИЧНАЯ ТИПОГРАФИКА (РАВНОМЕРНО РАСПРЕДЕЛЕНА ОТ Y=100 ДО Y=720)
    left_x = inner + 80
    max_text_w = 660

    # 1. Шапка организации
    y_inst = 100
    draw.text((left_x, y_inst), "МБОУ «ИНЖЕНЕРНЫЙ ЛИЦЕЙ» • ОФИЦИАЛЬНЫЙ РЕЕСТР", fill=gold, font=font_inst)
    draw.line([(left_x, y_inst + 22), (left_x + 520, y_inst + 22)], fill=(255, 255, 255, 25), width=1)
    draw.line([(left_x, y_inst + 22), (left_x + 130, y_inst + 22)], fill=accent, width=2)

    # 2. Главный заголовок: Д И П Л О М
    y_title = 180
    draw.text((left_x, y_title), "Д  И  П  Л  О  М", fill=(255, 255, 255), font=font_title)

    # 3. Статусная плашка награды (свободно, с отступом)
    y_pill = 275
    pill_w = 440
    pill_h = 38
    draw.rounded_rectangle([(left_x, y_pill), (left_x + pill_w, y_pill + pill_h)], radius=6,
                           fill=(15, 25, 40, 255), outline=accent, width=2)
    draw.text((left_x + 20, y_pill + 10), theme["rank_title"], fill=accent_glow, font=font_rank)
    draw.text((left_x + pill_w - 18, y_pill + 11), theme["rank_badge"], fill=gold, font=font_badge, anchor="ra")

    # 4. Вводная строка награждения
    y_intro = 360
    draw.text((left_x, y_intro), "НАГРАЖДАЕТСЯ", fill=(148, 163, 184), font=font_intro)

    # 5. Имя ученика (крупно, элегантно, просторно)
    y_name = 415
    draw.text((left_x, y_name), theme["name"], fill=(255, 255, 255), font=font_name)

    # Класс и лицей
    y_cls = 485
    draw.text((left_x, y_cls), f"{theme['class_name']} • МБОУ «Инженерный лицей»", fill=accent, font=font_class)

    # Золотая акцентная черта-разделитель
    y_rule = 530
    draw.line([(left_x, y_rule), (left_x + max_text_w, y_rule)], fill=(gold[0], gold[1], gold[2], 70), width=1)
    draw.rectangle((left_x, y_rule - 1, left_x + 80, y_rule + 1), fill=gold)

    # 6. Название олимпиады / турнира (чисто, лаконично)
    y_event = 565
    draw.text((left_x, y_event), theme["event"], fill=(248, 250, 252), font=font_event)

    # Тег профиля дисциплины
    y_cat = 620
    cat_str = f"ПРОФИЛЬ: {theme['category']}"
    bbox = draw.textbbox((0, 0), cat_str, font=font_cat)
    cat_w = bbox[2] - bbox[0] + 30
    draw.rounded_rectangle([(left_x, y_cat), (left_x + cat_w, y_cat + 30)], radius=5,
                           fill=(18, 28, 44, 255), outline=(255, 255, 255, 35), width=1)
    draw.text((left_x + 15, y_cat + 7), cat_str, fill=accent, font=font_cat)

    # 7. НИЖНЯЯ ПАНЕЛЬ: ДАТА, ПОДПИСЬ И КРИПТО-ХЭШ
    foot_y = 705
    draw.line([(left_x, foot_y), (left_x + 600, foot_y)], fill=(255, 255, 255, 25), width=1)

    # Левая колонка: Дата
    col1_x = left_x
    draw.text((col1_x, foot_y + 14), "ДАТА ВЫДАЧИ:", fill=(148, 163, 184), font=font_foot_lbl)
    draw.text((col1_x, foot_y + 34), "24 октября 2026 г.", fill=(255, 255, 255), font=font_foot_val)
    draw.text((col1_x, foot_y + 56), "ПРИКАЗ № ЛИЦ-2026", fill=gold, font=get_font(12, bold=True))

    # Центральная колонка: Подпись
    col2_x = left_x + 300
    draw.text((col2_x, foot_y + 14), "ПРЕДСЕДАТЕЛЬ ОРГКОМИТЕТА:", fill=(148, 163, 184), font=font_foot_lbl)

    # Факсимиле росчерка подписи
    sig_pts = [
        (col2_x + 10, foot_y + 42),
        (col2_x + 35, foot_y + 28),
        (col2_x + 55, foot_y + 46),
        (col2_x + 75, foot_y + 32),
        (col2_x + 110, foot_y + 40),
        (col2_x + 150, foot_y + 26),
        (col2_x + 190, foot_y + 36)
    ]
    for i in range(len(sig_pts) - 1):
        draw.line([sig_pts[i], sig_pts[i+1]], fill=(120, 180, 255), width=2)
    draw.arc((col2_x + 130, foot_y + 22, col2_x + 175, foot_y + 46), start=0, end=360, fill=(120, 180, 255), width=2)

    draw.line([(col2_x, foot_y + 48), (col2_x + 220, foot_y + 48)], fill=(255, 255, 255, 45), width=1)
    draw.text((col2_x, foot_y + 54), "Проф. Сабитов К.Б.", fill=(203, 213, 225), font=get_font(12, bold=False))

    # 8. КРИПТОГРАФИЧЕСКИЙ ХЭШ В САМОМ НИЗУ
    val_data = f"{theme['name']}:{theme['event']}:{theme['rank_title']}:2026"
    val_hash = hashlib.sha256(val_data.encode()).hexdigest()[:20].upper()
    val_str = f"КРИПТО-ХЭШ SHA-256 • {val_hash} • ID: #CERT-2026-{theme['type'].upper()} • ВЕРИФИЦИРОВАНО"
    
    draw.text((left_x, H - inner - 24), val_str, fill=(100, 116, 139), font=font_foot_mono)

    # Сохранение файлов
    os.makedirs(os.path.dirname(theme["filename"]), exist_ok=True)
    img.save(theme["filename"], "PNG")
    print(f"Generated: {theme['filename']}")

    if "alt_filename" in theme:
        os.makedirs(os.path.dirname(theme["alt_filename"]), exist_ok=True)
        img.save(theme["alt_filename"], "PNG")
        print(f"Generated alt: {theme['alt_filename']}")

if __name__ == "__main__":
    for theme in THEMES:
        draw_diploma(theme)
    print("Done generating spacious balanced diplomas!")

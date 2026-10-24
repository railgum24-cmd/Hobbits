"""
Скрипт генерации официальной PowerPoint презентации (.pptx) для хакатона.
Тема: Лицейский Реестр Достижений & @Hobbits22_bot
Стиль: Dark Perspective (глубокий тёмный фон, акценты Emerald #00BD7D, Cyan #38BDF8, Gold #F59E0B).
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen ratio (13.333 x 7.5 inches)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Цветовая палитра
    C_BG = RGBColor(7, 10, 17)            # #070A11
    C_SURFACE = RGBColor(14, 20, 34)       # #0E1422
    C_SURFACE_CARD = RGBColor(18, 25, 42)  # #12192A
    C_PRIMARY = RGBColor(0, 189, 125)      # #00BD7D (Emerald)
    C_CYAN = RGBColor(56, 189, 248)        # #38BDF8
    C_GOLD = RGBColor(245, 158, 11)        # #F59E0B
    C_VIOLET = RGBColor(167, 139, 250)     # #A78BFA
    C_PINK = RGBColor(236, 72, 153)        # #EC4899
    C_TEXT = RGBColor(255, 255, 255)
    C_MUTED = RGBColor(148, 163, 184)
    C_DIM = RGBColor(100, 116, 139)

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background() # no line

        # Верхняя акцентная полоса прогресса
        top_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.06))
        top_line.fill.solid()
        top_line.fill.fore_color.rgb = C_PRIMARY
        top_line.line.fill.background()

        # Нижний футер с метаданными
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.7), Inches(0.35))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "МБОУ «Инженерный лицей» • Цифровой Реестр Достижений & @Hobbits22_bot • Хакатон 2026"
        p.font.size = Pt(9)
        p.font.name = "Arial"
        p.font.color.rgb = C_DIM

    def add_header(slide, tag_text, title_text, color=C_PRIMARY):
        # Тег
        tb_tag = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10), Inches(0.3))
        p_tag = tb_tag.text_frame.paragraphs[0]
        p_tag.text = tag_text
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.name = "Arial"
        p_tag.font.color.rgb = color

        # Заголовок
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.9))
        p_title = tb_title.text_frame.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(28)
        p_title.font.bold = True
        p_title.font.name = "Arial"
        p_title.font.color.rgb = C_TEXT

    # ==================== СЛАЙД 1: ТИТУЛЬНЫЙ ====================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Заголовок титула
    tb1 = s1.shapes.add_textbox(Inches(0.8), Inches(1.2), Inches(11.7), Inches(2.2))
    tf1 = tb1.text_frame
    p1 = tf1.paragraphs[0]
    p1.text = "ЦИФРОВОЙ РЕЕСТР ДОСТИЖЕНИЙ"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.name = "Arial"
    p1.font.color.rgb = C_TEXT

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "& TELEGRAM-ШЛЮЗ @Hobbits22_bot"
    p1_sub.font.size = Pt(36)
    p1_sub.font.bold = True
    p1_sub.font.name = "Arial"
    p1_sub.font.color.rgb = C_PRIMARY

    p1_desc = tf1.add_paragraph()
    p1_desc.text = "Единая экосистема олимпиадного движения лицея: сквозной рейтинг, официальные дипломы с SHA-256 и мобильный ассистент."
    p1_desc.font.size = Pt(14)
    p1_desc.font.name = "Arial"
    p1_desc.font.color.rgb = C_MUTED

    # 4 Метрические плашки
    metrics = [
        ("320+", "НАГРАД В БАЗЕ", "Подтверждено завучами", C_PRIMARY),
        ("100%", "СИНХРОНИЗАЦИЯ", "Сайт ⟷ Telegram-бот", C_CYAN),
        ("SHA-256", "КРИПТО-ХЭШ", "Защита от подделок", C_GOLD),
        ("5 МИН", "ВЕРИФИКАЦИЯ", "Вместо дней рутины", C_VIOLET),
    ]

    for i, (val, lbl, sub, col) in enumerate(metrics):
        x = Inches(0.8 + i * 2.95)
        y = Inches(3.8)
        w = Inches(2.8)
        h = Inches(2.2)

        card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = C_SURFACE_CARD
        card.line.color.rgb = col
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

        p = tf.paragraphs[0]
        p.text = val
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.name = "Arial"
        p.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = lbl
        p2.alignment = PP_ALIGN.CENTER
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.name = "Arial"
        p2.font.color.rgb = C_TEXT

        p3 = tf.add_paragraph()
        p3.text = sub
        p3.alignment = PP_ALIGN.CENTER
        p3.font.size = Pt(9)
        p3.font.name = "Arial"
        p3.font.color.rgb = C_MUTED

    # ==================== СЛАЙД 2: ПРОБЛЕМА ====================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "[ 02 // PROBLEM STATEMENT ]", "С ЧЕМ СТАЛКИВАЮТСЯ ШКОЛЫ БЕЗ ЕДИНОГО РЕЕСТРА?", C_PINK)

    problems = [
        ("📂 Хаос и потерянные сканы", 
         "Грамоты пересылаются в мессенджерах, теряются на флешках и в почтах. К 11 классу ученик не может восстановить историю побед для поступления.",
         C_PINK),
        ("📊 Рутина и перегрузка завучей", 
         "Методисты вручную сводят десятки Excel-таблиц, вручную высчитывают баллы по сложным критериям и тратят сотни часов на отчёты.",
         C_PINK),
        ("🔍 Непрозрачный рейтинг", 
         "Лицеисты не видят свои баллы в реальном времени. Распределение академических стипендий и путевок вызывает недоверие и споры.",
         C_PINK)
    ]

    for i, (title, text, col) in enumerate(problems):
        x = Inches(0.8 + i * 3.95)
        y = Inches(1.8)
        w = Inches(3.8)
        h = Inches(4.5)

        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = C_SURFACE_CARD
        card.line.color.rgb = col
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.name = "Arial"
        p.font.color.rgb = C_TEXT

        p2 = tf.add_paragraph()
        p2.text = "\n" + text
        p2.font.size = Pt(13)
        p2.font.name = "Arial"
        p2.font.color.rgb = C_MUTED

    # ==================== СЛАЙД 3: РЕШЕНИЕ ====================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "[ 03 // OUR SOLUTION ]", "СВЯЗАННАЯ ЭКОСИСТЕМА: WEB + TELEGRAM", C_PRIMARY)

    solutions = [
        ("🤖 Telegram-бот @Hobbits22_bot", 
         "Подача заявок за 30 секунд со смартфона: ученик прикрепляет фото диплома, выбирает олимпиаду и следит за статусом рассмотрения и своими баллами.",
         "Стек: Python aiogram, SQLite Live-Sync", C_PRIMARY),
        ("🌐 Кабинеты Ученика и Завуча", 
         "Административная панель для мгновенной модерации, фиксации приказов, публикации афиш и интерактивного просмотра сквозного рейтинга лицея.",
         "Стек: Dark Spatial UI, Context Modals, REST API", C_CYAN),
        ("📜 Дипломы с крипто-хэшем SHA-256", 
         "Автоматическая генерация официальных наградных листов высокого разрешения с защитой от подделок для приемных комиссий вузов и портфолио.",
         "Стек: HTML5 Canvas, Pillow, SHA-256 Protocol", C_GOLD)
    ]

    for i, (title, text, sub, col) in enumerate(solutions):
        x = Inches(0.8 + i * 3.95)
        y = Inches(1.8)
        w = Inches(3.8)
        h = Inches(4.5)

        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = C_SURFACE_CARD
        card.line.color.rgb = col
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.name = "Arial"
        p.font.color.rgb = C_TEXT

        p2 = tf.add_paragraph()
        p2.text = "\n" + text
        p2.font.size = Pt(13)
        p2.font.name = "Arial"
        p2.font.color.rgb = C_MUTED

        p3 = tf.add_paragraph()
        p3.text = "\n" + sub
        p3.font.size = Pt(10)
        p3.font.bold = True
        p3.font.name = "Arial"
        p3.font.color.rgb = col

    # ==================== СЛАЙД 4: АРХИТЕКТУРА И СИНХРОНИЗАЦИЯ ====================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "[ 04 // CROSS-DEVICE CLOUD & SYNC ]", "РЕАЛТАЙМ НА GITHUB PAGES И СМАРТФОНАХ", C_CYAN)

    # Левый блок
    card_l = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.8), Inches(4.5))
    card_l.fill.solid()
    card_l.fill.fore_color.rgb = C_SURFACE_CARD
    card_l.line.color.rgb = C_CYAN
    card_l.line.width = Pt(1.5)
    tf_l = card_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "🌐 Кросс-девайс Cloud Hub (GitHub Pages)"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = C_TEXT

    p_body = tf_l.add_paragraph()
    p_body.text = "\n• Работает на GitHub Pages без обязательного сервера!\n\n• Умный алгоритм Smart Merge предотвращает потерю данных при параллельных запросах\n\n• Ученик регистрируется со смартфона → аккаунт сразу виден на ноутбуке завуча\n\n• Подача диплома с любого устройства мгновенно пересчитывает общелицейский рейтинг\n\n• Статус в шапке: 🟢 ОНЛАЙН (GITHUB CLOUD)"
    p_body.font.size = Pt(12)
    p_body.font.color.rgb = C_MUTED

    # Правый блок
    card_r = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.5))
    card_r.fill.solid()
    card_r.fill.fore_color.rgb = C_SURFACE_CARD
    card_r.line.color.rgb = C_PRIMARY
    card_r.line.width = Pt(1.5)
    tf_r = card_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "🤖 Связка с Telegram-ботом & API"
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = C_TEXT

    p_body_r = tf_r.add_paragraph()
    p_body_r.text = "\n• Сквозная SQLite-архитектура с зеркалированием в единую базу данных\n\n• Поддержка CORS и ThreadingHTTPServer в едином процессе\n\n• Эндпоинты:\n  CLOUD  https://kvdb.io/.../lyceum_db • Реалтайм шлюз\n  GET    /api/db • Получение базы\n  POST   /api/achievements • Подача диплома\n  POLL   Каждые 2.5 сек • Бесшовное обновление"
    p_body_r.font.size = Pt(12)
    p_body_r.font.color.rgb = C_MUTED
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = C_TEXT

    p_body_r = tf_r.add_paragraph()
    p_body_r.text = "\n• Разграничение доступа по ролям (Ученик / Администратор)\n\n• Поддержка CORS и ThreadingHTTPServer в едином процессе\n\n• Эндпоинты:\n  GET  /api/users • Получение базы\n  POST /api/achievements • Подача диплома\n  POST /api/achievements/status • Верификация завучем\n  GET  /api/events • Афиша мероприятий"
    p_body_r.font.size = Pt(13)
    p_body_r.font.color.rgb = C_MUTED

    # ==================== СЛАЙД 5: ДИПЛОМЫ ====================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "[ 05 // CREDENTIALS & SECURITY ]", "ОФИЦИАЛЬНЫЕ ДИПЛОМЫ НОВОГО ПОКОЛЕНИЯ", C_GOLD)

    # 3 карточки с дипломами
    diplomas_info = [
        ("🥇 ПОБЕДИТЕЛЬ (GOLD)", "assets/diplomas/diploma_winner.png", "Изумрудно-золотая палитра для победителей финалов и ВсОШ. Номер приказа, подпись и лавровая медаль.", C_GOLD),
        ("🥈 ПРИЗЁР (SILVER)", "assets/diplomas/diploma_prize.png", "Платиново-циановый стиль для 2-3 мест региональных состязаний и инженерных хакатонов.", C_CYAN),
        ("🥉 УЧАСТНИК (BRONZE)", "assets/diplomas/diploma_participant.png", "Бронзово-фиолетовый сертификат успешного прохождения проектных смен и турниров лицея.", C_VIOLET)
    ]

    for i, (d_title, img_path, d_desc, d_col) in enumerate(diplomas_info):
        x = Inches(0.8 + i * 3.95)
        y = Inches(1.8)
        w = Inches(3.8)
        h = Inches(4.5)

        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = C_SURFACE_CARD
        card.line.color.rgb = d_col
        card.line.width = Pt(1.5)

        # Если картинка существует, вставляем
        if os.path.exists(img_path):
            try:
                s5.shapes.add_picture(img_path, x + Inches(0.2), y + Inches(0.6), Inches(3.4), Inches(2.2))
            except Exception:
                pass

        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = d_title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = d_col

        p2 = tf.add_paragraph()
        p2.text = "\n\n\n\n\n\n\n\n" + d_desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_MUTED

    # ==================== СЛАЙД 6: UX ДЕТАЛИ И АФИША ====================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "[ 06 // USER EXPERIENCE & EVENTS ]", "АФИША МЕРОПРИЯТИЙ & UX ИННОВАЦИИ", C_VIOLET)

    ux_items = [
        ("📅 Афиша для админов", 
         "Завуч может добавлять афиши хакатонов и олимпиад прямо из панели: дата, место, начисляемые баллы и прямая ссылка на регистрацию.", C_VIOLET),
        ("🌀 Арочный портал пасхалок", 
         "Интерактивная бегущая строка с юмором лицеистов («Кот Шрёдингера», «Дейкстра до столовой») и плавающими кнопками быстрого доступа.", C_PRIMARY),
        ("🎴 3D-наклон карточек (Tilt)", 
         "Мягкий пространственный перевес карточек под курсором и контекстные окна с приятным размытием заднего плана без потери читаемости.", C_CYAN)
    ]

    for i, (title, text, col) in enumerate(ux_items):
        x = Inches(0.8 + i * 3.95)
        y = Inches(1.8)
        w = Inches(3.8)
        h = Inches(4.5)

        card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = C_SURFACE_CARD
        card.line.color.rgb = col
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = C_TEXT

        p2 = tf.add_paragraph()
        p2.text = "\n" + text
        p2.font.size = Pt(13)
        p2.font.color.rgb = C_MUTED

    # ==================== СЛАЙД 7: ЭФФЕКТ И МЕТРИКИ ====================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "[ 07 // IMPACT & VALUE ]", "СОЦИАЛЬНЫЙ ЭФФЕКТ ДЛЯ ЛИЦЕЯ", C_PRIMARY)

    impacts = [
        ("0%", "ПОТЕРЬ ДОКУМЕНТОВ", "Все сканы и приказы надёжно сохранены в едином реестре навсегда.", C_PRIMARY),
        ("-40 ч", "ЭКОНОМИИ В СЕМЕСТР", "Автоматическое сведение отчётности для методистов и завучей.", C_CYAN),
        ("100%", "ПРОЗРАЧНОСТЬ", "Каждый балл в рейтинге подкреплен номером приказа и ссылкой на грамоту.", C_GOLD),
        ("+35%", "ВОВЛЕЧЁННОСТЬ", "Открытый рейтинг и геймификация мотивируют учеников участвовать чаще.", C_VIOLET)
    ]

    for i, (val, lbl, sub, col) in enumerate(impacts):
        x = Inches(0.8 + i * 2.95)
        y = Inches(1.8)
        w = Inches(2.8)
        h = Inches(4.5)

        card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = C_SURFACE_CARD
        card.line.color.rgb = col
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = val
        p.font.size = Pt(36)
        p.font.bold = True
        p.font.color.rgb = col

        p2 = tf.add_paragraph()
        p2.text = lbl
        p2.font.size = Pt(12)
        p2.font.bold = True
        p2.font.color.rgb = C_TEXT

        p3 = tf.add_paragraph()
        p3.text = "\n" + sub
        p3.font.size = Pt(11)
        p3.font.color.rgb = C_MUTED

    # ==================== СЛАЙД 8: ДОРОЖНАЯ КАРТА ====================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "[ 08 // ROADMAP & FUTURE ]", "ПЛАНЫ РАЗВИТИЯ ПРОЕКТА", C_CYAN)

    roadmap = [
        ("Этап 1: ИИ-рекомендации", 
         "Персональный подбор олимпиад и хакатонов под профиль ученика на основе прошлых побед и интересов.", C_PRIMARY),
        ("Этап 2: Интеграция с вузами", 
         "Прямой экспорт верифицированного портфолио с SHA-256 в приемные комиссии университетов (МФТИ, ВШЭ, КФУ).", C_CYAN),
        ("Этап 3: Мультишкольность", 
         "Масштабирование на все школы города и региона с единым межшкольным кубком академических талантов.", C_GOLD)
    ]

    for i, (title, text, col) in enumerate(roadmap):
        x = Inches(0.8 + i * 3.95)
        y = Inches(1.8)
        w = Inches(3.8)
        h = Inches(4.5)

        card = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
        card.fill.solid()
        card.fill.fore_color.rgb = C_SURFACE_CARD
        card.line.color.rgb = col
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = C_TEXT

        p2 = tf.add_paragraph()
        p2.text = "\n" + text
        p2.font.size = Pt(13)
        p2.font.color.rgb = C_MUTED

    # ==================== СЛАЙД 9: ФИНАЛ / ДЕМО ====================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)

    tb9 = s9.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(11.7), Inches(3.5))
    tf9 = tb9.text_frame
    p9 = tf9.paragraphs[0]
    p9.text = "ГОТОВЫ ОТВЕТИТЬ НА ВАШИ ВОПРОСЫ!"
    p9.alignment = PP_ALIGN.CENTER
    p9.font.size = Pt(36)
    p9.font.bold = True
    p9.font.name = "Arial"
    p9.font.color.rgb = C_TEXT

    p9_sub = tf9.add_paragraph()
    p9_sub.text = "ПЕРЕХОДИМ К ЖИВОМУ ДЕМО"
    p9_sub.alignment = PP_ALIGN.CENTER
    p9_sub.font.size = Pt(36)
    p9_sub.font.bold = True
    p9_sub.font.name = "Arial"
    p9_sub.font.color.rgb = C_PRIMARY

    p9_desc = tf9.add_paragraph()
    p9_desc.text = "\nЛицейский реестр достижений — прозрачное будущее академического признания уже сегодня.\n\nWeb: http://127.0.0.1:8000 • Telegram: @Hobbits22_bot"
    p9_desc.alignment = PP_ALIGN.CENTER
    p9_desc.font.size = Pt(15)
    p9_desc.font.name = "Arial"
    p9_desc.font.color.rgb = C_MUTED

    # Сохраняем PPTX
    out_path = "Лицейский_Реестр_Достижений_Презентация.pptx"
    prs.save(out_path)
    print(f"Presentation saved successfully to: {out_path}")

if __name__ == "__main__":
    create_deck()

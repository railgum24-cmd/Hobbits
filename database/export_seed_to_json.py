"""
Конвертер начальных данных из data/seed.js в database/lyceum_db.json
"""
import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_PATH = os.path.join(BASE_DIR, "data", "seed.js")
OUT_PATH = os.path.join(BASE_DIR, "database", "lyceum_db.json")

def convert():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Извлекаем JSON-структуру из JS файла
    # Убираем комментарии // ... и /* ... */
    no_comments = re.sub(r'//.*', '', content)
    no_comments = re.sub(r'/\*.*?\*/', '', no_comments, flags=re.DOTALL)
    
    # Находим const SEED = { ... }
    m = re.search(r'const\s+SEED\s*=\s*(\{.*\});', no_comments, re.DOTALL)
    if not m:
        raise ValueError("Could not find SEED object in seed.js")
    
    raw_obj = m.group(1).strip()
    
    # Заменяем ключи без кавычек на ключи в кавычках (id: -> "id":)
    raw_json = re.sub(r'([a-zA-Z0-9_]+)\s*:', r'"\1":', raw_obj)
    # Убираем trailing commas: , } или , ]
    raw_json = re.sub(r',\s*([\]\}])', r'\1', raw_json)

    data = json.loads(raw_json)
    
    # Гарантируем структуру
    if "users" not in data:
        data["users"] = []
    if "achievements" not in data:
        data["achievements"] = []
    
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Успешно экспортировано {len(data['users'])} пользователей и {len(data['achievements'])} достижений в {OUT_PATH}")

if __name__ == "__main__":
    convert()

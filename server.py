"""
Локальный сервер API и статических файлов для Портала достижений лицея.
Объединяет сайт и Telegram-бот в единую базу данных (database/lyceum_db.json и SQLite).

Запуск:
    python server.py
    (или через run_server.bat / run_all.bat)
"""

import os
import sys
import json
import time
import sqlite3
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import urllib.parse

# Кодировка UTF-8 для Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PORT = int(os.environ.get("PORT", 8000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_JSON_PATH = os.path.join(BASE_DIR, "database", "lyceum_db.json")
DB_SQLITE_PATH = os.path.join(BASE_DIR, "database", "lyceum.db")
SEED_PATH = os.path.join(BASE_DIR, "data", "seed.js")

# Блокировка для потокобезопасного доступа к базе
db_lock = threading.Lock()

def load_db():
    with db_lock:
        if os.path.exists(DB_JSON_PATH):
            try:
                with open(DB_JSON_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ERROR] Ошибка чтения lyceum_db.json: {e}")
        
        # Если файла нет, инициализируем из seed
        from database.export_seed_to_json import convert
        convert()
        with open(DB_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

def save_db(data):
    with db_lock:
        # 1. Сохраняем в JSON
        with open(DB_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 2. Синхронизируем с SQLite для полной согласованности
        sync_to_sqlite(data)

def sync_to_sqlite(data):
    try:
        conn = sqlite3.connect(DB_SQLITE_PATH)
        cur = conn.cursor()
        
        # Создаем таблицы если нет
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            login TEXT UNIQUE NOT NULL,
            password TEXT,
            name TEXT NOT NULL,
            class_name TEXT,
            role TEXT NOT NULL,
            is_new INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS achievements (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            type TEXT NOT NULL,
            level TEXT NOT NULL,
            result TEXT NOT NULL,
            points INTEGER NOT NULL,
            event_date TEXT NOT NULL,
            file_url TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            verified_by TEXT,
            verified_at TEXT,
            comment TEXT,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            level TEXT,
            date TEXT NOT NULL,
            place TEXT,
            points_award TEXT,
            badge_text TEXT,
            image_url TEXT,
            registration_link TEXT,
            description TEXT,
            created_at TEXT
        );
        """)

        # Обеспечиваем наличие колонок password и is_new в существующей базе
        try:
            cur.execute("ALTER TABLE users ADD COLUMN password TEXT")
        except Exception:
            pass
        try:
            cur.execute("ALTER TABLE users ADD COLUMN is_new INTEGER DEFAULT 0")
        except Exception:
            pass

        # Очищаем и перезаписываем для актуальности
        cur.execute("DELETE FROM users")
        for u in data.get("users", []):
            cur.execute(
                "INSERT OR REPLACE INTO users (id, login, password, name, class_name, role, is_new) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (u.get("id"), u.get("login"), u.get("password"), u.get("name"), u.get("class"), u.get("role", "student"), 1 if u.get("isNew") else 0)
            )

        cur.execute("DELETE FROM achievements")
        for a in data.get("achievements", []):
            cur.execute(
                """INSERT OR REPLACE INTO achievements 
                (id, user_id, title, category, type, level, result, points, event_date, file_url, status, verified_by, verified_at, comment, description) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    a.get("id"), a.get("userId"), a.get("title"), a.get("category"), a.get("type"),
                    a.get("level"), a.get("result"), a.get("points", 0), a.get("date"), a.get("fileUrl", ""),
                    a.get("status", "pending"), a.get("verifiedBy"), a.get("verifiedAt"), a.get("comment", ""), a.get("description", "")
                )
            )

        cur.execute("DELETE FROM events")
        for ev in data.get("events", []):
            cur.execute(
                """INSERT OR REPLACE INTO events
                (id, title, category, level, date, place, points_award, badge_text, image_url, registration_link, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    ev.get("id"), ev.get("title"), ev.get("category"), ev.get("level"), ev.get("date"),
                    ev.get("place", ""), ev.get("pointsAward", ""), ev.get("badgeText", ""),
                    ev.get("imageUrl", ""), ev.get("registrationLink", ""), ev.get("description", ""),
                    ev.get("createdAt", "")
                )
            )
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[SQLITE WARNING] Ошибка синхронизации SQLite: {e}")

class PortalHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(204)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # API: получить всю базу данных
        if path == "/api/db":
            db = load_db()
            body = json.dumps(db, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._set_cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # API: пользователи
        if path == "/api/users":
            db = load_db()
            body = json.dumps(db.get("users", []), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._set_cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return

        # API: достижения
        if path == "/api/achievements":
            db = load_db()
            body = json.dumps(db.get("achievements", []), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._set_cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return

        # API: афиши мероприятий
        if path == "/api/events":
            db = load_db()
            body = json.dumps(db.get("events", []), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._set_cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
            return

        # Стандартная отдача файлов сайта (index.html, rating.html, student.html и т.д.)
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        
        try:
            payload = json.loads(post_body)
        except Exception:
            payload = {}

        # API: Полная синхронизация базы с сайта
        if path in ("/api/sync", "/api/save"):
            if payload and "users" in payload and "achievements" in payload:
                save_db(payload)
                resp = json.dumps({"ok": True, "users_count": len(payload["users"]), "achievements_count": len(payload["achievements"])})
                self._send_json(200, resp)
                return

        # API: Создание нового пользователя с сайта
        if path == "/api/users":
            db = load_db()
            users = db.setdefault("users", [])
            
            # Проверка уникальности логина
            login = payload.get("login", "").strip()
            if any(u.get("login", "").lower() == login.lower() for u in users):
                self._send_json(400, json.dumps({"error": "Пользователь с таким логином уже зарегистрирован"}))
                return

            new_user = {
                "id": f"user-{len(users) + 1}",
                "name": payload.get("name", "").strip(),
                "class": payload.get("class", "").strip(),
                "role": "student",
                "login": login,
                "password": payload.get("password", "").strip(),
                "isNew": True
            }
            users.append(new_user)
            save_db(db)
            print(f"[ЕДИНАЯ БАЗА] Зарегистрирован новый ученик: {new_user['name']} ({new_user['class']}), логин: {login}")
            self._send_json(201, json.dumps(new_user, ensure_ascii=False))
            return

        # API: Подача нового достижения
        if path == "/api/achievements":
            db = load_db()
            achs = db.setdefault("achievements", [])
            new_ach = {
                "id": f"ach-{len(achs) + 1}",
                "userId": payload.get("userId"),
                "title": payload.get("title", "").strip(),
                "category": payload.get("category"),
                "type": payload.get("type", "olympiad"),
                "level": payload.get("level", "city"),
                "result": payload.get("result", "participant"),
                "points": int(payload.get("points", 0)),
                "date": payload.get("date", ""),
                "status": "pending",
                "fileUrl": payload.get("fileUrl", ""),
                "comment": "",
                "description": payload.get("description", "")
            }
            achs.append(new_ach)
            save_db(db)
            print(f"[ЕДИНАЯ БАЗА] Подано новое достижение: {new_ach['title']} ({new_ach['points']} б.)")
            self._send_json(201, json.dumps(new_ach, ensure_ascii=False))
            return

        # API: Добавление новой афиши мероприятия
        if path == "/api/events":
            db = load_db()
            events = db.setdefault("events", [])
            new_event = {
                "id": payload.get("id") or f"ev-{int(time.time())}",
                "title": payload.get("title", "").strip(),
                "category": payload.get("category", "informatics"),
                "level": payload.get("level", "Региональный"),
                "date": payload.get("date", "").strip(),
                "place": payload.get("place", "Лицей"),
                "pointsAward": payload.get("pointsAward", "+20 баллов"),
                "badgeText": payload.get("badgeText", "АФИША"),
                "imageUrl": payload.get("imageUrl", ""),
                "registrationLink": payload.get("registrationLink", ""),
                "description": payload.get("description", "").strip(),
                "createdAt": payload.get("createdAt") or time.strftime("%Y-%m-%d")
            }
            events.insert(0, new_event)
            save_db(db)
            print(f"[ЕДИНАЯ БАЗА] Добавлена новая афиша: {new_event['title']}")
            self._send_json(201, json.dumps(new_event, ensure_ascii=False))
            return

        # API: Сброс базы до сидов
        if path == "/api/reset":
            from database.export_seed_to_json import convert
            convert()
            db = load_db()
            self._send_json(200, json.dumps({"ok": True, "message": "База успешно сброшена до начального состояния"}))
            return

        self._send_json(404, json.dumps({"error": "Endpoint not found"}))

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # API: Удаление всех новых зарегистрированных аккаунтов (функция админ-панели)
        if path == "/api/users/new":
            db = load_db()
            initial_count = len(db.get("users", []))
            db["users"] = [u for u in db.get("users", []) if not u.get("isNew")]
            deleted_count = initial_count - len(db["users"])
            save_db(db)
            print(f"[ЕДИНАЯ БАЗА] Удалено новых зарегистрированных аккаунтов: {deleted_count}")
            self._send_json(200, json.dumps({"ok": True, "deleted": deleted_count}))
            return

        # API: Удаление афиши мероприятия
        if path == "/api/events" or path.startswith("/api/events/"):
            query = urllib.parse.parse_qs(parsed.query)
            event_id = query.get("id", [None])[0]
            if not event_id and path.startswith("/api/events/"):
                event_id = path.replace("/api/events/", "")

            if not event_id:
                content_len = int(self.headers.get("Content-Length", 0))
                if content_len > 0:
                    try:
                        p = json.loads(self.rfile.read(content_len).decode("utf-8"))
                        event_id = p.get("id")
                    except Exception:
                        pass

            db = load_db()
            events = db.setdefault("events", [])
            initial_count = len(events)
            db["events"] = [e for e in events if e.get("id") != event_id]
            save_db(db)
            deleted = initial_count > len(db["events"])
            print(f"[ЕДИНАЯ БАЗА] Удалена афиша id={event_id}, удалено: {deleted}")
            self._send_json(200, json.dumps({"ok": True, "deleted": deleted}))
            return

        self._send_json(404, json.dumps({"error": "Endpoint not found"}))

    def _send_json(self, status_code, json_str):
        body = json_str.encode("utf-8")
        self.send_response(status_code)
        self._set_cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def start_telegram_bot_thread():
    """Запуск Telegram-бота в фоновом потоке, если скрипт доступен"""
    try:
        from bot.telegram_bot import run_bot_polling
        bot_thread = threading.Thread(target=run_bot_polling, daemon=True, name="HobbitBotThread")
        bot_thread.start()
        print("[СИСТЕМА] Telegram-бот HobbitBot запущен в фоновом потоке единого сервера.")
    except Exception as e:
        print(f"[СИСТЕМА] Запуск бота в отдельном процессе: {e}")

def main():
    print("=" * 65)
    print("  ЕДИНЫЙ СЕРВЕР ПОРТАЛА ДОСТИЖЕНИЙ ЛИЦЕЯ И TELEGRAM-БОТА")
    print("=" * 65)
    
    # Инициализация базы
    db = load_db()
    print(f" Единая база данных загружена: {len(db.get('users', []))} пользователей, {len(db.get('achievements', []))} достижений.")
    print(f" Файл единой базы: {DB_JSON_PATH}")
    print(f" Файл SQLite:      {DB_SQLITE_PATH}")

    # Запуск Telegram-бота
    start_telegram_bot_thread()

    server = ThreadingHTTPServer(("0.0.0.0", PORT), PortalHandler)
    print(f"\n Веб-сервер и API запущены на http://localhost:{PORT}")
    print(f" Главная страница: http://localhost:{PORT}/index.html")
    print(f" Рейтинг:          http://localhost:{PORT}/rating.html")
    print(f" Личный кабинет:   http://localhost:{PORT}/student.html")
    print(f" Админ-панель:     http://localhost:{PORT}/admin.html")
    print("\nДля остановки нажмите Ctrl+C\n" + "-" * 65)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановка сервера...")
        server.server_close()

if __name__ == "__main__":
    main()

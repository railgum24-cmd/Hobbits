"""
Скрипт инициализации локальной SQLite базы данных лицея.
Создаёт таблицы и заполняет их начальными данными (сидами).
Запуск: python database/init_sqlite.py
"""

import sqlite3
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), "lyceum.db")

def hash_pass(p: str) -> str:
    return hashlib.sha256(p.encode("utf-8")).hexdigest()

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Таблицы
    cur.executescript("""
    CREATE TABLE users (
        id TEXT PRIMARY KEY,
        login TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        name TEXT NOT NULL,
        class_name TEXT,
        role TEXT NOT NULL,
        telegram_id INTEGER UNIQUE
    );

    CREATE TABLE achievements (
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
        description TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE VIEW v_leaderboard AS
    SELECT 
        u.id, u.name, u.class_name,
        COALESCE(SUM(a.points), 0) AS total_points,
        COUNT(a.id) AS approved_count
    FROM users u
    LEFT JOIN achievements a ON u.id = a.user_id AND a.status = 'approved'
    WHERE u.role = 'student'
    GROUP BY u.id, u.name, u.class_name
    ORDER BY total_points DESC;
    """)

    # Тестовые пользователи
    users = [
        ("admin-1", "admin", hash_pass("admin2026"), "Ильдар Маратович", None, "admin", None),
        ("user-1", "Rail", hash_pass("2026"), "Гумеров Раиль", "9Б", "student", 123456789),
        ("user-2", "Amir", hash_pass("2026"), "Якубов Амир", "9Б", "student", None),
        ("user-3", "Islam", hash_pass("2026"), "Фаррахов Ислам", "9Б", "student", None),
        ("user-4", "Samir", hash_pass("2026"), "Биктагиров Самир", "9Б", "student", None),
        ("user-5", "Radislav", hash_pass("2026"), "Авдошин Радислав", "9Б", "student", None),
        ("user-6", "Samat", hash_pass("2026"), "Яруллин Самат", "9Б", "student", None),
        ("user-7", "Aliya", hash_pass("2026"), "Хасанова Алия", "10А", "student", None),
        ("user-8", "Timur", hash_pass("2026"), "Загиров Тимур", "11Б", "student", None),
        ("user-9", "Kamila", hash_pass("2026"), "Валиуллина Камила", "9А", "student", None)
    ]
    cur.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", users)

    # Тестовые достижения
    achievements = [
        ("ach-1", "user-1", "Олимпиада по физике «Росатом»", "physics", "olympiad", "region", "winner", 50, "2026-02-14", "", "approved", "admin-1", "2026-02-20", "Диплом подтверждён", "Победитель регионального этапа"),
        ("ach-2", "user-2", "Городская олимпиада по математике", "math", "olympiad", "city", "prize", 25, "2026-01-20", "", "approved", "admin-1", "2026-01-25", "Призёр", "2 место"),
        ("ach-3", "user-3", "Хакатон «Digital Skills»", "informatics", "competition", "region", "winner", 40, "2026-03-10", "", "approved", "admin-1", "2026-03-15", "1 место", "Победитель хакатона"),
        ("ach-4", "user-7", "Конференция «Старт в науку»", "project", "conference", "city", "winner", 35, "2026-04-05", "", "approved", "admin-1", "2026-04-10", "1 степень", "Лучший доклад"),
        ("ach-5", "user-8", "ВсОШ по информатике (регион)", "informatics", "olympiad", "region", "prize", 35, "2026-01-30", "", "approved", "admin-1", "2026-02-05", "Призёр", "Протокол проверен"),
        ("ach-6", "user-4", "Школьная олимпиада по физике", "physics", "olympiad", "school", "winner", 20, "2025-11-15", "", "approved", "admin-1", "2025-11-18", "Подтверждено", "Школьный этап"),
        ("ach-7", "user-6", "Волонтёрская акция «Чистый берег»", "volunteering", "volunteering", "city", "participant", 10, "2026-05-20", "", "approved", "admin-1", "2026-05-22", "Благодарность", "Экология"),
        ("ach-8", "user-5", "Конкурс проектов «IT-решения»", "informatics", "project", "region", "prize", 30, "2026-09-25", "", "pending", None, None, "", "Умное расписание"),
        ("ach-9", "user-1", "Городская олимпиада по математике", "math", "olympiad", "city", "winner", 35, "2026-10-02", "", "pending", None, None, "", "1 место"),
        ("ach-13", "user-3", "Олимпиада «Ломоносов»", "math", "olympiad", "federal", "prize", 0, "2026-03-28", "", "rejected", "admin-1", "2026-04-02", "Не предоставлено подтверждение", "Нет скана")
    ]
    cur.executemany("INSERT INTO achievements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", achievements)

    conn.commit()
    conn.close()
    print(" База данных SQLite успешно инициализирована: database/lyceum.db")

if __name__ == "__main__":
    init_db()

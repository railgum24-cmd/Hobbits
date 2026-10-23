-- =====================================================================
-- Схема базы данных: Портал учёта достижений лицея
-- Диалект: PostgreSQL / совместимо с современными РСУБД
-- =====================================================================

-- 1. Таблица пользователей и ролей
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    login VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    class_name VARCHAR(10),                     -- Например: "9Б", "10А", NULL для администраторов
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'admin', 'teacher')),
    telegram_id BIGINT UNIQUE,                  -- Для привязки Telegram-бота и уведомлений
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для быстрого поиска по логину и Telegram ID
CREATE INDEX idx_users_login ON users(login);
CREATE INDEX idx_users_telegram ON users(telegram_id);
CREATE INDEX idx_users_class ON users(class_name);

-- 2. Справочник категорий достижений
CREATE TABLE categories (
    code VARCHAR(30) PRIMARY KEY,               -- physics, math, informatics, project, volunteering
    title VARCHAR(100) NOT NULL,
    icon VARCHAR(10),
    description TEXT
);

INSERT INTO categories (code, title, icon, description) VALUES
('physics', 'Физика', '⚛️', 'Олимпиады, турниры и исследования по физике'),
('math', 'Математика', '📐', 'Олимпиады, матбои и математические конкурсы'),
('informatics', 'Информатика', '💻', 'Хакатоны, программирование, алгоритмы и робототехника'),
('project', 'Проекты и конференции', '🚀', 'Научно-практические конференции и инженерные проекты'),
('volunteering', 'Волонтёрство', '🤝', 'Социальные и экологические лицейские инициативы');

-- 3. Справочник типов мероприятий и уровней
CREATE TABLE achievement_types (
    code VARCHAR(30) PRIMARY KEY,               -- olympiad, competition, conference, project, volunteering, exam
    title VARCHAR(100) NOT NULL
);

INSERT INTO achievement_types (code, title) VALUES
('olympiad', 'Олимпиада'),
('competition', 'Конкурс / Турнир'),
('conference', 'Научно-практическая конференция'),
('project', 'Проектная деятельность'),
('volunteering', 'Волонтёрство'),
('exam', 'Специализированный экзамен');

-- 4. Сетка баллов за результаты
CREATE TABLE points_matrix (
    id SERIAL PRIMARY KEY,
    type_code VARCHAR(30) REFERENCES achievement_types(code),
    level VARCHAR(20) CHECK (level IN ('school', 'city', 'region', 'federal')),
    result VARCHAR(20) CHECK (result IN ('winner', 'prize', 'participant')),
    points INT NOT NULL CHECK (points >= 0),
    UNIQUE (type_code, level, result)
);

-- 5. Основная таблица достижений
CREATE TABLE achievements (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    category_code VARCHAR(30) NOT NULL REFERENCES categories(code),
    type_code VARCHAR(30) NOT NULL REFERENCES achievement_types(code),
    level VARCHAR(20) NOT NULL CHECK (level IN ('school', 'city', 'region', 'federal')),
    result VARCHAR(20) NOT NULL CHECK (result IN ('winner', 'prize', 'participant')),
    points INT NOT NULL DEFAULT 0,
    event_date DATE NOT NULL,
    file_url TEXT,                              -- Ссылка на скан/диплом в облачном хранилище
    description TEXT,
    
    -- Статус верификации и аудит
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    verified_by VARCHAR(36) REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    rejection_comment TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для фильтрации рейтинга и личного кабинета
CREATE INDEX idx_achievements_user ON achievements(user_id);
CREATE INDEX idx_achievements_status ON achievements(status);
CREATE INDEX idx_achievements_category ON achievements(category_code);
CREATE INDEX idx_achievements_date ON achievements(event_date);

-- 6. Журнал аудита верификаций (защита от коллизий двух администраторов)
CREATE TABLE verification_audit_log (
    id SERIAL PRIMARY KEY,
    achievement_id VARCHAR(36) NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    admin_id VARCHAR(36) NOT NULL REFERENCES users(id),
    action VARCHAR(20) NOT NULL CHECK (action IN ('approved', 'rejected')),
    comment TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Представление: Рейтинг учеников (только подтверждённые баллы)
CREATE OR REPLACE VIEW v_student_leaderboard AS
SELECT 
    u.id AS user_id,
    u.full_name,
    u.class_name,
    COALESCE(SUM(a.points), 0) AS total_points,
    COUNT(a.id) AS approved_count,
    COALESCE(SUM(CASE WHEN a.category_code = 'physics' THEN a.points ELSE 0 END), 0) AS physics_points,
    COALESCE(SUM(CASE WHEN a.category_code = 'math' THEN a.points ELSE 0 END), 0) AS math_points,
    COALESCE(SUM(CASE WHEN a.category_code = 'informatics' THEN a.points ELSE 0 END), 0) AS informatics_points,
    DENSE_RANK() OVER (ORDER BY COALESCE(SUM(a.points), 0) DESC) AS rank
FROM users u
LEFT JOIN achievements a ON u.id = a.user_id AND a.status = 'approved'
WHERE u.role = 'student'
GROUP BY u.id, u.full_name, u.class_name;

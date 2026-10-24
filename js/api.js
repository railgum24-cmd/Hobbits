// =================================================================
// API-слой портала достижений лицея.
// Эмулирует бэкенд: при появлении реального сервера тела методов
// заменяются на fetch(), а сигнатуры остаются прежними — UI не меняется.
// =================================================================
const api = (() => {
  // ---------- Утилиты ----------

  // Хеш пароля (cyrb53): пароли не хранятся открытым текстом.
  // Для демо достаточно; на сервере используют bcrypt/argon2.
  const hash = (s) => {
    let h1 = 0xdeadbeef, h2 = 0x41c6ce57;
    for (let i = 0; i < s.length; i++) {
      const c = s.charCodeAt(i);
      h1 = Math.imul(h1 ^ c, 2654435761);
      h2 = Math.imul(h2 ^ c, 1597334677);
    }
    h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
    h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
    return (4294967296 * (2097151 & h2) + (h1 >>> 0)).toString(36);
  };

  // Публичная версия пользователя: без хеша пароля
  const pub = ({ passHash, password, ...u }) => u;

  // Генератор уникальных id: "a_lx3k9ab"
  const newId = (prefix) =>
    prefix + "_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 5);

  // Бросить ошибку с понятным сообщением
  const fail = (msg) => { throw new Error(msg); };

  // Проверка прав: только администратор
  const requireAdmin = (id) => {
    const u = db.users.find(x => x.id === id);
    if (!u || u.role !== "admin") fail("Нужны права администратора");
  };

  // Сегодняшняя дата в формате ISO (YYYY-MM-DD)
  const today = () => new Date().toISOString().slice(0, 10);

  // ---------- База данных ----------

  // Загрузка из хранилища или инициализация тестовыми данными
  let db = Storage.load();
  if (!db) {
    db = structuredClone(SEED);
    // Хешируем пароли при первой загрузке, сохраняя поле password для Telegram-бота
    db.users.forEach(u => { u.passHash = hash(u.password); });
  }

  // Фоновая синхронизация с единым сервером и Telegram-ботом
  Storage.syncWithServer((serverDb) => {
    if (serverDb && serverDb.users && serverDb.achievements) {
      db = serverDb;
      window.dispatchEvent(new CustomEvent('lyceum:db-synced', { detail: db }));
    }
  });

  // Слушаем событие обновления единой базы данных
  if (typeof window !== "undefined") {
    window.addEventListener('lyceum:db-synced', (e) => {
      if (e.detail && e.detail.users && e.detail.achievements) {
        db = e.detail;
      }
    });
  }

  // Сохранить изменения после каждой записи
  const commit = () => Storage.save(db);

  // ---------- Таблица баллов ----------
  // Баллы зависят от типа, уровня и результата: pointsTable[type][level][result]
  const getPoints = (type, level, result) => {
    const table = db.pointsTable || SEED.pointsTable;
    if (table[type] && table[type][level] && table[type][level][result] !== undefined) {
      return table[type][level][result];
    }
    // Значения по умолчанию, если комбинация не найдена
    return { winner: 30, prize: 20, participant: 10 }[result] || 5;
  };

  // =================================================================
  // ПУБЛИЧНЫЙ API
  // =================================================================
  return {
    // ---------- Пользователи ----------
    users: {
      // Все пользователи (без хешей паролей)
      list: () => db.users.map(pub),

      // Один пользователь по id
      get: (id) => {
        const u = db.users.find(x => x.id === id);
        return u ? pub(u) : null;
      },

      // Проверка, является ли пользователь базовым из сидов
      isSeed(u) {
        if (!u) return false;
        return SEED.users.some(s => s.id === u.id || (s.login && u.login && s.login.toLowerCase() === u.login.toLowerCase()));
      },

      // Регистрация нового ученика
      create(data) {
        if (!data.name || !data.login) fail("Заполните имя и логин");
        if (!data.password || data.password.length < 4) fail("Пароль: минимум 4 символа");
        if (!data.class) fail("Укажите класс");
        if (db.users.some(u => u.login.toLowerCase() === data.login.trim().toLowerCase())) fail("Такой логин уже существует");
        const u = {
          id: newId("u"),
          name: data.name.trim(),
          class: data.class.trim(),
          role: "student",
          login: data.login.trim(),
          password: data.password.trim(),
          passHash: hash(data.password),
          isNew: true,
          registeredAt: today()
        };
        db.users.push(u);
        commit();
        return pub(u);
      },

      // Список всех учеников (для рейтинга и админки)
      students: () => db.users.filter(u => u.role === "student").map(pub),

      // Список только новых зарегистрированных аккаунтов (для управления в админке)
      newUsers() {
        return db.users
          .filter(u => u.role !== "admin" && (u.isNew || !SEED.users.some(s => s.id === u.id || s.login.toLowerCase() === u.login.toLowerCase())))
          .map(u => ({
            ...pub(u),
            achievementsCount: db.achievements.filter(a => a.userId === u.id).length
          }));
      },

      // Удаление конкретного пользователя (только администратор)
      delete(id, adminId) {
        requireAdmin(adminId);
        const target = db.users.find(u => u.id === id) || fail("Пользователь не найден");
        if (target.role === "admin") fail("Нельзя удалить администратора");
        
        // Удаляем пользователя и все его достижения
        db.users = db.users.filter(u => u.id !== id);
        db.achievements = db.achievements.filter(a => a.userId !== id);
        commit();
        return true;
      },

      // Удаление ВСЕХ новых зарегистрированных аккаунтов (только администратор)
      deleteNewUsers(adminId) {
        requireAdmin(adminId);
        const seedLogins = new Set(SEED.users.map(s => s.login.toLowerCase()));
        const seedIds = new Set(SEED.users.map(s => s.id));

        // Идентифицируем аккаунты, созданные после сидов
        const toDelete = db.users.filter(u => u.role !== "admin" && (u.isNew || (!seedIds.has(u.id) && !seedLogins.has(u.login.toLowerCase()))));
        const toDeleteIds = new Set(toDelete.map(u => u.id));

        const usersCount = toDelete.length;
        const achievementsCount = db.achievements.filter(a => toDeleteIds.has(a.userId)).length;

        // Удаляем пользователей и связанные достижения
        db.users = db.users.filter(u => !toDeleteIds.has(u.id));
        db.achievements = db.achievements.filter(a => !toDeleteIds.has(a.userId));
        
        // Очищаем отдельное локальное хранилище
        Storage.clearRegisteredUsers();
        commit();

        return { deletedUsers: usersCount, deletedAchievements: achievementsCount };
      },

      // Экспорт локальной базы зарегистрированных аккаунтов в JSON
      exportRegisteredJSON(adminId) {
        requireAdmin(adminId);
        const newOnes = this.newUsers();
        Storage.exportJSON(newOnes, "registered_accounts_" + today() + ".json");
      }
    },

    // ---------- Авторизация ----------
    auth: {
      // Проверка логина и пароля
      check(login, password) {
        const trimmedLogin = (login || "").trim().toLowerCase();
        const u = db.users.find(x => 
          (x.login || "").toLowerCase() === trimmedLogin && 
          (x.passHash === hash(password) || String(x.password) === String(password))
        );
        if (!u) fail("Неверный логин или пароль");
        return pub(u);
      }
    },

    // ---------- Достижения (CRUD) ----------
    achievements: {
      // Все достижения с фильтрацией
      list: (filter = {}) => db.achievements.filter(a =>
        (!filter.userId || a.userId === filter.userId) &&
        (!filter.category || a.category === filter.category) &&
        (!filter.status || a.status === filter.status) &&
        (!filter.level || a.level === filter.level)
      ),

      // Одно достижение по id
      get: (id) => db.achievements.find(a => a.id === id) || null,

      // Ученик подаёт новое достижение на верификацию
      create(data) {
        const uid = data.userId || data.studentId;
        if (!data.title) fail("Введите название достижения");
        if (!data.category) fail("Выберите категорию");
        if (!data.type) fail("Выберите тип достижения");
        if (!data.result) fail("Выберите результат");
        if (!data.date) fail("Укажите дату");
        if (!uid) fail("Не указан пользователь");

        // Вычисляем баллы по таблице
        const points = getPoints(data.type, data.level || "school", data.result);

        const a = {
          id: newId("a"),
          userId: uid,
          title: data.title.trim(),
          category: data.category,
          type: data.type,
          level: data.level || "school",
          result: data.result,
          points: points,
          date: data.date,
          fileUrl: data.fileUrl || "",
          status: "pending",         // ждёт верификации
          verifiedBy: null,
          verifiedAt: null,
          comment: "",
          description: data.description || ""
        };
        db.achievements.push(a);
        commit();
        return a;
      },

      // Администратор подтверждает достижение
      approve(id, adminId, comment = "") {
        requireAdmin(adminId);
        const a = db.achievements.find(x => x.id === id) || fail("Достижение не найдено");
        if (a.status === "approved") fail("Уже подтверждено");
        a.status = "approved";
        a.verifiedBy = adminId;
        a.verifiedAt = today();
        a.comment = comment;
        commit();
        return a;
      },

      // Администратор отклоняет достижение
      reject(id, adminId, comment = "") {
        requireAdmin(adminId);
        if (!comment) fail("Укажите причину отклонения");
        const a = db.achievements.find(x => x.id === id) || fail("Достижение не найдено");
        if (a.status !== "pending") fail("Можно отклонить только ожидающее проверки");
        a.status = "rejected";
        a.verifiedBy = adminId;
        a.verifiedAt = today();
        a.comment = comment;
        commit();
        return a;
      },

      // Администратор добавляет достижение любому ученику (уже подтверждённое)
      createByAdmin(data, adminId) {
        requireAdmin(adminId);
        const uid = data.userId || data.studentId;
        if (!data.title) fail("Введите название достижения");
        if (!uid) fail("Выберите ученика");
        if (!data.category) fail("Выберите категорию");
        if (!data.type) fail("Выберите тип");
        if (!data.result) fail("Выберите результат");

        const points = getPoints(data.type, data.level || "school", data.result);

        const a = {
          id: newId("a"),
          userId: uid,
          title: data.title.trim(),
          category: data.category,
          type: data.type,
          level: data.level || "school",
          result: data.result,
          points: points,
          date: data.date || today(),
          fileUrl: data.fileUrl || "",
          status: "approved",
          verifiedBy: adminId,
          verifiedAt: today(),
          comment: data.comment || "Добавлено администратором",
          description: data.description || ""
        };
        db.achievements.push(a);
        commit();
        return a;
      },

      // Удаление достижения (только админ)
      delete(id, adminId) {
        requireAdmin(adminId);
        const idx = db.achievements.findIndex(a => a.id === id);
        if (idx === -1) fail("Достижение не найдено");
        db.achievements.splice(idx, 1);
        commit();
      }
    },

    // ---------- Рейтинг ----------
    rating: {
      // Подсчёт баллов ученика по категориям (только подтверждённые)
      userScore(userId) {
        const approved = db.achievements.filter(
          a => a.userId === userId && a.status === "approved"
        );
        const byCategory = {};
        let total = 0;
        for (const a of approved) {
          byCategory[a.category] = (byCategory[a.category] || 0) + a.points;
          total += a.points;
        }
        return { total, byCategory, count: approved.length };
      },

      // Общий рейтинг: массив учеников, отсортированный по убыванию баллов.
      // Фильтры: classFilter (строка), category (строка), period (объект {from, to})
      leaderboard(filters = {}) {
        const students = db.users.filter(u => u.role === "student");
        const board = students.map(u => {
          let approved = db.achievements.filter(
            a => a.userId === u.id && a.status === "approved"
          );

          // Фильтр по категории
          if (filters.category) {
            approved = approved.filter(a => a.category === filters.category);
          }
          // Фильтр по периоду
          if (filters.from) {
            approved = approved.filter(a => a.date >= filters.from);
          }
          if (filters.to) {
            approved = approved.filter(a => a.date <= filters.to);
          }

          const total = approved.reduce((s, a) => s + a.points, 0);
          const count = approved.length;
          return { userId: u.id, name: u.name, class: u.class, total, count };
        });

        // Фильтр по классу
        let result = board;
        if (filters.classFilter) {
          result = result.filter(r => r.class === filters.classFilter);
        }

        // Сортировка по убыванию баллов
        result.sort((a, b) => b.total - a.total);

        // Нумерация мест (одинаковые баллы → одинаковое место)
        let rank = 0, prevTotal = -1;
        for (let i = 0; i < result.length; i++) {
          if (result[i].total !== prevTotal) {
            rank = i + 1;
            prevTotal = result[i].total;
          }
          result[i].rank = rank;
        }

        return result;
      },

      // Топ-10
      top10(filters = {}) {
        return this.leaderboard(filters).slice(0, 10);
      },

      // Список уникальных классов (для фильтра)
      classes() {
        const set = new Set(db.users.filter(u => u.role === "student").map(u => u.class));
        return [...set].sort();
      }
    },

    // ---------- Портфолио ----------
    portfolio: {
      // Полная сводка ученика для портфолио / экспорта
      summary(userId) {
        const user = db.users.find(u => u.id === userId);
        if (!user) fail("Пользователь не найден");

        const all = db.achievements.filter(a => a.userId === userId);
        const approved = all.filter(a => a.status === "approved");
        const pending = all.filter(a => a.status === "pending");
        const rejected = all.filter(a => a.status === "rejected");

        // Сводка по категориям
        const categories = {};
        const CATS = ["physics", "math", "informatics", "project", "volunteering"];
        for (const cat of CATS) {
          const catAch = approved.filter(a => a.category === cat);
          categories[cat] = {
            count: catAch.length,
            points: catAch.reduce((s, a) => s + a.points, 0),
            items: catAch
          };
        }

        // Уровни достижений
        const levels = {};
        for (const lvl of ["school", "city", "region", "federal"]) {
          levels[lvl] = approved.filter(a => a.level === lvl).length;
        }

        const totalPoints = approved.reduce((s, a) => s + a.points, 0);

        return {
          user: pub(user),
          totalPoints,
          totalAchievements: approved.length,
          pending: pending.length,
          rejected: rejected.length,
          categories,
          levels,
          allAchievements: all
        };
      }
    },

    // ---------- Геймификация: уровни и значки ----------
    gamification: {
      userBadges(userId) {
        const approved = db.achievements.filter(a => a.userId === userId && a.status === "approved");
        const totalPoints = approved.reduce((s, a) => s + a.points, 0);

        // Уровень
        let level = { name: "Новичок", title: "1 уровень", nextPoints: 30, progress: totalPoints / 30 };
        if (totalPoints >= 100) {
          level = { name: "Легенда лицея", title: "4 уровень", nextPoints: 100, progress: 1 };
        } else if (totalPoints >= 60) {
          level = { name: "Мастер наук", title: "3 уровень", nextPoints: 100, progress: totalPoints / 100 };
        } else if (totalPoints >= 30) {
          level = { name: "Активист", title: "2 уровень", nextPoints: 60, progress: totalPoints / 60 };
        }

        // Значки
        const badges = [];
        const hasPhys = approved.some(a => a.category === "physics");
        const hasMath = approved.some(a => a.category === "math");
        const hasInf = approved.some(a => a.category === "informatics");
        const hasProj = approved.some(a => a.category === "project");
        const hasVol = approved.some(a => a.category === "volunteering");
        const winnersCount = approved.filter(a => a.result === "winner").length;

        if (hasPhys) badges.push({ id: "phys", icon: "⚛️", title: "Юный Ньютон", desc: "Достижение по физике" });
        if (hasMath) badges.push({ id: "math", icon: "📐", title: "Архимед", desc: "Достижение по математике" });
        if (hasInf) badges.push({ id: "inf", icon: "💻", title: "Кодер лицея", desc: "Успехи в информатике" });
        if (hasProj) badges.push({ id: "proj", icon: "🚀", title: "Инноватор", desc: "Успешный проект" });
        if (hasVol) badges.push({ id: "vol", icon: "🤝", title: "Доброе сердце", desc: "Волонтёрская активность" });
        if (winnersCount >= 2) badges.push({ id: "win", icon: "🏆", title: "Чемпион лицея", desc: "2+ победы в мероприятиях" });
        if (approved.length >= 3) badges.push({ id: "multi", icon: "🌟", title: "Многогранность", desc: "3+ подтверждённых достижения" });

        return { level, badges, totalPoints };
      }
    },

    // ---------- Академический аудит (расчёт стипендий и баланса дисциплин) ----------
    academic: {
      audit(userId) {
        const user = db.users.find(u => u.id === userId);
        if (!user) fail("Пользователь не найден");

        const approved = db.achievements.filter(a => a.userId === userId && a.status === "approved");
        const scores = { physics: 0, math: 0, informatics: 0, project: 0, volunteering: 0 };
        approved.forEach(a => { scores[a.category] = (scores[a.category] || 0) + a.points; });
        const total = approved.reduce((s, a) => s + a.points, 0);

        const targetScholarship = 60; // Порог для повышенной стипендии лицея
        const scholarshipReady = total >= targetScholarship;
        const ptsNeeded = Math.max(0, targetScholarship - total);

        return {
          studentName: user.name,
          currentPoints: total,
          targetScholarship,
          scholarshipReady,
          ptsNeeded,
          scores,
          calendar: [
            { date: "14 ноя", title: "Муниципальный этап ВсОШ по физике", cat: "Физика", pts: "до +35 б." },
            { date: "21 ноя", title: "Лицейский IT-хакатон по алгоритмам", cat: "Информатика", pts: "до +40 б." },
            { date: "02 дек", title: "Олимпиада «Росатом» по математике", cat: "Математика", pts: "до +50 б." }
          ]
        };
      }
    },

    // ---------- Отчёты ----------
    reports: {
      // Таблица для CSV-выгрузки
      rows() {
        const CATS = { physics: "Физика", math: "Математика", informatics: "Информатика",
                       project: "Проект", volunteering: "Волонтёрство" };
        const TYPES = { olympiad: "Олимпиада", competition: "Конкурс", conference: "Конференция",
                        project: "Проект", volunteering: "Волонтёрство", exam: "Экзамен" };
        const LEVELS = { school: "Школьный", city: "Городской", region: "Региональный",
                         federal: "Федеральный" };
        const RESULTS = { winner: "Победитель", prize: "Призёр", participant: "Участник" };
        const STATUSES = { pending: "На проверке", approved: "Подтверждено", rejected: "Отклонено" };

        const body = db.achievements.map(a => {
          const u = db.users.find(x => x.id === a.userId);
          return [
            u ? u.name : "?",
            u ? u.class : "?",
            a.title,
            CATS[a.category] || a.category,
            TYPES[a.type] || a.type,
            LEVELS[a.level] || a.level,
            RESULTS[a.result] || a.result,
            a.points,
            a.date,
            STATUSES[a.status] || a.status,
            a.verifiedAt || ""
          ];
        });
        return [
          ["Ученик", "Класс", "Достижение", "Категория", "Тип", "Уровень",
           "Результат", "Баллы", "Дата", "Статус", "Дата проверки"],
          ...body
        ];
      }
    },

    // ---------- Таблица баллов (публичная) ----------
    pointsTable: {
      get: () => db.pointsTable || SEED.pointsTable
    },

    // ---------- Афиши мероприятий и олимпиад ----------
    events: {
      // Список всех афиш
      list: () => [...(db.events || SEED.events || [])],

      // Получить одну афишу по id
      get: (id) => (db.events || SEED.events || []).find(e => e.id === id) || null,

      // Добавить новую афишу (только администратор)
      create(data, adminId) {
        requireAdmin(adminId);
        if (!data.title || !data.title.trim()) fail("Введите название мероприятия");
        if (!data.date || !data.date.trim()) fail("Укажите дату проведения");
        if (!db.events) db.events = [...(SEED.events || [])];

        const newEv = {
          id: "ev-" + Date.now().toString(36) + Math.random().toString(36).slice(2, 5),
          title: data.title.trim(),
          category: data.category || "informatics",
          level: data.level || "Региональный",
          date: data.date.trim(),
          place: (data.place || "Лицей").trim(),
          pointsAward: (data.pointsAward || "+20 баллов").trim(),
          badgeText: (data.badgeText || "ОЛИМПИАДА").trim(),
          imageUrl: (data.imageUrl || "").trim(),
          registrationLink: (data.registrationLink || "").trim(),
          description: (data.description || "").trim(),
          createdAt: today()
        };

        db.events.unshift(newEv);
        commit();

        // Фоновый запрос к серверу на добавление
        fetch("/api/events", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(newEv)
        }).catch(() => {
          fetch(Storage.SERVER_URL + "/api/events", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(newEv)
          }).catch(() => {});
        });

        return newEv;
      },

      // Удалить афишу по id (только администратор)
      delete(id, adminId) {
        requireAdmin(adminId);
        if (!db.events) db.events = [...(SEED.events || [])];
        const idx = db.events.findIndex(e => e.id === id);
        if (idx === -1) fail("Мероприятие не найдено");
        db.events.splice(idx, 1);
        commit();

        // Фоновый запрос к серверу на удаление
        fetch("/api/events?id=" + encodeURIComponent(id), { method: "DELETE" }).catch(() => {
          fetch(Storage.SERVER_URL + "/api/events?id=" + encodeURIComponent(id), { method: "DELETE" }).catch(() => {});
        });

        return true;
      }
    },

    // Принудительная синхронизация с единым сервером / ботом
    sync(onDone) {
      return Storage.forceSync((serverDb) => {
        if (serverDb) db = serverDb;
        if (typeof onDone === "function") onDone(db);
      });
    },

    // Сброс демо: удалить сохранённые данные и вернуть тестовые
    reset() {
      Storage.reset();
      location.reload();
    }
  };
})();

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
  const pub = ({ passHash, ...u }) => u;

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
    // Хешируем пароли при первой загрузке
    db.users.forEach(u => { u.passHash = hash(u.password); delete u.password; });
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

      // Регистрация нового ученика
      create(data) {
        if (!data.name || !data.login) fail("Заполните имя и логин");
        if (!data.password || data.password.length < 4) fail("Пароль: минимум 4 символа");
        if (!data.class) fail("Укажите класс");
        if (db.users.some(u => u.login === data.login)) fail("Такой логин уже существует");
        const u = {
          id: newId("u"),
          name: data.name.trim(),
          class: data.class.trim(),
          role: "student",
          login: data.login.trim(),
          passHash: hash(data.password)
        };
        db.users.push(u);
        commit();
        return pub(u);
      },

      // Список всех учеников (для рейтинга и админки)
      students: () => db.users.filter(u => u.role === "student").map(pub)
    },

    // ---------- Авторизация ----------
    auth: {
      // Проверка логина и пароля
      check(login, password) {
        const u = db.users.find(x => x.login === login && x.passHash === hash(password));
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

    // ---------- ИИ-помощник (рекомендательная система) ----------
    assistant: {
      recommend(userId) {
        const user = db.users.find(u => u.id === userId);
        if (!user) fail("Пользователь не найден");

        const approved = db.achievements.filter(a => a.userId === userId && a.status === "approved");
        const scores = { physics: 0, math: 0, informatics: 0, project: 0, volunteering: 0 };
        approved.forEach(a => { scores[a.category] = (scores[a.category] || 0) + a.points; });
        const total = approved.reduce((s, a) => s + a.points, 0);

        const tips = [];
        const targetScholarship = 60; // Порог для повышенной стипендии лицея

        if (total < targetScholarship) {
          tips.push(`До повышенной академической стипендии не хватает **${targetScholarship - total} баллов**.`);
        } else {
          tips.push(`🎉 Вы преодолели порог повышенной стипендии (${total} из ${targetScholarship} баллов)!`);
        }

        // Анализ профильных предметов
        const stemWeak = [];
        if (scores.physics === 0) stemWeak.push("физике");
        if (scores.math === 0) stemWeak.push("математике");
        if (scores.informatics === 0) stemWeak.push("информатике");

        if (stemWeak.length > 0) {
          tips.push(`Для инженерного/IT-профиля рекомендуем добавить достижения по **${stemWeak.join(", ")}**.`);
        } else {
          tips.push(`Отличный баланс: у вас закрыты все ключевые дисциплины (физика, математика, IT)!`);
        }

        // Конкретные советы мероприятий
        if (scores.informatics < 30) {
          tips.push(`💡 **Совет:** примите участие в ближайшем хакатоне или муниципальном этапе ВсОШ по информатике — это даст от 25 до 40 баллов.`);
        }
        if (scores.math < 30) {
          tips.push(`💡 **Совет:** открыта регистрация на олимпиаду по математике «Росатом» и турнир Ломоносова.`);
        }
        if (scores.volunteering === 0) {
          tips.push(`💡 **Бонус:** добавьте волонтёрские часы лицея — они учитываются при равенстве баллов в рейтинге.`);
        }

        return {
          studentName: user.name,
          currentPoints: total,
          scholarshipReady: total >= targetScholarship,
          tips
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

    // Сброс демо: удалить сохранённые данные и вернуть тестовые
    reset() {
      Storage.reset();
      location.reload();
    }
  };
})();

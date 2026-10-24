/**
 * Модуль Storage — гибридное хранилище портала достижений лицея.
 * Обеспечивает единую синхронизацию базы данных между веб-сайтом и Telegram-ботом.
 * 
 * - При наличии локального сервера (http://localhost:8000) синхронизирует данные в реальном времени каждые 2.5 секунды.
 * - При автономной работе без сервера работает через localStorage как надёжный кэш.
 */
const Storage = {
  KEY: "lyceum_achievements_db_v1",
  KEY_REGISTERED: "lyceum_registered_accounts_v1",
  SERVER_URL: "http://localhost:8000",
  isOnline: false,
  _lastHash: null,
  _syncing: false,

  /**
   * Загрузить базу из localStorage.
   * @returns {Object|null}
   */
  load() {
    const raw = localStorage.getItem(this.KEY);
    return raw ? JSON.parse(raw) : null;
  },

  /**
   * Сохранить базу локально и отправить на единый сервер для Telegram-бота.
   * @param {Object} db
   */
  save(db) {
    if (!db) return;
    const jsonStr = JSON.stringify(db);
    localStorage.setItem(this.KEY, jsonStr);
    this._lastHash = this._quickHash(jsonStr);

    if (db.users) {
      const registered = db.users.filter(u => u.isNew);
      localStorage.setItem(this.KEY_REGISTERED, JSON.stringify(registered));
    }

    // Фоновая синхронизация с единым сервером для бота
    this._pushToServer(db);
  },

  /**
   * Простой хэш для сравнения версий БД
   */
  _quickHash(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = (Math.imul(31, hash) + str.charCodeAt(i)) | 0;
    }
    return hash + "_" + str.length;
  },

  /**
   * Отправка обновленной базы на сервер (без блокировки UI)
   */
  _pushToServer(db) {
    const payload = JSON.stringify(db);
    
    // Пробуем относительный путь (если сайт открыт через сервер)
    fetch("/api/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload
    }).then(res => {
      if (res.ok) this._setOnline(true);
    }).catch(() => {
      // Если сайт открыт локально через file:///, шлём напрямую на localhost:8000
      fetch(this.SERVER_URL + "/api/sync", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: payload
      }).then(res => {
        if (res.ok) this._setOnline(true);
      }).catch(() => {
        this._setOnline(false);
      });
    });
  },

  _setOnline(status) {
    if (this.isOnline !== status) {
      this.isOnline = status;
      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent('lyceum:server-status', { detail: { online: status } }));
      }
    }
  },

  /**
   * Синхронизация с сервером (подтягивает заявки из Telegram-бота, афиши и новые аккаунты)
   * @param {Function} [onUpdate] - коллбэк вызывается при получении свежих данных
   */
  syncWithServer(onUpdate) {
    if (this._syncing) return Promise.resolve(false);
    this._syncing = true;

    const parseServerDb = (serverDb) => {
      if (serverDb && serverDb.users && serverDb.achievements) {
        this._setOnline(true);
        const jsonStr = JSON.stringify(serverDb);
        const currentHash = this._quickHash(jsonStr);
        
        const hasChanged = this._lastHash !== currentHash;
        this._lastHash = currentHash;

        localStorage.setItem(this.KEY, jsonStr);

        if (typeof window !== "undefined") {
          window.dispatchEvent(new CustomEvent('lyceum:db-synced', { detail: serverDb, changed: hasChanged }));
        }

        if (typeof onUpdate === "function") {
          onUpdate(serverDb, hasChanged);
        }
        return true;
      }
      return false;
    };

    const tryFetch = (url) => {
      return fetch(url, { cache: "no-store", headers: { "Accept": "application/json" } })
        .then(res => res.ok ? res.json() : Promise.reject(new Error("HTTP " + res.status)));
    };

    return tryFetch("/api/db")
      .then(parseServerDb)
      .catch(() => {
        return tryFetch(this.SERVER_URL + "/api/db")
          .then(parseServerDb)
          .catch(() => {
            this._setOnline(false);
            return false;
          });
      })
      .finally(() => {
        this._syncing = false;
      });
  },

  /**
   * Принудительная немедленная синхронизация
   */
  forceSync(onUpdate) {
    this._syncing = false;
    return this.syncWithServer(onUpdate);
  },

  /**
   * Получить локальную базу зарегистрированных пользователей.
   * @returns {Array}
   */
  loadRegisteredUsers() {
    const raw = localStorage.getItem(this.KEY_REGISTERED);
    return raw ? JSON.parse(raw) : [];
  },

  /**
   * Очистить локальную базу зарегистрированных пользователей.
   */
  clearRegisteredUsers() {
    localStorage.removeItem(this.KEY_REGISTERED);
    fetch("/api/users/new", { method: "DELETE" }).catch(() => {
      fetch(this.SERVER_URL + "/api/users/new", { method: "DELETE" }).catch(() => {});
    });
  },

  /**
   * Скачать локальную базу пользователей в виде JSON файла.
   */
  exportJSON(data, filename = "registered_users.json") {
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  },

  /**
   * Сброс базы
   */
  reset() {
    localStorage.removeItem(this.KEY);
    localStorage.removeItem(this.KEY_REGISTERED);
    fetch("/api/reset", { method: "POST" }).catch(() => {
      fetch(this.SERVER_URL + "/api/reset", { method: "POST" }).catch(() => {});
    });
  }
};

// Автоматический периодический опрос единого сервера каждые 2.5 сек
if (typeof window !== "undefined") {
  // Первичный опрос
  Storage.syncWithServer();

  // Интервальный опрос для мгновенного появления заявок из Telegram
  setInterval(() => {
    Storage.syncWithServer();
  }, 2500);

  // Опрос при возвращении фокуса во вкладку
  window.addEventListener("focus", () => {
    Storage.syncWithServer();
  });
}

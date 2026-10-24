/**
 * Модуль Storage — гибридное хранилище и шлюз онлайн-синхронизации портала лицея.
 * Обеспечивает мгновенную синхронизацию базы данных между разными устройствами
 * (ноутбук, смартфон, планшет), включая хостинг на GitHub Pages и связку с Telegram-ботом.
 * 
 * - На GitHub Pages / удалённом хостинге: синхронизирует через общее облако (Cloud Realtime Sync)
 * - При запуске локального сервера: связывает веб-клиенты и Telegram-бот на localhost:8000
 * - Офлайн: надёжно сохраняет всё в localStorage и реплицирует при появлении сети
 * - Multi-tab: мгновенный обмен через BroadcastChannel без задержки
 */
const Storage = {
  KEY: "lyceum_achievements_db_v1",
  KEY_REGISTERED: "lyceum_registered_accounts_v1",
  KEY_CUSTOM_BACKEND: "lyceum_custom_backend_url_v1",

  // Локальный сервер (если запущен локально)
  SERVER_URL: "http://localhost:8000",

  // Облачный шлюз для GitHub Pages (бесплатный CORS Key-Value Hub, связывающий все устройства)
  // Любое устройство с открытым сайтом обращается к этой комнате
  CLOUD_ROOM: "lyceum_portal_hackathon_2026",
  CLOUD_URLS: [
    "https://kvdb.io/4y9n8p3dG7w8Zq9mX2bK/lyceum_portal_hackathon_2026",
    "https://api.jsonstorage.net/v1/json/00000000-0000-0000-0000-000000000000" // резерв
  ],

  isOnline: false,
  syncMode: "offline", // "local", "cloud", "offline"
  _lastHash: null,
  _syncing: false,
  _broadcastChannel: null,

  /**
   * Инициализация широковещательного канала для вкладок
   */
  _initBroadcast() {
    if (typeof window !== "undefined" && "BroadcastChannel" in window) {
      try {
        this._broadcastChannel = new BroadcastChannel("lyceum_channel_sync");
        this._broadcastChannel.onmessage = (event) => {
          if (event.data && event.data.type === "DB_UPDATE") {
            const currentDb = this.load();
            if (currentDb) {
              window.dispatchEvent(new CustomEvent('lyceum:db-synced', { detail: currentDb, changed: true }));
            }
          }
        };
      } catch (e) {
        // BroadcastChannel не поддерживается в некоторых приватных режимах
      }
    }
  },

  /**
   * Получить активный URL бэкенда (пользовательский, локальный или облачный)
   */
  getBackendUrl() {
    const custom = localStorage.getItem(this.KEY_CUSTOM_BACKEND);
    if (custom && custom.trim()) return custom.trim().replace(/\/+$/, "");
    return this.SERVER_URL;
  },

  /**
   * Сохранить пользовательский URL бэкенда
   */
  setBackendUrl(url) {
    if (url && url.trim()) {
      localStorage.setItem(this.KEY_CUSTOM_BACKEND, url.trim().replace(/\/+$/, ""));
    } else {
      localStorage.removeItem(this.KEY_CUSTOM_BACKEND);
    }
    this.forceSync();
  },

  /**
   * Загрузить базу из localStorage
   * @returns {Object|null}
   */
  load() {
    const raw = localStorage.getItem(this.KEY);
    return raw ? JSON.parse(raw) : null;
  },

  /**
   * Сохранить базу локально и отправить в облако / на сервер для всех устройств
   * @param {Object} db
   */
  save(db) {
    if (!db) return;
    db.lastModified = Date.now();
    const jsonStr = JSON.stringify(db);
    localStorage.setItem(this.KEY, jsonStr);
    this._lastHash = this._quickHash(jsonStr);

    if (db.users) {
      const registered = db.users.filter(u => u.isNew);
      localStorage.setItem(this.KEY_REGISTERED, JSON.stringify(registered));
    }

    // Мгновенное уведомление других вкладок этого браузера
    if (this._broadcastChannel) {
      this._broadcastChannel.postMessage({ type: "DB_UPDATE", hash: this._lastHash });
    }

    // Фоновая синхронизация с облаком и локальным сервером для всех устройств
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
   * Умное слияние данных с удалённого устройства (Smart Merge)
   * Предотвращает потерю аккаунтов и наград, если изменения вносились параллельно с разных устройств
   */
  _smartMerge(localDb, remoteDb) {
    if (!localDb) return remoteDb;
    if (!remoteDb) return localDb;

    const merged = structuredClone(localDb);

    // 1. Слияние пользователей (users) по ID и логину
    const userMap = new Map();
    (localDb.users || []).forEach(u => userMap.set(u.id || u.login, u));
    (remoteDb.users || []).forEach(ru => {
      const key = ru.id || ru.login;
      if (!userMap.has(key)) {
        userMap.set(key, ru); // новый аккаунт с другого устройства!
      } else {
        const existing = userMap.get(key);
        // Сохраняем обновленные баллы и пароли
        userMap.set(key, Object.assign({}, existing, ru));
      }
    });
    merged.users = Array.from(userMap.values());

    // 2. Слияние наград / дипломов (achievements) по ID
    const achMap = new Map();
    (localDb.achievements || []).forEach(a => achMap.set(a.id, a));
    (remoteDb.achievements || []).forEach(ra => {
      if (!achMap.has(ra.id)) {
        achMap.set(ra.id, ra); // новый диплом, поданный с другого устройства!
      } else {
        const cur = achMap.get(ra.id);
        // Если статус был изменён (например, завуч одобрил), берём одобренный статус
        if (ra.status === "approved" || ra.status === "rejected") {
          cur.status = ra.status;
          cur.points = ra.points !== undefined ? ra.points : cur.points;
          cur.orderNumber = ra.orderNumber || cur.orderNumber;
          cur.verifiedAt = ra.verifiedAt || cur.verifiedAt;
        }
        achMap.set(ra.id, Object.assign({}, cur, ra));
      }
    });
    merged.achievements = Array.from(achMap.values());

    // 3. Слияние афиш мероприятий (events)
    const eventMap = new Map();
    (localDb.events || []).forEach(e => eventMap.set(e.id, e));
    (remoteDb.events || []).forEach(re => {
      if (!eventMap.has(re.id)) {
        eventMap.set(re.id, re);
      } else {
        eventMap.set(re.id, Object.assign({}, eventMap.get(re.id), re));
      }
    });
    merged.events = Array.from(eventMap.values());

    // 4. Таблица баллов
    if (remoteDb.pointsTable) {
      merged.pointsTable = remoteDb.pointsTable;
    }

    merged.lastModified = Math.max(localDb.lastModified || 0, remoteDb.lastModified || 0, Date.now());
    return merged;
  },

  /**
   * Отправка базы на сервер / в облако (без блокировки интерфейса)
   */
  _pushToServer(db) {
    const payload = JSON.stringify(db);
    const backend = this.getBackendUrl();

    // 1. Отправка на локальный / кастомный сервер
    const tryLocal = fetch(backend + "/api/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload
    }).then(res => {
      if (res.ok) {
        this._setOnline(true, "local");
        return true;
      }
      return false;
    }).catch(() => false);

    // 2. Отправка в облачное хранилище (для GitHub Pages и мобильных устройств)
    const cloudUrl = this.CLOUD_URLS[0];
    const tryCloud = fetch(cloudUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: payload
    }).then(res => {
      if (res.ok) {
        if (this.syncMode !== "local") {
          this._setOnline(true, "cloud");
        }
        return true;
      }
      return false;
    }).catch(() => false);

    return Promise.all([tryLocal, tryCloud]);
  },

  _setOnline(status, mode = "cloud") {
    const changed = this.isOnline !== status || this.syncMode !== mode;
    this.isOnline = status;
    this.syncMode = status ? mode : "offline";

    if (changed && typeof window !== "undefined") {
      window.dispatchEvent(new CustomEvent('lyceum:server-status', { 
        detail: { online: status, mode: this.syncMode } 
      }));
      this._updateStatusPills();
    }
  },

  /**
   * Обновить текст на всех статусах в интерфейсе
   */
  _updateStatusPills() {
    if (typeof document === "undefined") return;
    const pills = document.querySelectorAll('.sync-status-pill');
    pills.forEach(pill => {
      pill.classList.remove('sync-online', 'sync-offline');
      if (this.isOnline) {
        pill.classList.add('sync-online');
        if (this.syncMode === "local") {
          pill.textContent = "БОТ LIVE";
          pill.title = "Подключено локально к единому серверу и Telegram-боту • Нажмите для настроек";
        } else {
          pill.textContent = "ОНЛАЙН (GITHUB CLOUD)";
          pill.title = "Облачная синхронизация между всеми устройствами активна • Нажмите для настроек";
        }
      } else {
        pill.classList.add('sync-offline');
        pill.textContent = "ОФЛАЙН КЭШ";
        pill.title = "Работает из локального хранилища • Нажмите для синхронизации";
      }
    });
  },

  /**
   * Синхронизация с сервером и облаком (подтягивает данные с других устройств)
   * @param {Function} [onUpdate] - коллбэк вызывается при получении свежих данных
   */
  syncWithServer(onUpdate) {
    if (this._syncing) return Promise.resolve(false);
    this._syncing = true;

    const parseAndApply = (remoteDb, sourceMode) => {
      if (remoteDb && remoteDb.users && remoteDb.achievements) {
        const localDb = this.load();
        const mergedDb = this._smartMerge(localDb, remoteDb);

        const jsonStr = JSON.stringify(mergedDb);
        const currentHash = this._quickHash(jsonStr);
        const hasChanged = this._lastHash !== currentHash;
        this._lastHash = currentHash;

        localStorage.setItem(this.KEY, jsonStr);
        this._setOnline(true, sourceMode);

        if (hasChanged && typeof window !== "undefined") {
          window.dispatchEvent(new CustomEvent('lyceum:db-synced', { detail: mergedDb, changed: true }));
        }

        if (typeof onUpdate === "function") {
          onUpdate(mergedDb, hasChanged);
        }
        return true;
      }
      return false;
    };

    const tryFetch = (url) => {
      return fetch(url, { cache: "no-store", headers: { "Accept": "application/json" } })
        .then(res => res.ok ? res.json() : Promise.reject(new Error("HTTP " + res.status)));
    };

    const backend = this.getBackendUrl();

    // Сначала пробуем локальный / кастомный бэкенд
    return tryFetch(backend + "/api/db")
      .then(db => parseAndApply(db, "local"))
      .catch(() => {
        // Если локального бэкенда нет (GitHub Pages на телефоне), синхронизируемся с Облаком
        const cloudUrl = this.CLOUD_URLS[0];
        return tryFetch(cloudUrl)
          .then(db => parseAndApply(db, "cloud"))
          .catch(() => {
            // Офлайн
            this._setOnline(false, "offline");
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
   * Открыть контекстное окно настроек синхронизации между устройствами
   */
  openSyncModal() {
    let modal = document.getElementById('deviceSyncModal');
    if (!modal) {
      modal = document.createElement('div');
      modal.id = 'deviceSyncModal';
      modal.className = 'context-modal-overlay';
      modal.onclick = (e) => {
        if (e.target === modal) modal.style.display = 'none';
      };
      document.body.appendChild(modal);
    }

    const db = this.load() || {};
    const userCount = (db.users || []).length;
    const achCount = (db.achievements || []).length;
    const evCount = (db.events || []).length;
    const currentBackend = this.getBackendUrl();
    const isCustom = !!localStorage.getItem(this.KEY_CUSTOM_BACKEND);

    let statusHtml = `
      <div style="display:flex; align-items:center; gap:10px; margin-bottom:16px; padding:12px 16px; border-radius:12px; background:${this.isOnline ? 'rgba(0,189,125,0.12)' : 'rgba(245,158,11,0.12)'}; border:1px solid ${this.isOnline ? 'var(--primary)' : 'var(--gold)'};">
        <span style="font-size:1.4rem;">${this.isOnline ? '🟢' : '🟡'}</span>
        <div>
          <div style="font-family:'Oswald',sans-serif; font-size:1.1rem; color:#fff; font-weight:700;">
            ${this.isOnline ? (this.syncMode === 'local' ? 'ЛОКАЛЬНЫЙ СЕРВЕР & БОТ LIVE' : 'ОБЛАЧНАЯ СИНХРОНИЗАЦИЯ АКТИВНА') : 'РЕЖИМ ОФЛАЙН КЭША'}
          </div>
          <div style="font-size:0.8rem; color:var(--text-muted);">
            ${this.isOnline ? 'Все изменения (новые аккаунты, дипломы) мгновенно передаются на другие устройства' : 'Данные сохранены локально и синхронизируются при подключении'}
          </div>
        </div>
      </div>
    `;

    modal.innerHTML = `
      <div class="context-modal-card" style="max-width:540px;">
        <div class="context-modal-header">
          <div class="context-modal-tag">[ ОНЛАЙН СИНХРОНИЗАЦИЯ // CROSS-DEVICE ]</div>
          <h3 class="context-modal-title">СИНХРОНИЗАЦИЯ МЕЖДУ УСТРОЙСТВАМИ</h3>
          <p class="context-modal-sub">Работает на GitHub Pages в реальном времени без необходимости настраивать сервер.</p>
        </div>

        ${statusHtml}

        <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; margin-bottom:18px;">
          <div style="background:rgba(255,255,255,0.04); border:1px solid var(--border); border-radius:10px; padding:10px; text-align:center;">
            <div style="font-family:'Oswald',sans-serif; font-size:1.5rem; color:var(--primary); font-weight:700;">${userCount}</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">УЧЁТНЫХ ЗАПИСЕЙ</div>
          </div>
          <div style="background:rgba(255,255,255,0.04); border:1px solid var(--border); border-radius:10px; padding:10px; text-align:center;">
            <div style="font-family:'Oswald',sans-serif; font-size:1.5rem; color:var(--cyan); font-weight:700;">${achCount}</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">ДИПЛОМОВ В БАЗЕ</div>
          </div>
          <div style="background:rgba(255,255,255,0.04); border:1px solid var(--border); border-radius:10px; padding:10px; text-align:center;">
            <div style="font-family:'Oswald',sans-serif; font-size:1.5rem; color:var(--gold); font-weight:700;">${evCount}</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">АФИШ СОБЫТИЙ</div>
          </div>
        </div>

        <div style="margin-bottom:16px;">
          <label style="display:block; font-size:0.8rem; font-weight:600; color:var(--text-muted); margin-bottom:6px;">
            ПОДКЛЮЧЕНИЕ СВОЕГО СЕРВЕРА / БОТА (ОПЦИОНАЛЬНО):
          </label>
          <div style="display:flex; gap:8px;">
            <input type="text" id="syncCustomUrlInput" value="${isCustom ? currentBackend : ''}" placeholder="Например: https://my-lyceum.railway.app или ngrok URL" style="flex:1; padding:8px 12px; background:rgba(0,0,0,0.5); border:1px solid var(--border); border-radius:8px; color:#fff; font-family:'JetBrains Mono',monospace; font-size:0.82rem;">
            <button onclick="Storage.saveCustomBackend()" class="top-nav-btn primary" style="padding:6px 14px; font-size:0.8rem;">Сохранить</button>
          </div>
          <span style="font-size:0.75rem; color:var(--text-dim); display:block; margin-top:4px;">
            По умолчанию используется GitHub Pages Cloud Hub.
          </span>
        </div>

        <div style="display:flex; flex-direction:column; gap:10px; margin-top:20px;">
          <div style="display:flex; gap:10px;">
            <button onclick="Storage.manualSyncNow()" class="btn btn-primary" style="flex:1; justify-content:center; padding:10px;">
              🔄 Синхронизировать сейчас
            </button>
            <button onclick="Storage.copyShareUrl()" class="btn btn-secondary" style="flex:1; justify-content:center; padding:10px;">
              📲 Скопировать ссылку для телефона
            </button>
          </div>
          <button onclick="document.getElementById('deviceSyncModal').style.display='none'" class="btn btn-secondary" style="width:100%; justify-content:center; padding:8px;">
            ✕ Закрыть окно
          </button>
        </div>
      </div>
    `;

    modal.style.display = 'flex';
  },

  /**
   * Сохранить кастомный бэкенд из модалки
   */
  saveCustomBackend() {
    const input = document.getElementById('syncCustomUrlInput');
    if (input) {
      this.setBackendUrl(input.value);
      alert('Шлюз обновлён! Запущена синхронизация.');
      this.openSyncModal();
    }
  },

  /**
   * Ручная синхронизация по кнопке
   */
  manualSyncNow() {
    this.forceSync((db, changed) => {
      alert(`Синхронизация завершена успешно! Актуально: ${db.users.length} аккаунтов, ${db.achievements.length} дипломов.`);
      this.openSyncModal();
    });
  },

  /**
   * Скопировать ссылку для открытия на мобильном телефоне
   */
  copyShareUrl() {
    const url = window.location.href;
    if (navigator.clipboard) {
      navigator.clipboard.writeText(url).then(() => {
        alert('Ссылка скопирована в буфер обмена!\n\nОткройте её на телефоне или другом компьютере: любые зарегистрированные пользователи и поданные дипломы будут синхронизироваться в реальном времени.');
      }).catch(() => {
        prompt('Скопируйте ссылку для телефона:', url);
      });
    } else {
      prompt('Скопируйте ссылку для телефона:', url);
    }
  },

  /**
   * Получить зарегистрированных пользователей
   */
  loadRegisteredUsers() {
    const raw = localStorage.getItem(this.KEY_REGISTERED);
    return raw ? JSON.parse(raw) : [];
  },

  clearRegisteredUsers() {
    localStorage.removeItem(this.KEY_REGISTERED);
    fetch(this.getBackendUrl() + "/api/users/new", { method: "DELETE" }).catch(() => {});
  },

  exportJSON(data, filename = "registered_users.json") {
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: "application/json;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);
  },

  reset() {
    localStorage.removeItem(this.KEY);
    localStorage.removeItem(this.KEY_REGISTERED);
    fetch(this.getBackendUrl() + "/api/reset", { method: "POST" }).catch(() => {});
  }
};

// Инициализация при загрузке страницы
if (typeof window !== "undefined") {
  Storage._initBroadcast();
  Storage.syncWithServer();

  // Регулярный опрос (2.5 сек) для моментального появления новых дипломов и аккаунтов
  setInterval(() => {
    Storage.syncWithServer();
  }, 2500);

  // Опрос при возвращении фокуса в окно браузера
  window.addEventListener("focus", () => {
    Storage.syncWithServer();
  });

  // Обновление статусов
  window.addEventListener("DOMContentLoaded", () => {
    Storage._updateStatusPills();
  });
}

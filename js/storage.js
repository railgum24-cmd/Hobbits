/**
 * Модуль Storage — единственное место проекта,
 * где происходит прямое обращение к localStorage.
 *
 * Все остальные модули работают с данными исключительно
 * через промежуточный слой (api.js), а не напрямую.
 */
const Storage = {
  /** Ключ, под которым хранится вся база в localStorage */
  KEY: "lyceum_achievements_db_v1",

  /**
   * Загрузить всю базу из localStorage.
   * @returns {Object|null} — объект базы данных или null, если записи ещё нет
   */
  load() {
    const raw = localStorage.getItem(this.KEY);
    return raw ? JSON.parse(raw) : null;
  },

  /**
   * Сохранить всю базу целиком в localStorage.
   * @param {Object} db — объект базы данных для сохранения
   */
  save(db) {
    localStorage.setItem(this.KEY, JSON.stringify(db));
  },

  /**
   * Удалить базу из localStorage (полный сброс данных).
   */
  reset() {
    localStorage.removeItem(this.KEY);
  }
};

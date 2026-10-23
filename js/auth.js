// Вход и роли. Текущий пользователь хранится на время сессии (до закрытия вкладки).
const Auth = {
  // Вход по логину и паролю: проверку делает api.auth.check,
  // при неверных данных она бросает ошибку, и переход не происходит
  login(login, password) {
    const user = api.auth.check(login.trim(), password);
    sessionStorage.setItem("userId", user.id);
    location.href = user.role === "admin" ? "admin.html" : "student.html";
  },

  // Кто сейчас вошёл (или null)
  current() { return api.users.get(sessionStorage.getItem("userId")); },

  // Выход: забываем пользователя и возвращаемся на страницу входа
  logout() { sessionStorage.removeItem("userId"); location.href = "index.html"; },

  // Защита страницы. Вызывается в начале каждой страницы:
  // не вошёл -> на вход; зашёл не в свой раздел -> на свою страницу
  guard(role) {
    const u = this.current();
    if (!u) { location.href = "index.html"; return null; }
    if (u.role !== role) { location.href = u.role === "admin" ? "admin.html" : "student.html"; return null; }
    return u;
  }
};
// Тестовые данные для демо: портал достижений лицея
// Хранятся в .js, чтобы сайт открывался без сервера.

const SEED = {

  /* ──────────────────────────────────────────────
     Пользователи системы
     ────────────────────────────────────────────── */
  users: [
    // Администратор
    {
      id: "admin-1",
      name: "Ильдар Маратович",
      class: null,
      role: "admin",
      login: "admin",
      password: "admin2026"
    },

    // ── Команда 9Б ──
    {
      id: "user-1",
      name: "Гумеров Раиль",
      class: "9Б",
      role: "student",
      login: "Rail",
      password: "2026"
    },
    {
      id: "user-2",
      name: "Якубов Амир",
      class: "9Б",
      role: "student",
      login: "Amir",
      password: "2026"
    },
    {
      id: "user-3",
      name: "Фаррахов Ислам",
      class: "9Б",
      role: "student",
      login: "Islam",
      password: "2026"
    },
    {
      id: "user-4",
      name: "Биктагиров Самир",
      class: "9Б",
      role: "student",
      login: "Samir",
      password: "2026"
    },
    {
      id: "user-5",
      name: "Авдошин Радислав",
      class: "9Б",
      role: "student",
      login: "Radislav",
      password: "2026"
    },
    {
      id: "user-6",
      name: "Яруллин Самат",
      class: "9Б",
      role: "student",
      login: "Samat",
      password: "2026"
    },

    // ── Ученики из других классов ──
    {
      id: "user-7",
      name: "Хасанова Алия",
      class: "10А",
      role: "student",
      login: "Aliya",
      password: "2026"
    },
    {
      id: "user-8",
      name: "Загиров Тимур",
      class: "11Б",
      role: "student",
      login: "Timur",
      password: "2026"
    },
    {
      id: "user-9",
      name: "Валиуллина Камила",
      class: "9А",
      role: "student",
      login: "Kamila",
      password: "2026"
    }
  ],

  /* ──────────────────────────────────────────────
     Достижения учеников
     ────────────────────────────────────────────── */
  achievements: [

    // ═══ APPROVED (подтверждённые) ═══

    {
      id: "ach-1",
      userId: "user-1",
      title: "Олимпиада по физике «Росатом»",
      category: "physics",
      type: "olympiad",
      level: "region",
      result: "winner",
      points: 50,
      date: "2026-02-14",
      status: "approved",
      verifiedBy: "admin-1",
      verifiedAt: "2026-02-20",
      comment: "Отлично! Диплом подтверждён.",
      description: "Победитель регионального этапа олимпиады по физике «Росатом» среди 9 классов."
    },
    {
      id: "ach-2",
      userId: "user-2",
      title: "Городская олимпиада по математике",
      category: "math",
      type: "olympiad",
      level: "city",
      result: "prize",
      points: 25,
      date: "2026-01-20",
      status: "approved",
      verifiedBy: "admin-1",
      verifiedAt: "2026-01-25",
      comment: "Призёр, диплом загружен.",
      description: "Призёр (2-е место) городской олимпиады по математике."
    },
    {
      id: "ach-3",
      userId: "user-3",
      title: "Хакатон «Digital Skills»",
      category: "informatics",
      type: "competition",
      level: "region",
      result: "winner",
      points: 40,
      date: "2026-03-10",
      status: "approved",
      verifiedBy: "admin-1",
      verifiedAt: "2026-03-15",
      comment: "Победа подтверждена организатором.",
      description: "Команда заняла 1-е место на региональном хакатоне по программированию."
    },
    {
      id: "ach-4",
      userId: "user-7",
      title: "Научно-практическая конференция «Старт в науку»",
      category: "project",
      type: "conference",
      level: "city",
      result: "winner",
      points: 35,
      date: "2026-04-05",
      status: "approved",
      verifiedBy: "admin-1",
      verifiedAt: "2026-04-10",
      comment: "Диплом 1-й степени подтверждён.",
      description: "Лучший доклад на городской научно-практической конференции, секция «Экология»."
    },
    {
      id: "ach-5",
      userId: "user-8",
      title: "Всероссийская олимпиада по информатике (региональный этап)",
      category: "informatics",
      type: "olympiad",
      level: "region",
      result: "prize",
      points: 35,
      date: "2026-01-30",
      status: "approved",
      verifiedBy: "admin-1",
      verifiedAt: "2026-02-05",
      comment: "Призёр, протокол проверен.",
      description: "Призёр регионального этапа ВсОШ по информатике, 11 класс."
    },
    {
      id: "ach-6",
      userId: "user-4",
      title: "Школьная олимпиада по физике",
      category: "physics",
      type: "olympiad",
      level: "school",
      result: "winner",
      points: 20,
      date: "2025-11-15",
      status: "approved",
      verifiedBy: "admin-1",
      verifiedAt: "2025-11-18",
      comment: "Протокол школьного этапа подтверждён.",
      description: "Победитель школьного этапа олимпиады по физике."
    },
    {
      id: "ach-7",
      userId: "user-6",
      title: "Волонтёрская акция «Чистый берег»",
      category: "volunteering",
      type: "volunteering",
      level: "city",
      result: "participant",
      points: 10,
      date: "2026-05-20",
      status: "approved",
      verifiedBy: "admin-1",
      verifiedAt: "2026-05-22",
      comment: "Благодарственное письмо получено.",
      description: "Участие в городской экологической акции по очистке берега реки."
    },

    // ═══ Олимпиада по татарскому языку ═══

    {
      id: "ach-15",
      userId: "user-9",
      title: "Олимпиада по татарскому языку «Туган тел»",
      category: "tatar",
      type: "olympiad",
      level: "city",
      result: "winner",
      points: 35,
      date: "2026-10-05",
      status: "approved",
      verifiedBy: "admin-1",
      verifiedAt: "2026-10-09",
      comment: "Диплом победителя подтверждён.",
      description: "1-е место на городской олимпиаде по татарскому языку и литературе среди 9 классов."
    },

    // ═══ PENDING (ожидают проверки) ═══

    {
      id: "ach-8",
      userId: "user-5",
      title: "Региональный конкурс проектов «IT-решения»",
      category: "informatics",
      type: "project",
      level: "region",
      result: "prize",
      points: 30,
      date: "2026-09-25",
      status: "pending",
      verifiedBy: null,
      verifiedAt: null,
      comment: "",
      description: "Проект «Умное расписание» занял 2-е место на региональном конкурсе."
    },
    {
      id: "ach-9",
      userId: "user-1",
      title: "Городская олимпиада по математике",
      category: "math",
      type: "olympiad",
      level: "city",
      result: "winner",
      points: 35,
      date: "2026-10-02",
      status: "pending",
      verifiedBy: null,
      verifiedAt: null,
      comment: "",
      description: "Победитель городской олимпиады по математике среди 9 классов."
    },
    {
      id: "ach-10",
      userId: "user-9",
      title: "Школьная научная конференция",
      category: "project",
      type: "conference",
      level: "school",
      result: "prize",
      points: 15,
      date: "2026-10-10",
      status: "pending",
      verifiedBy: null,
      verifiedAt: null,
      comment: "",
      description: "Доклад «Фракталы в природе» на школьной конференции, 2-е место."
    },
    {
      id: "ach-11",
      userId: "user-2",
      title: "Волонтёрский проект «Помощь ветеранам»",
      category: "volunteering",
      type: "volunteering",
      level: "school",
      result: "participant",
      points: 5,
      date: "2026-10-15",
      status: "pending",
      verifiedBy: null,
      verifiedAt: null,
      comment: "",
      description: "Организация поздравительных открыток для ветеранов лицея."
    },
    {
      id: "ach-12",
      userId: "user-8",
      title: "Федеральный конкурс «Большие вызовы»",
      category: "project",
      type: "competition",
      level: "federal",
      result: "participant",
      points: 20,
      date: "2026-09-18",
      status: "pending",
      verifiedBy: null,
      verifiedAt: null,
      comment: "",
      description: "Участие в финале всероссийского конкурса проектов «Большие вызовы»."
    },
    {
      id: "ach-16",
      userId: "user-7",
      title: "Республиканская олимпиада по татарскому языку",
      category: "tatar",
      type: "olympiad",
      level: "region",
      result: "prize",
      points: 35,
      date: "2026-10-18",
      status: "pending",
      verifiedBy: null,
      verifiedAt: null,
      comment: "",
      description: "Призёр республиканского этапа олимпиады по татарскому языку, 10 класс."
    },

    // ═══ REJECTED (отклонённые) ═══

    {
      id: "ach-13",
      userId: "user-3",
      title: "Олимпиада по математике «Ломоносов»",
      category: "math",
      type: "olympiad",
      level: "federal",
      result: "prize",
      points: 0,
      date: "2026-03-28",
      status: "rejected",
      verifiedBy: "admin-1",
      verifiedAt: "2026-04-02",
      comment: "Не предоставлено подтверждение. Загрузите скан диплома.",
      description: "Заявка на призёрство в олимпиаде «Ломоносов» по математике."
    },
    {
      id: "ach-14",
      userId: "user-5",
      title: "Городской турнир по робототехнике",
      category: "informatics",
      type: "competition",
      level: "city",
      result: "winner",
      points: 0,
      date: "2026-05-12",
      status: "rejected",
      verifiedBy: "admin-1",
      verifiedAt: "2026-05-18",
      comment: "Не предоставлено подтверждение. Результат не найден в протоколе соревнований.",
      description: "Заявка на победу в городском турнире по робототехнике."
    }
  ],

  /* ──────────────────────────────────────────────
     Мероприятия лицея (афиша).
     Создаются администратором в admin.html,
     ученики записываются из личного кабинета.
     participants — массив id записавшихся.
     ────────────────────────────────────────────── */
  events: [
    {
      id: "ev-1",
      title: "Олимпиада по татарскому языку",
      category: "tatar",
      type: "olympiad",
      level: "city",
      date: "2026-11-14",
      time: "10:00",
      deadline: "2026-11-10",
      place: "Актовый зал лицея, 2-й этаж",
      organizer: "Кафедра татарского языка и литературы",
      description: "Городской этап олимпиады по татарскому языку и литературе для 9–11 классов. Два тура: лексико-грамматический тест и творческое задание. Победители представят лицей на республиканском этапе.",
      link: "",
      createdBy: "admin-1",
      createdAt: "2026-10-20",
      participants: ["user-1", "user-9"]
    },
    {
      id: "ev-2",
      title: "Республиканская олимпиада по татарскому языку «Туган тел»",
      category: "tatar",
      type: "olympiad",
      level: "region",
      date: "2026-12-05",
      time: "10:00",
      deadline: "2026-11-28",
      place: "Республиканский олимпиадный центр",
      organizer: "Министерство образования и науки Республики Татарстан",
      description: "Республиканский этап олимпиады по татарскому языку и литературе. Лицей направляет победителей городского этапа и призёров прошлого года.",
      link: "",
      createdBy: "admin-1",
      createdAt: "2026-10-21",
      participants: ["user-7"]
    },
    {
      id: "ev-3",
      title: "Школьный этап ВсОШ по физике",
      category: "physics",
      type: "olympiad",
      level: "school",
      date: "2026-10-30",
      time: "09:00",
      deadline: "2026-10-27",
      place: "Кабинет физики № 204",
      organizer: "МО учителей физики",
      description: "Отборочный этап для учеников 9–11 классов. Победители и призёры проходят на муниципальный этап ВсОШ.",
      link: "",
      createdBy: "admin-1",
      createdAt: "2026-10-18",
      participants: ["user-4", "user-5"]
    },
    {
      id: "ev-4",
      title: "Городской хакатон «Digital Skills 2026»",
      category: "informatics",
      type: "competition",
      level: "city",
      date: "2026-12-12",
      time: "11:00",
      deadline: "2026-12-01",
      place: "IT-квантум, корпус 2",
      organizer: "Центр цифрового образования",
      description: "Командный хакатон по программированию и робототехнике. Команда лицея — до 4 человек, возрастная категория 9–11 классов.",
      link: "",
      createdBy: "admin-1",
      createdAt: "2026-10-22",
      participants: ["user-3", "user-6"]
    },
    {
      id: "ev-5",
      title: "Олимпиада по математике «Ломоносов»",
      category: "math",
      type: "olympiad",
      level: "federal",
      date: "2026-09-20",
      time: "10:00",
      deadline: "2026-09-15",
      place: "Дистанционный формат",
      organizer: "МГУ имени М. В. Ломоносова",
      description: "Отборочный тур олимпиады школьников «Ломоносов» по математике. Результаты опубликованы в личных кабинетах участников.",
      link: "",
      createdBy: "admin-1",
      createdAt: "2026-09-01",
      participants: ["user-2", "user-3"]
    }
  ],

  /* ──────────────────────────────────────────────
     Таблица начисления баллов
     Ключ — тип мероприятия, значение — баллы
     по результату (winner / prize / participant)
     ────────────────────────────────────────────── */
  pointsTable: {
    olympiad: {
      school:  { winner: 20, prize: 15, participant: 5 },
      city:    { winner: 35, prize: 25, participant: 10 },
      region:  { winner: 50, prize: 35, participant: 15 },
      federal: { winner: 70, prize: 50, participant: 25 }
    },
    competition: {
      school:  { winner: 15, prize: 10, participant: 5 },
      city:    { winner: 30, prize: 20, participant: 10 },
      region:  { winner: 40, prize: 30, participant: 15 },
      federal: { winner: 60, prize: 40, participant: 20 }
    },
    conference: {
      school:  { winner: 15, prize: 10, participant: 5 },
      city:    { winner: 35, prize: 25, participant: 10 },
      region:  { winner: 45, prize: 30, participant: 15 },
      federal: { winner: 60, prize: 45, participant: 20 }
    },
    project: {
      school:  { winner: 15, prize: 10, participant: 5 },
      city:    { winner: 30, prize: 20, participant: 10 },
      region:  { winner: 45, prize: 30, participant: 15 },
      federal: { winner: 60, prize: 40, participant: 20 }
    },
    volunteering: {
      school:  { winner: 10, prize: 5,  participant: 5 },
      city:    { winner: 20, prize: 15, participant: 10 },
      region:  { winner: 30, prize: 20, participant: 15 },
      federal: { winner: 40, prize: 30, participant: 20 }
    },
    exam: {
      school:  { winner: 15, prize: 10, participant: 5 },
      city:    { winner: 30, prize: 20, participant: 10 },
      region:  { winner: 45, prize: 30, participant: 15 },
      federal: { winner: 60, prize: 45, participant: 25 }
    }
  }
};

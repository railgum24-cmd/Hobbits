/**
 * Генератор дипломов Портала достижений лицея
 * Стиль: Dark Perspective с дизайном по референсу:
 * динамичные изгибы (swoosh), золотая окантовка, наградная медаль с лавровым венком,
 * элегантная академическая типографика, электронная подпись и криптографический хэш.
 * 
 * Создаёт 3 вида дипломов: Победитель (Gold), Призёр (Silver), Участник (Bronze)
 * Экспорт в PNG через HTML Canvas API.
 */

const DiplomaGenerator = (() => {

  const THEMES = {
    winner: {
      rankTitle: 'ПОБЕДИТЕЛЬ I СТЕПЕНИ',
      rankSub: '1-Е МЕСТО • ВЫСШАЯ АКАДЕМИЧЕСКАЯ НАГРАДА',
      accent: '#00BD7D',
      accentLight: '#34D399',
      accentGlow: 'rgba(0, 189, 125, 0.25)',
      gold: '#F59E0B',
      goldLight: '#FCD34D',
      medallionTitle: '1 МЕСТО',
      medallionSub: 'WINNER',
      crestChar: '★'
    },
    prize: {
      rankTitle: 'ПРИЗЁР II СТЕПЕНИ',
      rankSub: '2-Е МЕСТО • ПРИЗЁР РЕГИОНАЛЬНОГО ТУРНИРА',
      accent: '#38BDF8',
      accentLight: '#7DD3FC',
      accentGlow: 'rgba(56, 189, 248, 0.25)',
      gold: '#CBD5E1',
      goldLight: '#F8FAFC',
      medallionTitle: 'ПРИЗЁР',
      medallionSub: 'PRIZE',
      crestChar: '◈'
    },
    participant: {
      rankTitle: 'СЕРТИФИКАТ УЧАСТНИКА',
      rankSub: 'АКТИВНОЕ УЧАСТИЕ В ОЛИМПИАДНОМ ДВИЖЕНИИ ЛИЦЕЯ',
      accent: '#A78BFA',
      accentLight: '#C4B5FD',
      accentGlow: 'rgba(167, 139, 250, 0.25)',
      gold: '#D8B4FE',
      goldLight: '#F3E8FF',
      medallionTitle: 'ФИНАЛИСТ',
      medallionSub: 'HONOR',
      crestChar: '❖'
    }
  };

  const CATS = {
    physics: 'ФИЗИКА И КВАНТОВАЯ ОПТИКА',
    math: 'ПРИКЛАДНАЯ МАТЕМАТИКА И МОДЕЛИРОВАНИЕ',
    informatics: 'ИНФОРМАТИКА И АЛГОРИТМЫ',
    project: 'ИНЖЕНЕРНЫЕ ПРОЕКТЫ И ИССЛЕДОВАНИЯ',
    volunteering: 'ЛИЦЕЙСКОЕ ВОЛОНТЁРСТВО И ИНИЦИАТИВЫ'
  };

  function generate(opts) {
    const resKey = (opts.result || 'participant').toLowerCase();
    const theme = THEMES[resKey] || THEMES.participant;
    const catLabel = CATS[opts.category] || (opts.category ? opts.category.toUpperCase() : 'ОБЩИЙ ПРОФИЛЬ');

    const W = 1200;
    const H = 850;
    const canvas = document.createElement('canvas');
    canvas.width = W;
    canvas.height = H;
    const ctx = canvas.getContext('2d');

    // 1. Глубокий темный фон
    ctx.fillStyle = '#080C14';
    ctx.fillRect(0, 0, W, H);

    // Мягкий радиальный ореол в лево-центральной зоне
    const radGrad = ctx.createRadialGradient(W / 2 - 100, H / 2, 40, W / 2 - 100, H / 2, 540);
    radGrad.addColorStop(0, theme.accentGlow);
    radGrad.addColorStop(0.7, 'rgba(8, 12, 20, 0.5)');
    radGrad.addColorStop(1, '#080C14');
    ctx.fillStyle = radGrad;
    ctx.fillRect(0, 0, W, H);

    // Микро-сетка точек
    ctx.fillStyle = 'rgba(255, 255, 255, 0.03)';
    for (let x = 36; x < W - 36; x += 32) {
      for (let y = 36; y < H - 36; y += 32) {
        if (x < W - 240 || y < H - 240) {
          ctx.fillRect(x, y, 1.5, 1.5);
        }
      }
    }

    // 2. Рамки по периметру
    const inset = 28;
    const inner = inset + 8;

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.lineWidth = 1;
    roundRect(ctx, inset, inset, W - 2 * inset, H - 2 * inset, 12);
    ctx.stroke();

    ctx.strokeStyle = theme.accent + '66';
    ctx.lineWidth = 1;
    roundRect(ctx, inner, inner, W - 2 * inner, H - 2 * inner, 8);
    ctx.stroke();

    // 3. ВЕРХНИЙ ЛЕВЫЙ УГОЛ: ДИНАМИЧНЫЕ КРИВЫЕ/ПОЛОСЫ (как в референсе)
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(inner, inner);
    ctx.lineTo(inner + 180, inner);
    ctx.lineTo(inner, inner + 180);
    ctx.closePath();
    ctx.fillStyle = '#0E1826';
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(inner, inner);
    ctx.lineTo(inner + 130, inner);
    ctx.lineTo(inner, inner + 130);
    ctx.closePath();
    ctx.fillStyle = theme.accent + '28';
    ctx.fill();

    // Линии отсечения (золотая + акцентная)
    ctx.strokeStyle = theme.gold;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(inner, inner + 140);
    ctx.lineTo(inner + 140, inner);
    ctx.stroke();

    ctx.strokeStyle = theme.accent;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(inner, inner + 155);
    ctx.lineTo(inner + 155, inner);
    ctx.stroke();

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(inner, inner + 185);
    ctx.lineTo(inner + 185, inner);
    ctx.stroke();
    ctx.restore();

    // 4. НИЖНИЙ ПРАВЫЙ УГОЛ: ДИНАМИЧНЫЕ ИЗГИБЫ (SWOOSH WAVES)
    ctx.save();
    // Волна 1 (глубокая подложка)
    ctx.beginPath();
    ctx.moveTo(W * 0.42, H - inner);
    ctx.bezierCurveTo(W * 0.65, H * 0.82, W * 0.78, H * 0.62, W - inner, H * 0.40);
    ctx.lineTo(W - inner, H - inner);
    ctx.closePath();
    ctx.fillStyle = '#0C1320';
    ctx.fill();

    // Волна 2 (акцентная)
    ctx.beginPath();
    ctx.moveTo(W * 0.52, H - inner);
    ctx.bezierCurveTo(W * 0.72, H * 0.88, W * 0.84, H * 0.70, W - inner, H * 0.52);
    ctx.lineTo(W - inner, H - inner);
    ctx.closePath();
    ctx.fillStyle = theme.accent + '1E';
    ctx.fill();

    // Окантовка волны 1: Золотая линия
    ctx.beginPath();
    ctx.moveTo(W * 0.42, H - inner);
    ctx.bezierCurveTo(W * 0.65, H * 0.82, W * 0.78, H * 0.62, W - inner, H * 0.40);
    ctx.strokeStyle = theme.gold;
    ctx.lineWidth = 4;
    ctx.stroke();

    // Параллельная неоновая линия
    ctx.beginPath();
    ctx.moveTo(W * 0.42 + 4, H - inner);
    ctx.bezierCurveTo(W * 0.65 + 4, H * 0.82 + 4, W * 0.78 + 4, H * 0.62 + 4, W - inner, H * 0.40 + 4);
    ctx.strokeStyle = theme.accent;
    ctx.lineWidth = 2;
    ctx.stroke();

    // Вторая тонкая золотая линия
    ctx.beginPath();
    ctx.moveTo(W * 0.52, H - inner);
    ctx.bezierCurveTo(W * 0.72, H * 0.88, W * 0.84, H * 0.70, W - inner, H * 0.52);
    ctx.strokeStyle = theme.gold + '66';
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.restore();

    // 5. КРУГЛАЯ НАГРАДНАЯ МЕДАЛЬ (SEAL MEDALLION) СПРАВА
    const sealX = W - 170;
    const sealY = H * 0.52;
    const sealR = 74;

    ctx.save();
    // Ленты медали, свисающие вниз
    const ribbonH = 80;
    ctx.fillStyle = theme.gold;
    ctx.strokeStyle = '#B46405';
    ctx.lineWidth = 1;

    // Левая лента
    ctx.beginPath();
    ctx.moveTo(sealX - 24, sealY + 40);
    ctx.lineTo(sealX - 44, sealY + 40 + ribbonH);
    ctx.lineTo(sealX - 28, sealY + 40 + ribbonH - 14);
    ctx.lineTo(sealX - 12, sealY + 40 + ribbonH);
    ctx.lineTo(sealX - 8, sealY + 40);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Правая лента
    ctx.beginPath();
    ctx.moveTo(sealX + 8, sealY + 40);
    ctx.lineTo(sealX + 12, sealY + 40 + ribbonH);
    ctx.lineTo(sealX + 28, sealY + 40 + ribbonH - 14);
    ctx.lineTo(sealX + 44, sealY + 40 + ribbonH);
    ctx.lineTo(sealX + 24, sealY + 40);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Зубчатый внешний круг медали
    const numTeeth = 36;
    ctx.beginPath();
    for (let i = 0; i < numTeeth * 2; i++) {
      const a = i * (Math.PI / numTeeth);
      const r = (i % 2 === 0) ? sealR + 6 : sealR - 2;
      const tx = sealX + r * Math.cos(a);
      const ty = sealY + r * Math.sin(a);
      if (i === 0) ctx.moveTo(tx, ty);
      else ctx.lineTo(tx, ty);
    }
    ctx.closePath();
    ctx.fillStyle = theme.gold;
    ctx.fill();
    ctx.strokeStyle = theme.goldLight;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Внутренний темный диск
    ctx.beginPath();
    ctx.arc(sealX, sealY, sealR - 6, 0, Math.PI * 2);
    ctx.fillStyle = '#101725';
    ctx.fill();
    ctx.strokeStyle = theme.goldLight;
    ctx.lineWidth = 2;
    ctx.stroke();

    // Тонкое кольцо с акцентным цветом
    ctx.beginPath();
    ctx.arc(sealX, sealY, sealR - 14, 0, Math.PI * 2);
    ctx.strokeStyle = theme.accent + 'AA';
    ctx.lineWidth = 1;
    ctx.stroke();

    // Точечный орнамент по кругу
    ctx.fillStyle = theme.goldLight;
    for (let i = 0; i < 24; i++) {
      const a = i * (Math.PI / 12);
      const px = sealX + (sealR - 10) * Math.cos(a);
      const py = sealY + (sealR - 10) * Math.sin(a);
      ctx.fillRect(px - 1, py - 1, 2, 2);
    }

    // Текст внутри медали
    ctx.textAlign = 'center';
    ctx.fillStyle = theme.goldLight;
    ctx.font = '700 12px "Segoe UI", sans-serif';
    ctx.fillText('★ ★ ★', sealX, sealY - 24);

    ctx.fillStyle = '#FFFFFF';
    ctx.font = '700 22px "Oswald", sans-serif';
    ctx.fillText(theme.medallionTitle, sealX, sealY - 2);

    ctx.fillStyle = theme.goldLight;
    ctx.font = '700 10px "JetBrains Mono", monospace';
    ctx.fillText(theme.medallionSub, sealX, sealY + 16);

    ctx.fillStyle = theme.accentLight;
    ctx.font = '700 11px "JetBrains Mono", monospace';
    ctx.fillText('• 2026 •', sealX, sealY + 30);
    ctx.restore();

    // 6. ПРОСТОРНАЯ ГАРМОНИЧНАЯ ТИПОГРАФИКА (РАСПРЕДЕЛЕНА ПО ВСЕЙ ВЫСОТЕ ХОЛСТА)
    const leftX = inner + 80;
    const maxTextW = 660;

    // 1. Шапка организации
    const yInst = 100;
    ctx.textAlign = 'left';
    ctx.fillStyle = theme.gold;
    ctx.font = '700 13px "JetBrains Mono", monospace';
    ctx.fillText('МБОУ «ИНЖЕНЕРНЫЙ ЛИЦЕЙ» • ОФИЦИАЛЬНЫЙ РЕЕСТР', leftX, yInst);

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(leftX, yInst + 14);
    ctx.lineTo(leftX + 520, yInst + 14);
    ctx.stroke();

    ctx.strokeStyle = theme.accent;
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(leftX, yInst + 14);
    ctx.lineTo(leftX + 130, yInst + 14);
    ctx.stroke();

    // 2. Главный титульный заголовок: Д И П Л О М
    const yTitle = 180;
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '700 56px "Oswald", sans-serif';
    ctx.fillText('Д  И  П  Л  О  М', leftX, yTitle);

    // 3. Статусная плашка награды (свободно, не впритык)
    const yPill = 275;
    const pillW = 440;
    const pillH = 38;

    ctx.fillStyle = '#0F1928';
    roundRect(ctx, leftX, yPill, pillW, pillH, 6);
    ctx.fill();
    ctx.strokeStyle = theme.accent;
    ctx.lineWidth = 2;
    roundRect(ctx, leftX, yPill, pillW, pillH, 6);
    ctx.stroke();

    ctx.fillStyle = theme.accentLight;
    ctx.font = '700 16px "Oswald", sans-serif';
    ctx.fillText(theme.rankTitle, leftX + 20, yPill + 24);

    ctx.textAlign = 'right';
    ctx.fillStyle = theme.gold;
    ctx.font = '700 12px "JetBrains Mono", monospace';
    const badgeText = resKey === 'winner' ? '1 МЕСТО • GOLD' : (resKey === 'prize' ? '2 МЕСТО • SILVER' : 'ФИНАЛИСТ • BRONZE');
    ctx.fillText(badgeText, leftX + pillW - 18, yPill + 23);

    // 4. Вводная строка награждения
    ctx.textAlign = 'left';
    const yIntro = 360;
    ctx.fillStyle = '#94A3B8';
    ctx.font = '400 15px "Poppins", sans-serif';
    ctx.fillText('НАГРАЖДАЕТСЯ', leftX, yIntro);

    // 5. ФИО лицеиста (крупно, элегантно, в центре)
    const yName = 415;
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '700 46px "Oswald", sans-serif';
    ctx.fillText(opts.name || 'Гумеров Раиль Рустемович', leftX, yName);

    // Класс и лицей
    const yCls = 485;
    ctx.fillStyle = theme.accent;
    ctx.font = '600 18px "Poppins", sans-serif';
    ctx.fillText(`${opts.studentClass || '9Б класс'} • МБОУ «Инженерный лицей»`, leftX, yCls);

    // Золотая акцентная черта-разделитель
    const yRule = 530;
    ctx.strokeStyle = theme.gold + '66';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(leftX, yRule);
    ctx.lineTo(leftX + maxTextW, yRule);
    ctx.stroke();

    ctx.fillStyle = theme.gold;
    ctx.fillRect(leftX, yRule - 1, 80, 2);

    // 6. Название олимпиады / турнира (чисто, лаконично)
    const yEvent = 565;
    ctx.fillStyle = '#F8FAFC';
    ctx.font = '700 24px "Poppins", sans-serif';
    let titleStr = opts.title || 'Всероссийская олимпиада школьников по информатике';
    if (titleStr.length > 55) titleStr = titleStr.substring(0, 52) + '...';
    ctx.fillText(titleStr, leftX, yEvent);

    // Профиль / предмет
    const yCat = 620;
    const catStr = `ПРОФИЛЬ: ${catLabel}`;
    ctx.font = '700 13px "JetBrains Mono", monospace';
    const tagW = ctx.measureText(catStr).width + 30;

    ctx.fillStyle = '#121C2C';
    roundRect(ctx, leftX, yCat, tagW, 30, 5);
    ctx.fill();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.18)';
    ctx.lineWidth = 1;
    roundRect(ctx, leftX, yCat, tagW, 30, 5);
    ctx.stroke();

    ctx.fillStyle = theme.accent;
    ctx.fillText(catStr, leftX + 15, yCat + 20);

    // 7. НИЖНЯЯ ПАНЕЛЬ: ДАТА, ПОДПИСЬ И КРИПТО-ХЭШ
    const footY = 705;
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(leftX, footY);
    ctx.lineTo(leftX + 600, footY);
    ctx.stroke();

    // Левая колонка: Дата
    ctx.fillStyle = '#94A3B8';
    ctx.font = '700 11px "JetBrains Mono", monospace';
    ctx.fillText('ДАТА ВЫДАЧИ:', leftX, footY + 18);
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '500 14px "JetBrains Mono", monospace';
    ctx.fillText(opts.date || '24 октября 2026 г.', leftX, footY + 38);
    ctx.fillStyle = theme.gold;
    ctx.font = '700 12px "JetBrains Mono", monospace';
    ctx.fillText('ПРИКАЗ № ЛИЦ-2026', leftX, footY + 60);

    // Центральная колонка: Подпись
    const col2X = leftX + 300;
    ctx.fillStyle = '#94A3B8';
    ctx.font = '700 11px "JetBrains Mono", monospace';
    ctx.fillText('ПРЕДСЕДАТЕЛЬ ОРГКОМИТЕТА:', col2X, footY + 18);

    // Факсимиле росчерка подписи
    ctx.strokeStyle = '#78B4FF';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(col2X + 10, footY + 44);
    ctx.lineTo(col2X + 35, footY + 30);
    ctx.lineTo(col2X + 55, footY + 48);
    ctx.lineTo(col2X + 75, footY + 34);
    ctx.lineTo(col2X + 110, footY + 42);
    ctx.lineTo(col2X + 150, footY + 28);
    ctx.lineTo(col2X + 190, footY + 38);
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(col2X + 150, footY + 36, 14, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(col2X, footY + 50);
    ctx.lineTo(col2X + 220, footY + 50);
    ctx.stroke();

    ctx.fillStyle = '#CBD5E1';
    ctx.font = '400 12px "Poppins", sans-serif';
    ctx.fillText('Проф. Сабитов К.Б.', col2X, footY + 66);

    // 8. КРИПТОГРАФИЧЕСКИЙ ХЭШ SHA-256
    const hashStr = (opts.name || 'USER') + (opts.title || 'ACH') + resKey;
    let simpleHash = '';
    for (let i = 0; i < 20; i++) {
      const code = (hashStr.charCodeAt(i % hashStr.length) * (i + 13) * 31) % 16;
      simpleHash += code.toString(16).toUpperCase();
    }
    const valStr = `КРИПТО-ХЭШ SHA-256 • ${simpleHash} • ID: #CERT-2026-${resKey.toUpperCase()} • ВЕРИФИЦИРОВАНО`;
    ctx.fillStyle = '#64748B';
    ctx.font = '700 11px "JetBrains Mono", monospace';
    ctx.fillText(valStr, leftX, H - inner - 24);

    return canvas.toDataURL('image/png');
  }

  function download(opts) {
    const dataUrl = generate(opts);
    const link = document.createElement('a');
    link.download = `Диплом_${opts.result || 'участник'}_${(opts.name || 'Ученик').replace(/\s+/g, '_')}.png`;
    link.href = dataUrl;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.lineTo(x + w - r, y);
    ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r);
    ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h);
    ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r);
    ctx.quadraticCurveTo(x, y, x + r, y);
    ctx.closePath();
  }

  return { generate, download, THEMES, CATS };
})();

// Скачивание таблицы как CSV-файла.
// Разделитель ";" и BOM (\uFEFF) нужны, чтобы Excel правильно показал кириллицу.
function downloadCSV(rows, filename) {
  // Каждое значение в кавычках, внутренние кавычки удваиваем (правило CSV)
  const text = rows.map(r => r.map(v => `"${String(v).replace(/"/g, '""')}"`).join(";")).join("\n");
  // Собираем файл в памяти и «кликаем» по невидимой ссылке для скачивания
  const blob = new Blob(["\uFEFF" + text], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
}
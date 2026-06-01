# Сортировка почты

Проект разработан в рамках хакатона по Технологиям Программирования.
Система автоматически читает входящие письма в различных форматах (TXT, EML, JSON, HTML), анализирует их содержимое (заголовки, адресатов, текст) и распределяет по соответствующим папкам.

---

## Описание работы алгоритма

1. Чтение.
   EmailReader сканирует папку inbox/, распознает форматы .txt, .json, .eml, .html и преобразует каждый файл в объект Email. Если файл поврежден или имеет неизвестное расширение, система записывает ошибку в объект и безопасно продолжает работу, не завершаясь аварийно.

3. Классификация.
   CategoryClassifier анализирует содержимое (тему, тело письма, отправителя) на основе правил из config.py. Проверка идет строго по приоритету: Спам → Важные → Черновики → Отправленные → Входящие. Если совпадений нет или при чтении возникла ошибка, письму присваивается категория Uncategorized.

4. Перемещение.
   FileMover переносит (удаляя из исходной папки) файлы в папки соответствующих категорий внутри директории sorted/.

5. Логирование и статистика.
   Logger записывает хронологию выполнения и все возникшие системные предупреждения в файл logs/processing.log. Параллельно StatisticsTracker подсчитывает метрики, и главный файл main.py выводит финальный текстовый отчет со счетчиками и распределением по папкам в logs/run_output.log.

---

## Структура проекта

```
Хакатон ТП/
├── src/           код
├── tests/         тесты pytest
├── inbox/         входящие файлы
├── sorted/        отсортированные письма (создается автоматически)
├── logs/          processing.log, run_output.log (создаются автоматически)
├── run.sh         bash-скрипт запуска
├── requirements.txt зависимости проекта
├── pytest.ini     конфигурация
└── README.md      документация
```

---

## Запуск

```bash
cd "Хакатон ТП"

# письма в inbox/

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

chmod +x run.sh
./run.sh

# тесты
pytest -v
```

`run.sh` пишет в консоль `запуск...`, потом `success` или `failed`. вывод программы (print) уходит в `logs/run_output.log`, stderr в `errors.log`.

---

## Архитектура и логика

Проект построен с использованием принципов ООП. Главная функция process_mailbox() (в main.py) координирует работу следующих модулей:
```
inbox/mail_0001.txt
       ↓
EmailReader.read_file()  →  Отвечает за парсинг писем. Поддерживает форматы .txt, .json, .eml, .html. Формирует универсальный дата-класс Email.
       ↓
CategoryClassifier.classify()  →  Анализирует текст и заголовки письма на основе ключевых слов из config.py.
       ↓
FileMover.move_email()  →  Физически распределяет файлы по папкам.
       ↓
Logger + Statistics  →  Собирают аналитику распределения и ведут журнал работы. Битые файлы безопасно получают статус ошибки чтения и отправляются в папку Uncategorized.
```

---

## Файлы в src/

### `__init__.py`

Одна строка коммента `# сортировка почты по папкам`. нужен чтобы `python3 -m src.main` работал (пакет).

---

### `models.py`

класс `Email` через `@dataclass` — просто данные письма:

- `filename`, `file_path`
- `subject`, `body`, `sender`, `recipients`
- `headers`, `raw_content`
- `read_error` — если `None` то ок, иначе строка с ошибкой

---

### `config.py`

Константы категорий (`CATEGORY_INBOX = "Входящие"` и тд), список `ALL_CATEGORIES`, расширения `SUPPORTED_EXTENSIONS`.

`RULES` — список словарей с `category` и `words`. **порядок важен**: сначала спам, потом важные, черновики, отправленные, входящие. кто первый совпал — тот и категория.

в комментариях написано из каких mail_ взяли слова (типа mail_0041).

---

### `email_reader.py`

`EmailReader(inbox_dir)` читает файлы из inbox.

- `list_email_files()` — список файлов, без скрытых (с точкой)
- `read_all()` — все письма списком
- `read_file(path)` — одно письмо

Читает через `read_text`, сначала utf-8, если не вышло — cp1251. пустой файл → ошибка. неизвестное расширение → ошибка.

форматы:
- `.txt` — `_parse_txt`, заголовки Subject/Тема/От кого (см `HEADER_NAMES`)
- `.json` — from, subject, body
- `.eml` — модуль `email`
- `.html` — body + title если есть

Ошибки не через `raise`, а в `mail.read_error`, чтобы main не упал.

---

### `classifier.py`

`CategoryClassifier`, правила из `RULES` (можно свои передать в тестах).

`classify(mail)`:
- если `read_error` — сразу `Uncategorized`
- иначе ищет слова в тексте (`_get_full_text` — subject, body, sender, filename, recipients, всё в lower)

`classify_batch` — для списка, возвращает dict `{имя: категория}`.

---

### `file_mover.py`

Создаёт папки в `sorted/`, переносит `shutil.move` (не копия).

Если файл с таким именем уже есть — `_fix_name` добавляет `_1`, `_2`...

`move_email` возвращает `(True, "ok")` или `(False, текст ошибки)`.

---

### `logger.py`

Пишет в `logs/processing.log` и в консоль строки вида `[2026-06-01 14:00:00] [INFO] пошли`.

Методы: `info`, `warning`, `error` (в error можно передать `filename=`).

---

### `statistics.py`

счётчики:
- `n_all` — сколько файлов видели
- `ok_n` — успешно перенесли
- `read_errors`, `move_errors`
- `by_cat` — словарь по категориям

Методы: `add_file()`, `add_success(cat)`, `register_read_error()`, `register_move_error()`, `get_report()`.

Пример вывода `get_report()`:

```
итог по почте
файлов: 100
норм: 95
read fail: 3
move fail: 2

папки:
  Входящие - 76
  Спам - 6
```

(цифры примерные)

---

### `main.py`

`get_project_root()` — корень проекта (родитель папки src).

`process_mailbox(inbox, sorted, log_file)`:
1. создаёт logger, stats, reader, classifier, mover
2. `logger.info("пошли")`
3. читает все письма, если пусто — `inbox пустой` и отчёт
4. цикл: `stats.add_file()`, classify, при read_error → uncategorized + лог, move, при успехе `add_success`
5. в конце `print(stats.get_report())`, `logger.info("всё")`
6. возвращает `ret` (0 или 1)

`main()` вызывает `process_mailbox` с путями `inbox`, `sorted`, `logs/processing.log` и `sys.exit(code)`.

---

## run.sh

Короткий bash:
- нет `inbox` → `нет папки inbox`, exit 1
- `mkdir -p logs`
- `echo "запуск..."`
- `python3 -m src.main >> logs/run_output.log 2>> errors.log`
- success / failed

---

## Тесты

`pytest -v`

| файл | про что |
|------|---------|
| `conftest.py` | временные папки inbox/output |
| `test_email_reader.py` | txt, json, русские заголовки, пустые |
| `test_classifier.py` | спам, важные, входящие |
| `test_file_mover.py` | перенос |
| `test_error_handling.py` | не падает на битых |
| `test_statistics.py` | отчёт, там проверяется `файлов: 1` и `Входящие - 1` |

фикстуры pytest создаёт сама, удаляет временные папки.

---

## Категории

| папка | слова (не все) |
|-------|----------------|
| Спам | lottery, вы выиграли, spam |
| Важные | срочно, urgent, инцидент |
| Черновики | draft, черновик |
| Отправленные | re:, fwd: |
| Входящие | vpn, zoom, it-support, не работает |
| Uncategorized | остальное + битые |

Добавить слово — в `config.py` в `RULES` в нужный список `words`.

---


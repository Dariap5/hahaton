# сортировка почты (хакатон ТП, ВШЭ)

проект для хакатона по технологиям программирования. если чтото непонятно — ниже расписано по файлам, мы сами так разбирались когда писали.

---

## что вообще делает

1. берёт файлы из `inbox/` (это письма, txt eml json и тд)
2. читает каждый
3. кидает в папку по категории: Входящие, Спам, Важные...
4. пишет лог + в консоль печатает стата

если файл битый — программа не падает, кладёт в `Uncategorized` и пишет в лог.

---

## папки

```
Хакатон ТП/
├── src/           код
├── tests/         тесты pytest
├── inbox/         сюда кладём письма
├── sorted/        сюда они уезжают после запуска
├── logs/          processing.log, run_output.log
├── run.sh         запуск
├── requirements.txt
├── pytest.ini
└── README.md
```

`sorted/` и `logs/` в гите обычно пустые, создаются при работе.

---

## запуск

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

## схема (как связано)

```
inbox/mail_0001.txt
       ↓
EmailReader.read_file()  → объект Email
       ↓
CategoryClassifier.classify()
       ↓
FileMover.move_email()   → sorted/Спам/...
       ↓
Logger + Statistics
```

всё крутит `main.py`, функция `process_mailbox()`.

---

## файлы в src/

### `__init__.py`

там одна строка коммента `# сортировка почты по папкам`. нужен чтобы `python3 -m src.main` работал (пакет).

---

### `models.py`

класс `Email` через `@dataclass` — просто данные письма:

- `filename`, `file_path`
- `subject`, `body`, `sender`, `recipients`
- `headers`, `raw_content`
- `read_error` — если `None` то ок, иначе строка с ошибкой

логики тут нет, только поля.

---

### `config.py`

константы категорий (`CATEGORY_INBOX = "Входящие"` и тд), список `ALL_CATEGORIES`, расширения `SUPPORTED_EXTENSIONS`.

`RULES` — список словарей с `category` и `words`. **порядок важен**: сначала спам, потом важные, черновики, отправленные, входящие. кто первый совпал — тот и категория.

в комментах написано из каких mail_ взяли слова (типа mail_0041).

---

### `email_reader.py`

`EmailReader(inbox_dir)` читает файлы из inbox.

- `list_email_files()` — список файлов, без скрытых (с точкой)
- `read_all()` — все письма списком
- `read_file(path)` — одно письмо

читает через `read_text`, сначала utf-8, если не вышло — cp1251. пустой файл → ошибка. неизвестное расширение → ошибка.

форматы:
- `.txt` — `_parse_txt`, заголовки Subject/Тема/От кого (см `HEADER_NAMES`)
- `.json` — from, subject, body
- `.eml` — модуль `email`
- `.html` — body + title если есть

ошибки не через `raise`, а в `mail.read_error`, чтобы main не упал.

---

### `classifier.py`

`CategoryClassifier`, правила из `RULES` (можно свои передать в тестах).

`classify(mail)`:
- если `read_error` — сразу `Uncategorized`
- иначе ищет слова в тексте (`_get_full_text` — subject, body, sender, filename, recipients, всё в lower)

`classify_batch` — для списка, возвращает dict `{имя: категория}`.

---

### `file_mover.py`

создаёт папки в `sorted/`, переносит `shutil.move` (не копия).

если файл с таким именем уже есть — `_fix_name` добавляет `_1`, `_2`...

`move_email` возвращает `(True, "ok")` или `(False, текст ошибки)`.

---

### `logger.py`

пишет в `logs/processing.log` и в консоль строки вида `[2026-06-01 14:00:00] [INFO] пошли`.

методы: `info`, `warning`, `error` (в error можно передать `filename=`).

---

### `statistics.py`

счётчики:
- `n_all` — сколько файлов видели
- `ok_n` — успешно перенесли
- `read_errors`, `move_errors`
- `by_cat` — словарь по категориям

методы: `add_file()`, `add_success(cat)`, `register_read_error()`, `register_move_error()`, `get_report()`.

пример вывода `get_report()`:

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

короткий bash:
- нет `inbox` → `нет папки inbox`, exit 1
- `mkdir -p logs`
- `echo "запуск..."`
- `python3 -m src.main >> logs/run_output.log 2>> errors.log`
- success / failed

---

## тесты

`pytest -v` из корня (нужен venv с requirements).

| файл | про что |
|------|---------|
| `conftest.py` | временные папки inbox/output |
| `test_email_reader.py` | txt, json, русские заголовки, пустые |
| `test_classifier.py` | спам, важные, входящие |
| `test_file_mover.py` | перенос |
| `test_error_handling.py` | не падает на битых |
| `test_statistics.py` | отчёт, там проверяется `файлов: 1` и `Входящие - 1` |

фикстуры pytest сама создаёт и удаляет временные папки.

---

## категории (кратко)

| папка | слова (не все) |
|-------|----------------|
| Спам | lottery, вы выиграли, spam |
| Важные | срочно, urgent, инцидент |
| Черновики | draft, черновик |
| Отправленные | re:, fwd: |
| Входящие | vpn, zoom, it-support, не работает |
| Uncategorized | остальное + битые |

добавить слово — в `config.py` в `RULES` в нужный список `words`.

---

## вопросы которые у нас были

**почему inbox пустой после запуска?**  
файлы **переносятся** в sorted, не копируются. перед новым прогоном снова положить в inbox.

**где смотреть что случилось?**  
- `logs/processing.log` — наш лог (пошли, ошибки по файлам, всё)  
- `logs/run_output.log` — print отчёта  
- `errors.log` — если python упал

**зачем столько файлов?**  
по заданию OOP + тесты + run.sh, так и сдавали вроде.

---

## кто что делал (команда)

| кусок | файл |
|-------|------|
| модель письма | `models.py` |
| слова и категории | `config.py` |
| чтение | `email_reader.py` |
| классификация | `classifier.py` |
| перенос | `file_mover.py` |
| лог | `logger.py` |
| стата | `statistics.py` |
| главный цикл | `main.py` |
| bash | `run.sh` |

---

## python если совсем с нуля

| слово | смысл |
|-------|--------|
| переменная | `x = 5` |
| функция | `def f():` |
| класс | `class A:` |
| import | подключить модуль |
| for / if | цикл и условие |
| try/except | поймать ошибку |
| list / dict | список и словарь |

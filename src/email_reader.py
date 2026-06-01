import email
import json
from email import policy
from pathlib import Path

from src.config import SUPPORTED_EXTENSIONS
from src.models import Email

# заголовки в txt (русские и английские)
HEADER_NAMES = {
    "subject": "subject",
    "from": "from",
    "to": "to",
    "тема": "subject",
    "от кого": "from",
    "кому": "to",
}


class EmailReader:

    def __init__(self, inbox_dir):
        self.inbox_dir = Path(inbox_dir)

    def list_email_files(self):
        if not self.inbox_dir.exists():
            return []

        files = []
        for f in sorted(self.inbox_dir.iterdir()):
            if f.is_file() and not f.name.startswith("."):
                files.append(f)
        return files

    def read_all(self):
        mails = []
        for f in self.list_email_files():
            mails.append(self.read_file(f))
        return mails

    def read_file(self, path):
        path = Path(path)
        mail = Email(filename=path.name, file_path=path)

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                text = path.read_text(encoding="cp1251")
            except (UnicodeDecodeError, OSError) as err:
                mail.read_error = "Не удалось прочитать файл: " + str(err)
                return mail
        except (PermissionError, OSError) as err:
            mail.read_error = str(err)
            return mail

        if text.strip() == "":
            mail.read_error = "Файл пустой"
            return mail

        mail.raw_content = text
        ext = path.suffix.lower()

        if ext not in SUPPORTED_EXTENSIONS:
            mail.read_error = "Неизвестный формат: " + (ext or "без расширения")
            return mail

        try:
            if ext == ".eml":
                self._parse_eml(mail, text)
            elif ext == ".json":
                self._parse_json(mail, text)
            elif ext in {".html", ".htm"}:
                self._parse_html(mail, text)
            else:
                self._parse_txt(mail, text)
        except Exception as err:
            mail.read_error = "Ошибка разбора: " + str(err)

        return mail

    def _parse_txt(self, mail, text):
        lines = text.splitlines()
        body = []
        in_body = False

        for line in lines:
            if not in_body and ":" in line:
                key, val = line.split(":", 1)
                key = key.strip().lower()
                val = val.strip()

                if key in HEADER_NAMES:
                    field = HEADER_NAMES[key]
                    mail.headers[key] = val
                    if field == "subject":
                        mail.subject = val
                    elif field == "from":
                        mail.sender = val
                    elif field == "to":
                        mail.recipients = [x.strip() for x in val.split(",")]
                    continue

            in_body = True
            body.append(line)

        mail.body = "\n".join(body).strip()
        if mail.subject == "" and len(body) > 0:
            mail.subject = body[0][:120]

    def _parse_json(self, mail, text):
        data = json.loads(text)
        if isinstance(data, list):
            data = data[0]
        mail.sender = str(data.get("from", ""))
        mail.subject = str(data.get("subject", ""))
        mail.body = str(data.get("body", ""))

    def _parse_eml(self, mail, text):
        # модуль email разбирает .eml (учили на семинаре)
        msg = email.message_from_string(text, policy=policy.default)
        mail.subject = str(msg.get("Subject", ""))
        mail.sender = str(msg.get("From", ""))

        to_list = []
        for h in ("To", "Cc", "Bcc"):
            v = msg.get(h)
            if v:
                to_list.extend([x.strip() for x in str(v).split(",")])
        mail.recipients = to_list
        mail.headers = {k: str(v) for k, v in msg.items()}

        if msg.is_multipart():
            parts = []
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    c = part.get_content()
                    if c:
                        parts.append(str(c))
            mail.body = "\n".join(parts)
        else:
            c = msg.get_content()
            mail.body = "" if c is None else str(c)

    def _parse_html(self, mail, text):
        mail.body = text
        t = text.lower()
        s = t.find("<title>")
        e = t.find("</title>")
        if s != -1 and e != -1:
            mail.subject = text[s + 7:e].strip()
        if mail.subject == "":
            mail.subject = "HTML письмо"

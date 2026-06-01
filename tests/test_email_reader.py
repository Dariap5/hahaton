"""Тесты чтения писем."""

from src.email_reader import EmailReader


def test_txt_file(inbox_folder):
    text = (
        "Subject: Test subject\n"
        "From: sender@example.com\n"
        "To: support@company.com\n\n"
        "Hello, this is a test message."
    )
    f = inbox_folder / "message.txt"
    f.write_text(text, encoding="utf-8")

    mail = EmailReader(inbox_folder).read_file(f)

    assert mail.read_error is None
    assert mail.subject == "Test subject"
    assert mail.sender == "sender@example.com"
    assert "test message" in mail.body


def test_russian_headers(inbox_folder):
    text = (
        "От кого: Иван <ivan@company.ru>\n"
        "Кому: it-support@company.ru\n"
        "Тема: Запрос доступа\n\n"
        "Не работает VPN."
    )
    f = inbox_folder / "ru_mail.txt"
    f.write_text(text, encoding="utf-8")

    mail = EmailReader(inbox_folder).read_file(f)

    assert mail.read_error is None
    assert mail.subject == "Запрос доступа"
    assert "it-support@company.ru" in mail.recipients[0]


def test_json_file(inbox_folder):
    text = '{"from": "test@corp", "subject": "Аккаунт", "body": "текст"}'
    f = inbox_folder / "mail.json"
    f.write_text(text, encoding="utf-8")

    mail = EmailReader(inbox_folder).read_file(f)

    assert mail.read_error is None
    assert mail.subject == "Аккаунт"


def test_no_extension(inbox_folder):
    text = "From: a@b.com\nTo: it-support@company.ru\nSubject: API\n\nТекст"
    f = inbox_folder / "mail_0106"
    f.write_text(text, encoding="utf-8")

    mail = EmailReader(inbox_folder).read_file(f)

    assert mail.read_error is None
    assert mail.subject == "API"


def test_empty_file(inbox_folder):
    f = inbox_folder / "empty.txt"
    f.write_text("", encoding="utf-8")

    mail = EmailReader(inbox_folder).read_file(f)

    assert mail.read_error is not None
    assert "пустой" in mail.read_error.lower()


def test_bad_format(inbox_folder):
    f = inbox_folder / "unknown.xyz"
    f.write_text("data", encoding="utf-8")

    mail = EmailReader(inbox_folder).read_file(f)

    assert mail.read_error is not None


def test_skip_hidden(inbox_folder):
    (inbox_folder / ".DS_Store").write_bytes(b"hide")
    (inbox_folder / "mail.txt").write_text("Subject: Hi\n\nBody", encoding="utf-8")

    files = EmailReader(inbox_folder).list_email_files()

    assert len(files) == 1

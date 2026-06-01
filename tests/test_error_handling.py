"""Тесты обработки ошибок."""

from pathlib import Path

from src.classifier import CategoryClassifier
from src.config import CATEGORY_UNCATEGORIZED
from src.email_reader import EmailReader
from src.main import process_mailbox
from src.models import Email


def test_empty_file(inbox_folder):
    f = inbox_folder / "empty.txt"
    f.write_text("", encoding="utf-8")

    mail = EmailReader(inbox_folder).read_file(f)
    assert CategoryClassifier().classify(mail) == CATEGORY_UNCATEGORIZED


def test_unknown_format(inbox_folder):
    f = inbox_folder / "data.bin"
    f.write_bytes(b"\x00\x01")

    mail = EmailReader(inbox_folder).read_file(f)
    assert mail.read_error is not None
    assert CategoryClassifier().classify(mail) == CATEGORY_UNCATEGORIZED


def test_no_rules():
    mail = Email("x.txt", Path("x.txt"), "Привет", "Обычное сообщение")
    assert CategoryClassifier().classify(mail) == CATEGORY_UNCATEGORIZED


def test_processing_continues(inbox_folder, tmp_path):
    (inbox_folder / "bad.bin").write_bytes(b"\x00")
    (inbox_folder / "good.txt").write_text(
        "Subject: Проблема с VPN\nFrom: a@b.com\n\nНе работает VPN",
        encoding="utf-8",
    )

    code = process_mailbox(inbox_folder, tmp_path / "sorted", tmp_path / "log.txt")

    assert code == 0
    assert (tmp_path / "sorted" / "Uncategorized" / "bad.bin").exists()
    assert (tmp_path / "sorted" / "Входящие" / "good.txt").exists()
    assert (tmp_path / "log.txt").exists()  # проверяем, что файл с логами создан


def test_empty_inbox(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    code = process_mailbox(inbox, tmp_path / "sorted", tmp_path / "log.txt")
    assert code == 0

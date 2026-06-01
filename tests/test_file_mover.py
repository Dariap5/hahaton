"""Тесты перемещения файлов."""

from src.file_mover import FileMover
from src.models import Email


def test_move(inbox_folder, output_folder):
    src = inbox_folder / "mail.txt"
    src.write_text("Subject: Test\n\nBody", encoding="utf-8")

    mail = Email("mail.txt", src)
    ok, _ = FileMover(output_folder).move_email(mail, "Входящие")

    assert ok
    assert (output_folder / "Входящие" / "mail.txt").exists()
    assert not src.exists()


def test_dirs(output_folder):
    FileMover(output_folder).ensure_category_dirs()
    assert (output_folder / "Спам").is_dir()
    assert (output_folder / "Uncategorized").is_dir()

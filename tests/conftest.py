"""Фикстуры для тестов — временные папки."""

import pytest
from pathlib import Path

from src.models import Email


@pytest.fixture
def inbox_folder(tmp_path):
    # папка inbox для одного теста
    folder = tmp_path / "inbox"
    folder.mkdir()
    return folder


@pytest.fixture
def output_folder(tmp_path):
    # папка sorted для одного теста
    folder = tmp_path / "sorted"
    folder.mkdir()
    return folder


@pytest.fixture
def sample_email():
    return Email(
        filename="test.txt",
        file_path=Path("test.txt"),
        subject="Help with ticket",
        body="Please help with my support request",
        sender="user@company.com",
    )

"""Тесты классификации."""

from pathlib import Path

from src.classifier import CategoryClassifier
from src.config import (
    CATEGORY_DRAFTS,
    CATEGORY_IMPORTANT,
    CATEGORY_INBOX,
    CATEGORY_SENT,
    CATEGORY_SPAM,
    CATEGORY_UNCATEGORIZED,
)
from src.models import Email


def test_spam():
    mail = Email("a.txt", Path("a.txt"), "You won!", "Click here lottery prize")
    assert CategoryClassifier().classify(mail) == CATEGORY_SPAM


def test_important():
    mail = Email("b.txt", Path("b.txt"), "URGENT server down", "Critical incident")
    assert CategoryClassifier().classify(mail) == CATEGORY_IMPORTANT


def test_draft():
    mail = Email("c.txt", Path("c.txt"), "Draft notes", "черновик письма")
    assert CategoryClassifier().classify(mail) == CATEGORY_DRAFTS


def test_sent():
    mail = Email("d.txt", Path("d.txt"), "Re: update", "Forwarded reply")
    assert CategoryClassifier().classify(mail) == CATEGORY_SENT


def test_inbox():
    mail = Email("e.txt", Path("e.txt"), "Help ticket", "it-support problem with VPN")
    assert CategoryClassifier().classify(mail) == CATEGORY_INBOX


def test_uncategorized():
    mail = Email("f.txt", Path("f.txt"), "Hello", "Just saying hi")
    assert CategoryClassifier().classify(mail) == CATEGORY_UNCATEGORIZED


def test_broken_file():
    mail = Email("broken.txt", Path("broken.txt"), read_error="empty")
    assert CategoryClassifier().classify(mail) == CATEGORY_UNCATEGORIZED


def test_spam_iphone():
    mail = Email(
        "mail_0041.txt",
        Path("mail_0041.txt"),
        "Вы выиграли iPhone 15!",
        "введите логин http://secure-login-verify.net",
    )
    assert CategoryClassifier().classify(mail) == CATEGORY_SPAM


def test_important_ad():
    mail = Email(
        "mail_0101.txt",
        Path("mail_0101.txt"),
        "Срочно: не работает Active Directory",
        "работа остановлена",
    )
    assert CategoryClassifier().classify(mail) == CATEGORY_IMPORTANT


def test_custom_rules():
    rules = [{"category": "VIP", "words": ["ceo"]}]
    mail = Email("x.txt", Path("x.txt"), "Message for CEO", "hello")
    assert CategoryClassifier(rules=rules).classify(mail) == "VIP"


def test_batch():
    mails = [
        Email("a.txt", Path("a.txt"), "spam lottery", ""),
        Email("b.txt", Path("b.txt"), "hello", ""),
    ]
    res = CategoryClassifier().classify_batch(mails)
    assert res["a.txt"] == CATEGORY_SPAM
    assert res["b.txt"] == CATEGORY_UNCATEGORIZED

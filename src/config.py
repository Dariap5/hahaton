# папки в sorted/

CATEGORY_INBOX = "Входящие"
CATEGORY_SENT = "Отправленные"
CATEGORY_SPAM = "Спам"
CATEGORY_IMPORTANT = "Важные"
CATEGORY_DRAFTS = "Черновики"
CATEGORY_UNCATEGORIZED = "Uncategorized"

ALL_CATEGORIES = [
    CATEGORY_INBOX,
    CATEGORY_SENT,
    CATEGORY_SPAM,
    CATEGORY_IMPORTANT,
    CATEGORY_DRAFTS,
    CATEGORY_UNCATEGORIZED,
]

SUPPORTED_EXTENSIONS = {".txt", ".eml", ".msg", ".html", ".htm", ".json", ""}

# слова из inbox.zip, сверху вниз
# кто первый совпал — тот и категория
RULES = [
    {
        "category": CATEGORY_SPAM,
        "words": [
            # mail_0041, mail_0071, mail_0093
            "вы выиграли", "розыгрыш", "iphone 15", "totally-not-spam",
            "verify.net", "secure-login", "введите логин", "банковск",
            "верификация аккаунта", "спам", "spam", "lottery", "лотере",
        ],
    },
    {
        "category": CATEGORY_IMPORTANT,
        "words": [
            # mail_0012, mail_0101, mail_0062
            "urgent", "срочно", "critical", "[critical]", "критич",
            "инцидент", "массовый сбой", "работа остановлена",
        ],
    },
    {
        "category": CATEGORY_DRAFTS,
        "words": ["draft", "черновик", "не отправлять"],
    },
    {
        "category": CATEGORY_SENT,
        "words": [
            # mail_0013, mail_0065, mail_0099
            "re:", "fwd:", "forwarded message", "перенаправляю",
        ],
    },
    {
        "category": CATEGORY_INBOX,
        "words": [
            # mail_0001, mail_0010, mail_0020 и др.
            "it-support", "заявк", "запрос", "проблем", "не работ",
            "не могу", "ошибк", "vpn", "zoom", "chrome", "confluence",
            "принтер", "доступ", "падает", "недоступ",
        ],
    },
]

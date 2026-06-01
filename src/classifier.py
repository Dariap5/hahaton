from src.config import CATEGORY_UNCATEGORIZED, RULES


class CategoryClassifier:

    def __init__(self, rules=None):
        self.rules = rules if rules is not None else RULES

    def classify(self, mail):
        if mail.read_error is not None:
            return CATEGORY_UNCATEGORIZED

        text = self._get_full_text(mail)

        for rule in self.rules:
            for word in rule["words"]:
                if word.lower() in text:
                    return rule["category"]

        return CATEGORY_UNCATEGORIZED

    def _get_full_text(self, mail):
        parts = [mail.subject, mail.body, mail.sender, mail.filename]
        parts.extend(mail.recipients)
        return " ".join(parts).lower()

    def classify_batch(self, mails):
        res = {}
        for mail in mails:
            res[mail.filename] = self.classify(mail)
        return res

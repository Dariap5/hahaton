import shutil
from pathlib import Path

from src.config import ALL_CATEGORIES, CATEGORY_UNCATEGORIZED


class FileMover:

    def __init__(self, output_dir):
        self.output_dir = Path(output_dir)

    def ensure_category_dirs(self):
        for cat in ALL_CATEGORIES:
            (self.output_dir / cat).mkdir(parents=True, exist_ok=True)

    def move_email(self, mail, category):
        folder = self.output_dir / category
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / mail.filename

        try:
            if dest.exists():
                dest = self._fix_name(dest)
            shutil.move(str(mail.file_path), str(dest))
            return True, "ok"
        except (PermissionError, OSError) as err:
            return False, str(err)

    def move_batch(self, mails, categories):
        res = []
        for mail in mails:
            cat = categories.get(mail.filename, CATEGORY_UNCATEGORIZED)
            ok, msg = self.move_email(mail, cat)
            res.append((mail.filename, ok, msg))
        return res

    def _fix_name(self, path):
        # дубль — добавляем _1 _2 ...
        n = 1
        new = path
        while new.exists():
            new = path.with_name(path.stem + "_" + str(n) + path.suffix)
            n += 1
        return new

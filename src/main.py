import sys
from pathlib import Path

from src.classifier import CategoryClassifier
from src.email_reader import EmailReader
from src.file_mover import FileMover
from src.logger import Logger
from src.statistics import Statistics


def get_project_root():
    return Path(__file__).resolve().parent.parent


def process_mailbox(inbox_dir, output_dir, log_file):
    logger = Logger(log_file)
    stats = Statistics()
    reader = EmailReader(inbox_dir)
    classifier = CategoryClassifier()
    mover = FileMover(output_dir)

    logger.info("пошли")
    mover.ensure_category_dirs()

    mails = reader.read_all()
    if len(mails) == 0:
        logger.warning("inbox пустой")
        print(stats.get_report())
        return 0

    ret = 0

    for mail in mails:
        stats.add_file()
        category = classifier.classify(mail)

        if mail.read_error is not None:
            stats.register_read_error()
            logger.error(mail.read_error, filename=mail.filename)
            category = "Uncategorized"

        ok, msg = mover.move_email(mail, category)
        if ok:
            stats.add_success(category)
        else:
            stats.register_move_error()
            logger.error(msg, filename=mail.filename)
            ret = 1

    print(stats.get_report())
    logger.info("всё")

    return ret


def main():
    root = get_project_root()
    code = process_mailbox(root / "inbox", root / "sorted", root / "logs" / "processing.log")
    sys.exit(code)


if __name__ == "__main__":
    main()

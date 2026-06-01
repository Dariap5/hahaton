

class Statistics:

    def __init__(self):
        self.n_all = 0
        self.ok_n = 0
        self.read_errors = 0
        self.move_errors = 0
        self.by_cat = {}

    def add_file(self):
        self.n_all += 1

    def register_read_error(self):
        self.read_errors += 1

    def register_move_error(self):
        self.move_errors += 1

    def add_success(self, category):
        self.ok_n += 1
        if category not in self.by_cat:
            self.by_cat[category] = 0
        self.by_cat[category] += 1

    def get_report(self):
        lines = [
            "итог по почте",
            "файлов: " + str(self.n_all),
            "норм: " + str(self.ok_n),
            "read fail: " + str(self.read_errors),
            "move fail: " + str(self.move_errors),
            "",
            "папки:",
        ]

        if self.by_cat:
            for category in sorted(self.by_cat):
                lines.append("  " + category + " - " + str(self.by_cat[category]))
        else:
            lines.append("  пусто")

        return "\n".join(lines)

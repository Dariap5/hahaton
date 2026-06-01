from datetime import datetime
from pathlib import Path


class Logger:

    def __init__(self, log_file, to_console=True):
        self.log_file = Path(log_file)
        self.to_console = to_console
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def info(self, msg):
        self._write("INFO", msg)

    def warning(self, msg):
        self._write("WARNING", msg)

    def error(self, msg, filename=None):
        if filename:
            msg = "[" + filename + "] " + msg
        self._write("ERROR", msg)

    def _write(self, level, msg):
        t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = "[" + t + "] [" + level + "] " + msg
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        if self.to_console:
            print(line)

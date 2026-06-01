from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Email:
    filename: str
    file_path: Path
    subject: str = ""
    body: str = ""
    sender: str = ""
    recipients: list = field(default_factory=list)
    headers: dict = field(default_factory=dict)
    raw_content: str = ""
    read_error: str = None

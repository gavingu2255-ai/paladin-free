# placeholder for future helpersimport uuid
import re


def generate_id():
    return str(uuid.uuid4())


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def log(message: str):
    print(f"[Runtime] {message}")

import re


EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\b(?:\+?\d{1,3}[\s-]?)?(?:\d[\s-]?){7,}\b")


def mask(text: str) -> str:
text = EMAIL.sub("<EMAIL>", text)
text = PHONE.sub("<PHONE>", text)
return text

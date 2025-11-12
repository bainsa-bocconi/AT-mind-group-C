import re


def basic_clean(text: str) -> str:
text = text.replace("\r", "\n")
text = re.sub(r"\n{3,}", "\n\n", text)
text = re.sub(r"\s+", " ", text)
return text.strip()

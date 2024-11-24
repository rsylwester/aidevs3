import re

import unidecode


def remove_whitespace_chars(text: str):
    return re.sub(r"\s+", "", text)


def remove_diacritics(text):
    return unidecode.unidecode(text)

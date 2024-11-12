import os
import re
import zipfile
from pathlib import Path
from typing import List

from bs4 import BeautifulSoup


def extract_human_readable_text(html: str) -> str:
    """
    Extracts and returns human-readable text from raw HTML.

    :param html: The raw HTML content as a string.
    :return: A single string containing all visible text, cleaned of HTML tags and extra whitespace.
    """
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Extract text content and clean up whitespace
    text = soup.get_text(separator=' ')
    human_readable_text = ' '.join(text.split())

    return human_readable_text


def unzip_file(zip_path: str, extensions: List[str] = None) -> list:
    """Unzip file and return list of paths to extracted audio files"""
    dir = os.path.dirname(zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dir)

    os.remove(zip_path)

    # Get all audio files
    files = []
    if extensions:
        for ext in extensions:
            files.extend(list(Path(dir).glob(ext)))
    else:
        return list(Path(zip_path).iterdir())

    return files

def get_tag_value(text: str, tag: str) -> str:
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"No {tag} tag found in text")
    return match.group(1)
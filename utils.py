import os
import pickle
import re
from pathlib import Path
from typing import List, Optional

import pyzipper
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


def unzip_file(zip_path: str, extensions: List[str] = None, password: Optional[str] = None,
               extract_to: Optional[str] = None) -> List[Path]:
    # Set the extraction directory
    if extract_to:
        extract_path = Path(extract_to)
    else:
        extract_path = Path(os.path.dirname(zip_path))

    # Ensure the extraction directory exists
    extract_path.mkdir(parents=True, exist_ok=True)

    extracted_files = []

    with pyzipper.AESZipFile(zip_path, 'r') as zip_ref:
        if password:
            zip_ref.pwd = password.encode('utf-8')

        # Extract all files
        zip_ref.extractall(extract_path)

    # Remove the original ZIP file
    os.remove(zip_path)

    # Filter files by extensions if provided
    if extensions:
        for ext in extensions:
            extracted_files.extend(extract_path.glob(ext))
    else:
        extracted_files = list(extract_path.iterdir())

    return extracted_files


def get_tag_value(text: str, tag: str) -> str:
    pattern = f"<{tag}>(.*?)</{tag}>"
    match = re.search(pattern, text)
    if not match:
        raise ValueError(f"No {tag} tag found in text")
    return match.group(1)


def filter_files_by_extension(file_paths: List[Path], extensions: list) -> List[Path]:
    extensions = {ext if ext.startswith('.') else f'.{ext}' for ext in extensions}
    return [file for file in file_paths if file.suffix in extensions]


def read_text_file(text_filepath: Path):
    with open(text_filepath, 'r', encoding='utf-8') as file:
        text = file.read()
        return text


SERIALIZED_FILENAME = "object.pickle"


def serialize(object):
    # Serialize and save to file
    with open(SERIALIZED_FILENAME, 'wb') as f:
        pickle.dump(object, f)


def deserialize():
    # Read from file and deserialize
    with open(SERIALIZED_FILENAME, 'rb') as f:
        loaded_object = pickle.load(f)
        return loaded_object


# Read files from a directory
def read_files_from_directory(directory):
    data = {}
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8") as f:
                data[file] = f.read()
    return data


def read_files_from_paths(paths: List[Path]) -> dict:
    data = {}
    for file_path in paths:
        file_path = Path(file_path)  # Ensure it's a Path object
        if file_path.is_file():
            with file_path.open("r", encoding="utf-8") as f:
                data[file_path.name] = f.read()
        else:
            print(f"Warning: {file_path} is not a valid file.")
    return data


def normalize_whitespace(text: str) -> str:
    # Remove all tabs
    text = text.replace("\t", "")
    # Replace multiple spaces with a single space
    text = re.sub(r" +", " ", text)
    # Remove trailing spaces before newlines
    text = re.sub(r" +(\r?\n)", r"\1", text)
    # Strip leading and trailing whitespace from the whole text
    return text.strip()

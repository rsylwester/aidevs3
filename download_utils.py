import json
import os
from urllib.parse import urlparse, ParseResult

import requests


def download_file(url: str, target_dir: str) -> str:
    """Download zip file from URL to target directory"""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    parsed_url: ParseResult = urlparse(url)
    filename: str = os.path.basename(parsed_url.path)

    local_filename = os.path.join(target_dir, filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def download_text_file_to_variable(url: str) -> str:
    # Send a GET request to the URL
    response = requests.get(url)
    # Raise an exception for any HTTP errors
    response.raise_for_status()
    # Return the content as a string (decoded from bytes)
    return response.text

def download_json_file_to_variable(url: str) -> dict:
    # Send a GET request to the URL
    response = requests.get(url)
    # Raise an exception for any HTTP errors
    response.raise_for_status()
    # Parse and return the JSON content as a dictionary
    return json.loads(response.text)

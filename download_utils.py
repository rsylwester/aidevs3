import json
import os
from pathlib import Path
from urllib.parse import urlparse, ParseResult, urljoin
from bs4 import BeautifulSoup

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


def download_website_with_resources(url: str, output_dir: Path):
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Download HTML
    response = requests.get(url)
    html_content = response.text
    html_path = output_dir / "index.html"

    with open(html_path, "w", encoding="utf-8") as file:
        file.write(html_content)

    # Parse and download resources
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup.find_all(["img", "link", "script", "audio", "source"]):
        # Check relevant attribute
        resource_url = (
                tag.get("src") or tag.get("href")
        )  # For img, script, source, link

        if resource_url:
            full_url = urljoin(url, resource_url)
            parsed_url = urlparse(resource_url)
            resource_local_path = output_dir / parsed_url.path.lstrip("/")

            # Ensure the directory structure exists
            os.makedirs(resource_local_path.parent, exist_ok=True)

            try:
                # Download the resource
                resource_response = requests.get(full_url)
                with open(resource_local_path, "wb") as resource_file:
                    resource_file.write(resource_response.content)

                # Update the HTML tag to point to the local path
                if tag.name in ["img", "audio", "source"]:
                    tag["src"] = parsed_url.path
                elif tag.name in ["link", "script"]:
                    tag["href"] = parsed_url.path
            except Exception as e:
                print(f"Failed to download {resource_url}: {e}")

    # Save the modified HTML with updated resource paths
    with open(html_path, "w", encoding="utf-8") as file:
        file.write(str(soup))

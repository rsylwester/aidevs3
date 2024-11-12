import os

import requests


def download_zip(url: str, target_dir: str) -> str:
    """Download zip file from URL to target directory"""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    local_filename = os.path.join(target_dir, "downloaded_file.zip")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

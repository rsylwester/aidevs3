import logging
import re
from pathlib import Path
from typing import List

import download_utils
import utils
from env import S03E01_URL_DATA

logging.basicConfig(level=logging.INFO, format="%(message)s")


def download_unzip_data(dir: str) -> List[Path]:
    if not Path(dir).exists():
        logging.info(f"Directory '{dir}' does not exist. Creating it.")
        Path(dir).mkdir(parents=True, exist_ok=True)

    if not any(Path(dir).iterdir()):
        logging.info(f"Directory '{dir}' is empty. Downloading and extracting data.")
        zipfile = download_utils.download_file(S03E01_URL_DATA, dir)
        return utils.unzip_file(zipfile)

    logging.info(f"Directory '{dir}' is not empty. Returning existing files.")
    return list(Path(dir).iterdir())


def parse_filename(filename: str) -> str:
    # Extract date
    date = filename.split("_")[0]

    # Extract sektor and ID using regex
    match = re.search(r"sektor_([A-Za-z]+\d+)", filename)
    if match:
        sektor_id = match.group(1)
    else:
        sektor_id = "Unknown"

    # Extract just the last part (e.g., 'A3')
    id_only = sektor_id[-2:] if len(sektor_id) >= 2 else sektor_id

    # Return the formatted string
    return f"{date}, sektor {sektor_id}, {id_only}, {filename}"

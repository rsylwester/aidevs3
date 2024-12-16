import json
from pathlib import Path

import download_utils
from env import S04E02_URL_DATA
from utils import read_csv, unzip_file

DATA_DIR = './data'
correct_data_file = Path(DATA_DIR).joinpath("correct.txt")
incorrect_data_file = Path(DATA_DIR).joinpath("incorrect.txt")
verify_data_file = Path(DATA_DIR).joinpath("verify.txt")
classification_jsonl_file = Path(DATA_DIR).joinpath("classification.jsonl")


def generate_training_jsonl_data():
    datafile: str = download_utils.download_file(S04E02_URL_DATA, DATA_DIR)
    unzip_file(zip_path=datafile)

    # Read correct and incorrect data
    correct_data = read_csv(correct_data_file)
    incorrect_data = read_csv(incorrect_data_file)

    # Generate JSONL data
    jsonl_data = []
    for entry in correct_data:
        jsonl_data.append({
            "messages": [
                {"role": "system", "content": "classify data:"},
                {"role": "user", "content": entry},
                {"role": "assistant", "content": "CORRECT"}
            ]
        })

    for entry in incorrect_data:
        jsonl_data.append({
            "messages": [
                {"role": "system", "content": "classify data:"},
                {"role": "user", "content": entry},
                {"role": "assistant", "content": "INCORRECT"}
            ]
        })

    # Write to JSONL file
    with open(classification_jsonl_file, "w") as jsonl_file:
        for item in jsonl_data:
            jsonl_file.write(json.dumps(item) + "\n")

    print(f"JSONL file generated: {classification_jsonl_file}")

import utils
from aidevs3 import send_answer, Answer
from openai_client import OpenAIClient
from s04e02.fine_tuner import generate_training_jsonl_data, classification_jsonl_file, verify_data_file
from utils import read_csv

openai_client = OpenAIClient()

if not utils.does_file_exist(classification_jsonl_file):
    generate_training_jsonl_data()

csv_data = read_csv(verify_data_file)

result = []

for row in csv_data:
    key, value = row.split("=")
    response = openai_client.ask_question(value, system_message="classify data:",
                                          model_name="ft:gpt-4o-mini-2024-07-18:personal:aidevs-s04e02-reaserch:Af7wdAHx")

    if response == "CORRECT":
        result.append(key)

send_answer(Answer(task="research", answer=result))

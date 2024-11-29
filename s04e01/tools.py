from aidevs3 import send_answer, Answer
from logger import logger
from s04e01.main import Action


# Function to communicate with the API
def communicate_with_api(answer):
    logger.info("Sending answer to API: %s", answer)
    response = send_answer(Answer(task="photos", answer=answer))
    logger.info("Answer sent to API successfully.")

    return response


def issue_command(command, file_name):
    response = communicate_with_api(f"{command} {file_name}")
    return response


def start_conversation():
    logger.info("Sending START command to API.")
    response = communicate_with_api("START")
    logger.info("Received response from API: %s", response)
    return response


def prepare_description(details):
    return f"Barbara ma {details['hair_color']} włosy, {details['height']} wzrostu, ubrana w {details['clothing']}, cechy szczególne: {details.get('distinctive_features', 'brak')}."


def process_photo(action: Action):
    issue_command(f"{action} {action.filename}")

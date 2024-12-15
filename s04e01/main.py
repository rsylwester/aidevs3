import re
from typing import List

from aidevs3 import Response, send_answer, Answer
from logger import logger
from openai_client import OpenAIClient
from s04e01.config import SMALL_IMAGE_SUFFIX, WORK_ON_SMALL_RESOLUTION
from s04e01.tools import start_conversation, issue_command, extract_iamges, ImageAction, ImageAnalysisResult, \
    BooleanResponse
from utils import get_filename_from_url, replace_filename_in_url, add_suffix, deserialize, serialize

VALID_IMAGES_SERIALIZED_FILENAME = "valid_images.pickle"

command_improve_image = f"""
Analyse photo carefully. Image may be broken, too bright, too dark. So you can use commands that will improve readability of image. 

Available commands: {ImageAction.improve_image_commands()}

If image is readable command should be: {ImageAction.done_command()}
"""

prepare_barbara_description = f"""
Przeanalizuj dostarczone zdjęcia i przygotuj bardzo szczegółowy i spójny rysopis osoby widocznej na większości z nich. Szczególną uwagę zwróć na detale, które wyróżniają daną osobę, takie jak tatuaże, blizny, znamiona, piegi, biżuteria, makijaż czy cechy nietypowe. Twoim zadaniem jest opisanie każdej możliwej cechy, nawet tych, które mogą wydawać się mniej istotne, pod warunkiem, że są widoczne na zdjęciach.

Uwzględnij:
	1.	Płeć i przybliżony wiek.
	2.	Dokładny kolor włosów, fryzurę (np. długość, styl, sposób uczesania).
	3.	Kolor oczu oraz ich kształt.
	4.	Kształt twarzy, nosa, ust, oraz widoczne detale skóry (np. pieprzyki, blizny, zmarszczki).
	5.	Wszystkie widoczne tatuaże – opisz ich wygląd, lokalizację oraz szczegóły, jeśli to możliwe.
	6.	Styl ubioru, rodzaj biżuterii i inne akcesoria (np. okulary, zegarki).
	7.	Postawę ciała i wyraz twarzy, jeśli jest widoczny.

Pamiętaj, że każdy szczegół ma znaczenie, nawet jeśli na pierwszy rzut oka wydaje się nieistotny. Jeśli coś jest widoczne, opisz to. W przypadku niejednoznaczności opisz wszystkie możliwe warianty w sposób klarowny.

RULES:
Zignoruj wszelkie nieistone informacje jak napisy
"""

openai_client = OpenAIClient()


def process_photo(action: ImageAction):
    issue_command(f"{action} {action.filename}")


start_response: Response = start_conversation()
images: List[str] = extract_iamges(start_response.message, small=True)

valid_images = deserialize(VALID_IMAGES_SERIALIZED_FILENAME)
valid_images = valid_images if valid_images else []

if not valid_images:
    for image_url in images:
        current_image_url = image_url
        for i in range(5):
            response: ImageAnalysisResult = openai_client.json_mode(prompt=command_improve_image,
                                                                    image_file_url=current_image_url,
                                                                    response_format=ImageAnalysisResult)

            if response.action == ImageAction.DONE:
                is_woman: BooleanResponse = openai_client.json_mode(prompt="Does image present woman? Return True if you are sure that on the images woman is presented. Otherwise return False.", image_file_url=current_image_url,
                                                   response_format=BooleanResponse)
                if is_woman.result:
                    valid_images.append(current_image_url)
                else:
                    logger.info(f"Image with not woman: {current_image_url}")

                break
            else:
                command_response: Response = issue_command(response.action.value, get_filename_from_url(current_image_url))
                image_name = re.search(r'\b\w+\.(?:png|jpg|jpeg|gif|bmp|tiff)\b', command_response.message,
                                       re.IGNORECASE).group()

                if WORK_ON_SMALL_RESOLUTION:
                    image_name = add_suffix(image_name, SMALL_IMAGE_SUFFIX)

                current_image_url = replace_filename_in_url(current_image_url, image_name)
                logger.info(f"Image after fixing: {current_image_url}")

    serialize(valid_images, VALID_IMAGES_SERIALIZED_FILENAME)

logger.info(f"Valid images: {valid_images}")

barbara_description =  openai_client.ask_with_images(system_message=prepare_barbara_description, image_file_urls=valid_images)
logger.info(f"Barbara: {barbara_description}")

send_answer(Answer(task="photos", answer=barbara_description))

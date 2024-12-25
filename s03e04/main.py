import pickle
from dataclasses import field, dataclass
from pathlib import Path
from typing import List

import download_utils
import utils
from aidevs3 import send_answer, Answer
from env import S03E04_URL_BARBARA_TXT
from logger import logger
from s03e04.s03e04_lib import extract_places_names, query_places_api, extract_peoples_names, query_people_api, \
    is_barbara_on_the_list
from utils import get_filename_from_url, is_file_exist

DATA_DIR = "./data"
STORAGE_PICKLE = "./data/storage.pickle"

person_to_places = {}
place_to_people = {}


def send_answer_about_barbara_location(city: str) -> bool:
    response = send_answer(Answer(task="loop", answer=city))

    if "there is no Barbara" in response.message:
        return False
    else:
        return True


@dataclass
class Storage:
    init_people_names: List[str] = field(default_factory=list)
    init_places_names: List[str] = field(default_factory=list)

    def serialize(self, filepath: str):
        """Serialize the object to a file."""
        with open(filepath, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def deserialize(filepath: str):
        """Deserialize the object from a file."""
        if is_file_exist(filepath):
            with open(filepath, 'rb') as file:
                return pickle.load(file)
        return None

    def is_empty(self) -> bool:
        """Check if all fields are empty."""
        return not (self.init_people_names or self.init_places_names)


storage = Storage.deserialize(STORAGE_PICKLE)
storage = Storage() if storage is None else storage

if storage.is_empty():

    if not utils.is_directory_exist(DATA_DIR) or utils.is_directory_empty(DATA_DIR):
        download_utils.download_file(S03E04_URL_BARBARA_TXT, DATA_DIR)

    barbara_info = utils.read_text_file(Path(DATA_DIR).joinpath(get_filename_from_url(S03E04_URL_BARBARA_TXT)))
    storage.init_places_names = extract_places_names(barbara_info)
    storage.init_people_names = extract_peoples_names(barbara_info)
    storage.serialize(STORAGE_PICKLE)

people_to_be_checked = storage.init_people_names
places_to_be_checked = storage.init_places_names

iteration = 0
while True:
    logger.info(f"Iteration: {iteration}")
    iteration += 1
    for person in people_to_be_checked:
        if not person in person_to_places:
            places_dict: dict = query_people_api(person)
            person_to_places[person] = places_dict.keys()

            places_to_be_checked.extend(places_dict.keys())

    for place in places_to_be_checked:
        if not place in place_to_people:
            people_dict = query_places_api(place)
            people = people_dict.keys()
            place_to_people[place] = people

            if is_barbara_on_the_list(people):

                result = send_answer_about_barbara_location(place)
                if result:
                    logger.info(f"Barbara found in: [{place}]")
                    exit(0)
                else:
                    continue

            people_to_be_checked.extend(people)

# initial load
# for person in storage.init_people_names:
#     if not person in person_to_places:
#         places_dict: dict = query_people_api(person)
#         person_to_places[person] = places_dict.keys()

# for place in storage.init_places_names:
#     if not place in place_to_people:
#         people_dict = query_places_api(place)
#         place_to_people[place] = people_dict.values()
# if is_barbara_on_the_list(people_dict.keys()):

#     result = send_answer_about_barbara_location(place)
#     if result:
#         logger.info(f"Barbara found in: [{place}]")
#         exit(0)
#     else:
#         continue
#
# place_to_people[place] = people_dict.values()

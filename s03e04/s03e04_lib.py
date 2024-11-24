import re
from dataclasses import dataclass
from typing import List

import pandas as pd
import requests
from names_dataset import NameDataset

import text_utils
from env import AIDEVS_API_KEY, S03E04_URL_API_PEOPLE, S03E04_URL_API_PLACES
from logger import logger
from openai_client import OpenAIClient
from text_utils import remove_diacritics


@dataclass
class Response:
    code: int
    message: str


cities_df = pd.read_csv('./data/poland_cities.csv', header=None, names=['city', 'region'])
cities_df['normalized_city'] = cities_df['city'].apply(lambda x: remove_diacritics(x).lower())

valid_city_name_pattern = re.compile(r"^[A-Za-z\s'-]+$")
valic_first_name_pattern = re.compile(r"^[A-Za-z'-]{2,50}$")

openai_client = OpenAIClient()


def query_people_api(person) -> dict:
    '''
    This API allows you to search for members of the resistance by their first name (provided in the nominative case). The API returns a list of locations where the specified individual has been sighted.
    :param person:
    :return:
    '''
    logger.info(f"Querying [people] API, query: {person}")
    response = requests.post(
        S03E04_URL_API_PEOPLE,
        json={"apikey": AIDEVS_API_KEY, "query": person},
    )
    response.raise_for_status()
    data = response.json()

    api_response = Response(code=data.get("code"), message=data.get("message"))

    if api_response.code == 0:
        response = {}
        places = api_response.message.split()
        valid_places = []

        for place in places:
            place_modified = remove_diacritics(place)
            if is_valid_polish_city(place_modified):
                place_modified = place_modified.lower()
                valid_places.append(place_modified)
                response[place_modified] = place

        if len(places) > len(valid_places):
            logger.warn(f"Person [{person}] - Invalid places found: {list(set(places) - set(valid_places))}")

        logger.info(f"Person [{person}] visited places: {valid_places}")
        return response
    else:
        logger.error(data)
        raise Exception("Wrong response from places API")


def query_places_api(place):
    '''
    This API allows you to search for members of the resistance who have been seen in a specific city. You provide the name of the city (without Polish characters), and the API returns a list of resistance members sighted in that location.
    :param person:
    :return:
    '''
    logger.info(f"Querying [places] API, query: {place}")
    response = requests.post(
        S03E04_URL_API_PLACES,
        json={"apikey": AIDEVS_API_KEY, "query": place},
    )
    response.raise_for_status()
    data = response.json()
    logger.info(f"Response received: {data}")

    api_response = Response(code=data.get("code"), message=data.get("message"))

    if api_response.code == 0:
        response = {}
        people = api_response.message.split()
        valid_people = []

        for person in people:
            person_modified = remove_diacritics(person)
            if is_valid_first_name(person_modified):
                person_modified = person_modified.lower()
                valid_people.append(person_modified)
                response[person_modified] = person

        if len(people) > len(valid_people):
            logger.warn(f"Place [{place}] - Invalid people found: {list(set(people) - set(valid_people))}")

        logger.info(f"Place [{place}] visited by: {valid_people}")
        return response
    else:
        logger.error(data)
        raise Exception("Wrong response from places API")


def extract_peoples_names(text: str) -> List[str]:
    instruction = '''
    Extract all people’s first names in their nominative form from the given text,
    ensuring that any Polish characters (e.g., ą, ś, ć, ł) are replaced with their base Latin equivalents (e.g., a, s, c, l).
    Return the extracted names as a single string, with each name separated by a comma. Only include valid names in the output.
    '''
    response = openai_client.ask_question(question=text, system_message=instruction)
    return text_utils.remove_whitespace_chars(response).split(",")


def extract_places_names(text: str) -> List[str]:
    instruction = '''
    Extract all places names in their nominative form from the given text,
    ensuring that any Polish characters (e.g., ą, ś, ć, ł) are replaced with their base Latin equivalents (e.g., a, s, c, l).
    Return the extracted names as a single string, with each name separated by a comma. Only include valid names in the output.
    '''
    response = openai_client.ask_question(question=text, system_message=instruction)
    return text_utils.remove_whitespace_chars(response).split(",")


def is_valid_polish_city(city_name):
    if bool(valid_city_name_pattern.match(city_name)):
        try:
            normalized_city_name = remove_diacritics(city_name.strip()).lower()
            return normalized_city_name in cities_df['normalized_city'].values
        except Exception as e:
            logger.error(f"Error during city [{city_name}] validation. {e}")

    return False


def is_valid_first_name(name):
    nd = NameDataset()
    valid_regex = valid_city_name_pattern.match(name)
    if valid_regex:
        result = nd.search(name)['first_name']
        return bool(result)

    return False


def is_barbara_on_the_list(people: list):
    if "barbara" in people:
        return True

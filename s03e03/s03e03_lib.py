import re

import requests

from env import AIDEVS_API_KEY, S03E03_URL_API_DB
from logger import logger
from openai_client import OpenAIClient

openai_client = OpenAIClient()

def query_api(task, query):
    logger.info(f"Querying API with task: {task}, query: {query}")
    response = requests.post(
        S03E03_URL_API_DB,
        json={"task": task, "apikey": AIDEVS_API_KEY, "query": query},
    )
    response.raise_for_status()
    data = response.json()
    logger.info(f"Response received: {data}")
    return data

def fetch_table_structure():
    logger.info("Fetching table structure...")

    # Fetch tables from the database
    response = query_api("database", "show tables")
    if "reply" in response:
        tables = [item["Tables_in_banan"] for item in response["reply"]]
    else:
        logger.error(f"Unexpected response format: {response}")
        raise KeyError("Key 'reply' not found in the API response.")

    logger.info(f"Tables found: {tables}")

    # Fetch schema for each table
    table_schemas = {}
    for table in tables:
        logger.info(f"Fetching schema for table: {table}")
        schema_response = query_api("database", f"show create table {table}")

        # Ensure 'reply' exists in the schema response
        if "reply" in schema_response:
            table_schemas[table] = schema_response["reply"]
        else:
            logger.error(f"Unexpected response format for table {table}: {schema_response}")
            raise KeyError(f"Key 'reply' not found in the schema response for table {table}.")

        logger.info(f"Schema for {table}: {table_schemas[table]}")

    logger.info("Table structure fetched successfully.")
    return table_schemas


def generate_sql_query_with_openai(schema_details):
    logger.info("Generating SQL query using OpenAI...")
    prompt = f"""
    You are a SQL expert. Based on the following schema details:
    {schema_details}

    Write an SQL query to find the IDs (DC_ID) of active datacenters managed by users who are inactive (is_active = 0).
    """
    response = openai_client.ask_question(
        question=prompt,
        temperature=0,
    )

    logger.info(f"Received response for question: {response}")

    # Extract SQL query using regex
    match = re.search(r"```sql\n(.*?)```", response, re.S)
    if match:
        sql_query = match.group(1).strip()
        logger.info(f"Extracted SQL query: {sql_query}")
        return sql_query
    else:
        logger.error("Failed to extract SQL query from OpenAI response.")
        raise ValueError("OpenAI response does not contain a valid SQL query.")

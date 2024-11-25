import csv
import os

import requests
from neo4j import GraphDatabase

from env import AIDEVS_API_KEY, S03E03_URL_API_DB
from logger import logger


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


def save_relations_to_csv_file(relations: dict, path):
    directory = os.path.dirname(path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["user1", "user2"])
        writer.writeheader()
        writer.writerows(relations)


class Neo4jHandler:
    def __init__(self, uri, user, password, database="neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        logger.info("Connected to Neo4j (Database: %s)", self.database)

    def close(self):
        self.driver.close()
        logger.info("Connection to Neo4j closed")

    def run_query(self, query, parameters=None):
        with self.driver.session(database=self.database) as session:
            session.run(query, parameters or {})
            logger.info("Executed query on database '%s': %s", self.database, query)

    def ensure_unique_constraints(self):
        """
        Adds a unique constraint to the 'Person' nodes on the 'name' property.
        """
        query = """
        CREATE CONSTRAINT FOR (p:Person) REQUIRE p.name IS UNIQUE;
        """
        try:
            self.run_query(query)
            logger.info("Unique constraint on 'Person.name' ensured.")
        except Exception as e:
            logger.warning("Constraint may already exist or encountered an issue: %s", e)

    def create_person_and_relationship(self, user1, user2):
        query = """
        MERGE (u1:Person {name: $user1})
        MERGE (u2:Person {name: $user2})
        MERGE (u1)-[:KNOWS]->(u2);
        """
        self.run_query(query, {"user1": user1, "user2": user2})
        logger.info("Created relationship: %s KNOWS %s", user1, user2)

    def find_shortest_path(self, start_name, end_name):
        query = """
        MATCH (start:Person {name: $start_name}), (end:Person {name: $end_name})
        MATCH path = shortestPath((start)-[*]-(end))
        RETURN [n IN nodes(path) | n.name] AS path;
        """
        with self.driver.session(database=self.database) as session:
            result = session.run(query, {"start_name": start_name, "end_name": end_name})
            record = result.single()
            if record:
                path = record["path"]
                formatted_path = ", ".join(path)
                logger.info("Shortest path: %s", formatted_path)
                return formatted_path
            else:
                logger.info("No path found between %s and %s", start_name, end_name)
                return None

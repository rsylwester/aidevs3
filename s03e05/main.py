import csv

from aidevs3 import send_answer, Answer
from logger import logger
from s03e05.s03e05_lib import query_api, save_relations_to_csv_file, Neo4jHandler
from utils import is_file_exist

# select relations
SELECT_USERS = '''
    SELECT 
        u1.username AS user1,
        u2.username AS user2
    FROM 
        connections c
    JOIN 
        users u1 ON c.user1_id = u1.id
    JOIN 
        users u2 ON c.user2_id = u2.id;
'''


neo4j_handler = Neo4jHandler("bolt://localhost:7687", "neo4j", "neo4jneo4j")
neo4j_handler.ensure_unique_constraints()


def read_csv_and_import_to_neo4j(csv_path):
    """
    Reads a CSV file and imports the data into Neo4j as nodes and relationships.
    """
    try:
        with open(csv_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                user1 = row["user1"]
                user2 = row["user2"]
                neo4j_handler.create_person_and_relationship(user1, user2)
            logger.info("All data from %s imported into Neo4j", csv_path)
    except Exception as e:
        logger.error("Error reading CSV or importing data: %s", e)


DATA_DIR = './data'
RELATIONS_CSF_FILE = './data/relations.csv'

if not is_file_exist(RELATIONS_CSF_FILE):
    relations: dict = query_api("database", SELECT_USERS)['reply']
    save_relations_to_csv_file(relations, RELATIONS_CSF_FILE)

try:
    read_csv_and_import_to_neo4j(RELATIONS_CSF_FILE)

    path = neo4j_handler.find_shortest_path("Rafał", "Barbara")
    if path:
        print(f"Shortest path: {path}")
    else:
        print("No path found.")

    send_answer(Answer(task="connections", answer=path))

finally:
    neo4j_handler.close()

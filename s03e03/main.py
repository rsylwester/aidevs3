from aidevs3 import send_answer, Answer
from logger import logger
from s03e03.s03e03_lib import fetch_table_structure, generate_sql_query_with_openai, query_api


# Fetch table structure
table_schemas = fetch_table_structure()
schema_details = "\n".join(f"{table}: {details}" for table, details in table_schemas.items())

# Generate and clean SQL query
sql_query = generate_sql_query_with_openai(schema_details)
logger.info(f"Executing generated SQL query: {sql_query}")

# Execute the cleaned SQL query
results = query_api("database", sql_query)["reply"]
logger.info(f"Results obtained: {results}")

# Extract IDs from the query results
dc_ids = [item["dc_id"] for item in results]
logger.info(f"Extracted datacenter IDs: {dc_ids}")

# Send final response using send_answer
send_answer(Answer(task="database", answer=dc_ids))
logger.info(f"Answer sent successfully: {dc_ids}")

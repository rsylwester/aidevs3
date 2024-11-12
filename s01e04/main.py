# SOLUTION 1
"""
Output following result by replacing variables. Output should contain JSON format.

-- context --
UP - 1
RIGHT - 2
DOWN - 3
RIGHT - 4
--------
---- example: ---
input:
{
 "steps": "1, 2, 3"
}
output:
{
 "steps": "UP, RIGHT, DOWN"
}
-----------------

========= replace following ======
{
 "steps": "1, 1, 2, 2, 3, 3, 2,2, 2"
}
"""

# SOLUTION 2 - DRAFT
# openai_client = OpenAIClient(model="gpt-4o-mini")

# BOARD =
# [
# [o,x,o,o,o,o],
# [o,o,o,x,o,o],
# [o,x,o,x,o,o],
# [r,x,o,o,o,g]
# ]
# logger.info(verification_response)

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AIDEVS_API_KEY = os.getenv('AIDEVS_API_KEY')
LLAMA2_CLOUDFLARE_API_URL = os.getenv('LLAMA2_CLOUDFLARE_API_URL')
REPORT_ANSWER_URL = os.getenv('REPORT_ANSWER_URL')

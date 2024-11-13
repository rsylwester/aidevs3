import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AIDEVS_API_KEY = os.getenv('AIDEVS_API_KEY')
LLAMA2_CLOUDFLARE_API_URL = os.getenv('LLAMA2_CLOUDFLARE_API_URL')
REPORT_ANSWER_URL = os.getenv('REPORT_ANSWER_URL')

# lessons data
S01E01_WEBSITE_URL = os.getenv("S01E01_WEBSITE_URL")
S01E01_USERNAME = os.getenv("S01E01_USERNAME")
S01E01_PASSWORD = os.getenv("S01E01_PASSWORD")
S01E02_VERIFY_URL = os.getenv("S01E02_VERIFY_URL")
S01E03_URL_DATA = os.getenv("S01E03_URL_DATA").format(AIDEVS_API_KEY=AIDEVS_API_KEY)
S01E05_URL_DATA = os.getenv("S01E05_URL_DATA").format(AIDEVS_API_KEY=AIDEVS_API_KEY)
S02E01_URL_DATA = os.getenv('S02E01_URL_DATA')
S02E03_URL_DATA = os.getenv('S02E03_URL_DATA').format(AIDEVS_API_KEY=AIDEVS_API_KEY)

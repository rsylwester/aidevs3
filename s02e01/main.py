from pathlib import Path
from typing import List

import download_utils
import utils
from aidevs3 import Answer, send_answer
from env import S02E01_URL_DATA, AIDEVS_API_KEY, OPENAI_API_KEY
from logger import logger
from openai_client import OpenAIClient
from utils import get_tag_value

DATA_DIR = './data'

openai_client = OpenAIClient(model_name="gpt-4o")

system_context = ""

question = """
[Cel Promptu]
Twoim zadaniem jest ustalenie nazwy ulicy, na której znajduje się instytut profesora Maja, na podstawie transkrypcji zeznań świadków, wykorzystując również swoją wewnętrzną wiedzę ogólną. Podaj nazwę ulicy, a także – jeśli to możliwe – nazwę instytutu i miasta, w którym wykłada profesor Maj.

<prompt_objective>
Zidentyfikowanie nazwy ulicy, na której znajduje się instytut profesora Maja, z priorytetowym uwzględnieniem zeznania Rafała i werbalizacją procesu rozwiązywania sprzeczności między zeznaniami.
</prompt_objective>

<prompt_rules>
- PRIORYTETYZUJ: Traktuj zeznanie Rafała jako najbardziej wiarygodne.
- ROZWIĄZUJ SPRZECZNOŚCI: Jeśli zeznania są sprzeczne, analizuj możliwe powody rozbieżności. Przyjmij najbardziej prawdopodobną wersję na podstawie swojej wiedzy i logiki.
- MYŚL NA GŁOS: Przy wyciąganiu wniosków z rozbieżnych zeznań, stosuj metodę „myślenia na głos”, werbalizując kroki analizy i uzasadnienia, które prowadzą do ostatecznego wniosku.
- KORZYSTAJ Z WEWNĘTRZNEJ WIEDZY: Jeśli informacje z transkrypcji nie wystarczają, wykorzystaj swoją wiedzę wewnętrzną, aby podać nazwę ulicy lub instytutu, z którym profesor Maj mógłby być związany.
- OZNACZ NIEPEWNOŚĆ: Jeśli ostateczny wniosek nie jest jednoznaczny, zaznacz poziom pewności wyniku (np. „Z dużym prawdopodobieństwem ulica X”).

</prompt_rules>

<prompt_examples>
USER: Przesłuchanie świadków dotyczące lokalizacji profesora Maja.
AI:
1. Przeanalizuję dostępne zeznania, nadając priorytet relacji Rafała, który jest potwierdzonym kontaktem profesora.
2. Jeśli pojawią się sprzeczności, rozważę możliwość, że niektóre osoby mogą się mylić lub mieć niepełne informacje.
3. Gdy żadna transkrypcja nie zawiera bezpośredniej nazwy ulicy, posłużę się swoją wiedzą na temat lokalizacji uczelni, aby wywnioskować prawdopodobne adresy.

Na podstawie zeznań oraz ogólnej wiedzy sugeruję, że instytut profesora Maja może znajdować się na ulicy [Nazwa Ulicy], w instytucie [Nazwa Instytutu] w [Miasto].
</prompt_examples>

<final_notes>
Na koniec: Jeśli żaden konkretny adres nie wydaje się wyraźnie wynikać z analizy, przedstaw swoją odpowiedź jako przypuszczenie z zaznaczeniem poziomu pewności.

Niech przypuszczalna nazwa ulicy zostanie podana w tagu <street></street> eg. <street>Legnicka</street>

</final_notes>
"""


def transribe_file_and_add_to_system_context(transcription_path: Path) -> str:
    """
    Read transcription file and add to system context with filename as header
    """
    global system_context
    # Get filename without extension as header
    header = transcription_path.stem

    try:
        with open(transcription_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        # Format: Add header and content with clear separation
        section = f"""
        === {header} ===
        {content}
        {'-' * 80}
        """
        system_context += section

    except Exception as e:
        print(f"Error reading {transcription_path}: {str(e)}")

    return system_context


def list_transcription_files(directory: Path) -> list[Path]:
    text_files = list(directory.glob("*.txt"))
    if not text_files:
        raise Exception(f"No text files found in {directory}")
    return text_files


def extract_brackets(text: str) -> str:
    """Extract value from [[text]] format"""
    start = text.find("[[") + 2
    end = text.find("]]")

    if start < 2 or end < 0:
        raise ValueError(f"No [[]] brackets found in text: {text}")

    return text[start:end]


transcription_files = list_transcription_files(Path(DATA_DIR))

# download audio files and transcribe if not yet transcribed
if not transcription_files:
    file_path: str = download_utils.download_file(S02E01_URL_DATA, DATA_DIR)
    audio_files: List[str] = utils.unzip_file(file_path, ['*.mp3', '*.wav', '*.m4a', '*.ogg'])

    for file in audio_files:
        openai_client.transcribe_audio(file)

# create system_context from transcribed files
for file in transcription_files:
    transribe_file_and_add_to_system_context(file)

logger.info(system_context)

model_answer: str = openai_client.ask_question(question=question, system_message=system_context)

logger.info(f"Model's answer: {model_answer}")

logger.info(f"[Sending answer]")

my_answer = Answer(task="MP3", apikey=AIDEVS_API_KEY, answer=get_tag_value(model_answer, "street"))
send_answer(my_answer)


from logger import logger
from openai_client import OpenAIClient
from s04e01.tools import start_conversation
from pydantic import BaseModel


# f"""
# Zdjęcie o nazwie {filename}. Opisz, co przedstawia. Czy zdjęcie jest zbyt ciemne, zbyt jasne lub uszkodzone (z glitchami)? Czy widać tam kobietę? Podaj szczegóły.
# """

class Action(BaseModel):
    action: str
    filename: str
    reason: str

def process_action(action_data):
    """
    Wykonuje operację na zdjęciu na podstawie danych JSON wygenerowanych przez LLM.
    """
    action = action_data.get("action")
    file = action_data.get("file")
    reason = action_data.get("reason", "Brak powodu")

    print(f"Decyzja: {action}, Plik: {file}, Powód: {reason}")

    # Mapowanie akcji na odpowiednie funkcje
    actions_map = {
        "REPAIR": repair,
        "BRIGHTEN": brighten,
        "DARKEN": darken
    }

    if action in actions_map:
        return actions_map[action](file)
    else:
        return {"status": "error", "message": f"Nieznana akcja: {action}"}

start_response = start_conversation()

openai_client = OpenAIClient()


# Parsowanie JSON i przetwarzanie każdej akcji
actions_data = json.loads(llm_output_list)

for action_data in actions_data:
    result = process_action(action_data)
    print("Wynik akcji:", result)

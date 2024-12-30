from typing import List

import numpy as np
import uvicorn
from fastapi import FastAPI

from aidevs3 import send_answer, Answer, send_answer_async
from logger import logger
from openai_client import OpenAIClient
from s04e04.api.entities import ResponseEntity, RequestEntity
from s04e04.llm.inscrutions_response import InstructionLLMResponse, CoordinateShiftLLMResponse

openai_client = OpenAIClient()


def split_instruction(instruction) -> List[str]:
    system_message = """
    Twoim zadaniem jest podzielenie złożonej instrukcji na odrębne kroki, gdzie każdy krok jest pojedynczą akcją do wykonania.

    Przykład:
    Wejściowy tekst:
    "Poleciałem dwa pola w lewo, a później na samą górę."
    Oczekiwany wynik:
    
    Poleciałem dwa pola w lewo
    a później na samą górę
    """

    response: InstructionLLMResponse = openai_client.json_mode(system_message=system_message, prompt=instruction,
                                                               response_format=InstructionLLMResponse)
    return response.instructions


def transform_instruction_to_coordinates_move(instruction):
    system_message = """
    Jesteś programem, który przetwarza polecenia ruchu zapisane w języku naturalnym i zamienia je na przesunięcia współrzędnych kartezjańskich (Δx, Δy) — różnice w położeniu w osi x (poziomej) i y (pionowej).

    Zasady:
    Ruch w prawo:
    
    Jeśli polecenie wspomina o ruchu w prawo, zwiększ Δx o odpowiednią liczbę kroków.
    Jeśli polecenie sugeruje lot do końca w prawo (np. "na sam prawo", "do końca w prawo"), ustaw Δx na maksymalną wartość 3.
    Przykłady fraz:
    "na sam prawo"
    "do końca w prawo"
    "pełny ruch w prawo"
    Przykład: "na sam prawo" → (3, 0).
    Ruch w lewo:
    
    Jeśli polecenie wspomina o ruchu w lewo, zmniejsz Δx o odpowiednią liczbę kroków.
    Jeśli polecenie sugeruje lot do końca w lewo (np. "na sam lewo", "do końca w lewo"), ustaw Δx na maksymalną wartość ujemną -3.
    Przykłady fraz:
    "na sam lewo"
    "do końca w lewo"
    "pełny ruch w lewo"
    Przykład: "na sam lewo" → (-3, 0).
    Ruch w górę:
    
    Jeśli polecenie wspomina o ruchu w górę, zmniejsz Δy o odpowiednią liczbę kroków (ruch w górę to ujemna wartość Δy).
    Jeśli polecenie sugeruje lot do końca w górę (np. "na sam górę", "do końca w górę"), ustaw Δy na maksymalną wartość ujemną -3.
    Przykłady fraz:
    "na sam górę"
    "do końca w górę"
    "pełny ruch w górę"
    Przykład: "na sam górę" → (0, -3).
    Ruch w dół:
    
    Jeśli polecenie wspomina o ruchu w dół, zwiększ Δy o odpowiednią liczbę kroków.
    Jeśli polecenie sugeruje lot do końca w dół (np. "na sam dół", "do końca w dół"), ustaw Δy na maksymalną wartość 3.
    Przykłady fraz:
    "na sam dół"
    "do końca w dół"
    Przykład: "a później na sam dół" → (0, 3).
    Liczba kroków:
    
    Wyodrębnij liczbę kroków z tekstu (np. "jedno" oznacza 1, "dwa" oznacza 2). Jeśli liczba kroków nie jest określona, załóż, że ruch dotyczy jednej jednostki.
    Dane wejściowe:
    Instrukcja w języku naturalnym opisująca ruch (np. "poleciałem jedno pole w prawo", "do końca w dół").
    
    Dane wyjściowe:
    Krotka (Δx, Δy) reprezentująca przesunięcie w układzie współrzędnych.
    
    Przykłady danych wejściowych i wyjściowych:
    Dane wejściowe: "poleciałem jedno pole w prawo"
    Dane wyjściowe: (1, 0)
    Dane wejściowe: "na sam prawo"
    Dane wyjściowe: (3, 0)
    Dane wejściowe: "a później na sam dół"
    Dane wyjściowe: (0, 3)
    Dane wejściowe: "na sam lewo"
    Dane wyjściowe: (-3, 0)
    Dane wejściowe: "na sam górę"
    Dane wyjściowe: (0, -3)
    """

    response: CoordinateShiftLLMResponse = openai_client.json_mode(system_message=system_message, prompt=instruction,
                                                                   response_format=CoordinateShiftLLMResponse)

    return response.shift


def transform_instructions_to_moves(instructions) -> List[List[int]]:
    moves = []
    for instruction in instructions:
        move = transform_instruction_to_coordinates_move(instruction)
        moves.append(move)
    return moves


map_4x4 = np.array([
    ["start", "łąka", "drzewo", "dom"],
    ["łąka", "wiatrak", "łąka", "łąka"],
    ["łąka", "łąka", "skały", "dwa drzewa"],
    ["skały", "skały", "samochód", "jaskinia"]
], dtype=object)


def get_terrain(moves: List[List[int]]) -> str:
    current_position = [0, 0]

    for move in moves:
        # Update row and column while constraining to valid bounds
        current_position[0] = max(0, min(current_position[0] + move[0], map_4x4.shape[0] - 1))
        current_position[1] = max(0, min(current_position[1] + move[1], map_4x4.shape[1] - 1))

    return map_4x4[current_position[1], current_position[0]]


def normalize_instruction(instruction: str):
    prompt = """
        Given a text with multiple instructions, focus only on navigation-related commands and remove any unrelated, redundant, or indecisive statements. Normalize the output to retain the final clear instruction. Here are examples:
        
        Example 1
        Input:
        Idziemy na sam dół mapy. Albo nie! nie! nie idziemy. Zaczynamy od nowa. W prawo maksymalnie idziemy. Co my tam mamy?
        Output:
        W prawo maksymalnie idziemy
        
        Example 2
        Input:
        Dobra. To co? zaczynamy? Odpalam silniki. Czas na kolejny lot. Jesteś moimi oczami. Lecimy w dół, albo nie! nie! czekaaaaj. Polecimy wiem jak. W prawo i dopiero teraz w dół. Tak będzie OK. Co widzisz?
        Output:
        W prawo i dopiero teraz w dół 
     """

    normalized = openai_client.ask_question(question=instruction, system_message=prompt)

    logger.info(f"Normalizing: \n{instruction} ---> {normalized}")
    return normalized


app = FastAPI()


@app.post("/api", response_model=ResponseEntity)
def process_request(request: RequestEntity):
    logger.info(f"[Request] {request}")

    normalized_instruction = normalize_instruction(request.instruction)
    instructions: List[str] = split_instruction(normalized_instruction)
    moves = transform_instructions_to_moves(instructions)
    terrain: str = get_terrain(moves)

    logger.info(f"[Response] {terrain}")

    return ResponseEntity(description=terrain)


@app.get("/send")
def send_api_url():
    logger.info("send api url")
    answer = send_answer(Answer(task="webhook", answer="https://azyl-52263.ag3nts.org/api"))
    logger.info(answer)


if __name__ == "__main__":
    logger.info(f"Click to send API URL: http://127.0.0.1:3000/send")
    uvicorn.run("main:app", host="127.0.0.1", port=3000, reload=True)

from logger import logger
from openai_client import OpenAIClient

text_enrich_prompt = """
For each provided page of text, generate a concise list of keywords in Polish that emphasize factual information, specific names, entities, and concrete concepts mentioned in the text. Ensure the following:
	•	Include “Rafał” as a keyword on every page.
	•	Avoid including emotions or subjective states.
	•	Keywords should reflect tangible, factual elements to aid in efficient similarity searches in a vector database.

Example Output:

Strona 1

Tekst:
Nie powinienem był tego robić. Obsługa skomplikowanego sprzętu, niekoniecznie będąc trzeźwym, to nie był dobry pomysł. I ta pizza w ręce. Źle się czuję. Nie wiem, jak bardzo będę tego żałował. Może po prostu prześpię się i wszystko wróci do normy. Z jednej strony wiedziałem, czego się spodziewać i wiedziałem, że ta maszyna może przenosić w czasie, a z drugiej strony do dziś dnia nie mogę uwierzyć, że jestem w 20… roku. To nienormalne!

Słowa kluczowe:
Rafał, maszyna, podróże w czasie, sprzęt, przyszłość, rok 20…, pizza

Strona 2

Tekst:
Jestem normalny. To wszystko dzieje się naprawdę. Jestem normalny. To jest rzeczywistość. Jestem normalny. Wiem, gdzie jestem i kim jestem. Jestem normalny. To wszystko w koło. To jest normalne. Jestem normalny. Mam na imię Rafał. Jestem normalny. Świat jest nienormalny.

Słowa kluczowe:
Rafał, rzeczywistość, świat

Strona 3

Tekst:
Spotkałem Azazela, a przynajmniej tak się przedstawił ten człowiek. Twierdzi, że jest z przyszłości. Opowiadał mi o dziwnych rzeczach. Nie wierzę mu. Nikt przede mną nie cofnął się w czasie! Ale on wiedział o wszystkim, nad czym pracowałem z profesorem Majem. Dałem mu badania, które zabrałem z laboratorium.

Słowa kluczowe:
Rafał, Azazel, przyszłość, profesor Maj, badania, laboratorium, podróże w czasie
"""

def generate_keywords_for_text(text):
    openai_client = OpenAIClient(model_name="gpt-4o")
    llm_response = openai_client.ask_question(question=str(text), system_message=text_enrich_prompt, temperature=0.8)

    logger.info(f"\nEnrich text: \n>{text}\n>{llm_response}\n\n")
    return llm_response
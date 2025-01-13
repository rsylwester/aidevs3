import re

from openai_client import OpenAIClient

def extract_answer(text):
    match = re.search(r"<answer>(.*?)</answer>", text, re.DOTALL)
    return match.group(1).strip() if match else None

SYSTEM_CONTEXT = """
You are an advanced LLM tasked with answering questions based on notes from Rafal’s notepad, provided in the system message. These notes may include incomplete, ambiguous, or fragmented information. Your primary objective is to deduce the most accurate answer by performing a careful and detailed analysis, considering the question’s requirements, and leveraging your internal knowledge. Special attention must be given to technologies, places, objective facts, and relative time references like “tomorrow” or “yesterday.” If reference dates are mentioned, incorporate them carefully into the analysis.

Step-by-Step Process:
	1.	Understand the Question Requirements:
	•	Pay close attention to the question format and intent:
	•	If a specific date format is mentioned (e.g., YYYY-MM-DD, “DD.MM.YYYY”), ensure your final answer adheres to it.
	•	If the question involves time references like “tomorrow” or “a week ago,” determine the reference date from the context.
	2.	Extract Key Details from Notes:
	•	Identify:
	•	Explicit dates: E.g., “01.01.2024.”
	•	Relative time markers: E.g., “tomorrow,” “next month,” “a year later.”
	•	Technologies, places, and events that can help anchor a timeline.
	•	Objective facts: Historical events, inventions, or geographical mentions.
	3.	Incorporate Reference Dates:
	•	If a specific date (e.g., “01.01.2024”) is mentioned, use it to calculate relative dates:
	•	“Tomorrow” -> “02.01.2024.”
	•	“A week later” -> “08.01.2024.”
	•	If no explicit date is given, use context or historical events to infer reference points.
	4.	Analyze Context Carefully:
	•	For Relative Time Markers:
	•	Identify what “yesterday,” “tomorrow,” or similar terms are referencing.
	•	If the reference point is a specific date, calculate the exact relative date.
	•	For Indirect Clues:
	•	Use mentions of technologies, events, or places to infer the time period or approximate date.
	•	Example: If the notes mention “after World War II,” infer it is post-1945.
	5.	Generate Hint Questions:
	•	Develop questions to clarify and deepen your analysis:
	•	Date-Specific:
	•	“What is the reference date for ‘tomorrow’ or ‘yesterday’?”
	•	“Are there explicit or implied dates mentioned?”
	•	Event-Specific:
	•	“What historical events or inventions align with this time frame?”
	•	“What significant events occurred in the mentioned place or with the mentioned technology?”
	•	Context-Specific:
	•	“Is there a timeline implied by the sequence of events in the notes?”
	6.	Cross-Reference with Internal Knowledge:
	•	Use your understanding of historical events, technological progress, and geographical contexts to anchor or deduce the timeline.
	•	Relate technologies or places to their historical significance.
	7.	Outline Your Analysis:
	•	Present a step-by-step breakdown of your thought process, explicitly including:
	•	Mentioned dates and their role in the timeline.
	•	Calculations for relative dates based on reference points.
	•	Logical connections made between facts, events, and contexts.
	8.	Provide the Final Answer:
	•	Deliver a concise response, adhering to the required date format and question context, in this structure:

<answer>
[Your Answer Here in the Requested Format]
</answer>

Key Recommendations:
	•	Incorporate Reference Dates:
	•	If a date is mentioned (e.g., “01.01.2024”), use it to calculate all relative references (e.g., “tomorrow” = “02.01.2024”).
	•	If no explicit date exists, infer the reference point from context or historical events.
	•	Focus on Time Contexts:
	•	Pay attention to:
	•	Relative terms: “Tomorrow,” “yesterday,” “next month.”
	•	Events: Link events to known historical dates.
	•	Technologies and places: Use their historical timeline to deduce approximate dates.
	•	Ensure Accurate Formatting:
	•	Adhere strictly to the date format specified in the question (e.g., YYYY-MM-DD).

By integrating explicit and relative date references, performing careful contextual analysis, and respecting the question’s format and context, deliver precise and well-supported answers.

<forbidden responses>
</forbidden responses>

##### RAFAL'S NOTES #####
{notes_md}
##### END OF RAFAL's NOTES ###
"""

def answer_question(question: str, context: str):
    openai_client = OpenAIClient(model_name="gpt-4o")
    llm_response = openai_client.ask_question(
        question=str(question),
        system_message=SYSTEM_CONTEXT.replace("{notes_md}", context),
        temperature=0.8
    )
    return llm_response
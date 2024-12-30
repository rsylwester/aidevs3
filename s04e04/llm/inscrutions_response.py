from typing import List, Tuple

from pydantic import BaseModel, Field


class InstructionLLMResponse(BaseModel):
    instructions: List[str] = Field(None, description="Lista odrębnych instrukcji")

class CoordinateShiftLLMResponse(BaseModel):
    shift: List[int] = Field(None, description="Przesunięcie koordynatów")
from pydantic import BaseModel

class RequestEntity(BaseModel):
    instruction: str

class ResponseEntity(BaseModel):
    description: str
from pydantic import BaseModel

class PhishingRequest(BaseModel):
    text: str

class PhishingResponse(BaseModel):
    input: str
    is_phishing: bool
    confidence: float
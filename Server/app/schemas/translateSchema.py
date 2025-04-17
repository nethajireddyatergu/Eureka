from pydantic import BaseModel, HttpUrl

class TranscriptionRequest(BaseModel):
    sourceLang: str
    targetLang: str
    audio_url: HttpUrl

class TranscriptionResponse(BaseModel):
    path: str

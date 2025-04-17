from fastapi import APIRouter, HTTPException
from app.utils.downloader import download_audio
from app.schemas.translateSchema import TranscriptionRequest, TranscriptionResponse
from app.utils.translate import SpeechTranslate
router = APIRouter(prefix="/transcribe", tags=["Transcription"])

@router.post("/", response_model=TranscriptionResponse)
async def transcribe_audio_file(request: TranscriptionRequest):
    try:
        sourceLang = request.sourceLang
        targetLang = request.targetLang
        audio_url = request.audio_url

        # Step 1: Download audio file
        audio_path = download_audio(audio_url)
        
        # Step 2: Transcribe speech to speech
        translator = SpeechTranslate(source_lang=sourceLang, target_lang=targetLang)
        output = translator.translate_audio(audio_path)
        
        return TranscriptionResponse(path=output)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

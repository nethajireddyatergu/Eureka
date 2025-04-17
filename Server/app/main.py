from fastapi import FastAPI
from app.routes import translateRoutes

app = FastAPI(
    title="Video Transcription API",
    description="API to transcribe audio from videos hosted on Cloudinary",
    version="1.0.0",
)

# Include routers
app.include_router(translateRoutes.router)

# Root route
@app.get("/")
def read_root():
    return {"message": "Welcome to the Video Transcription API!"}

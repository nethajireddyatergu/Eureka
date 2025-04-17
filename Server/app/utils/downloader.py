import requests

def download_audio(audio_url: str) -> str:
    # Specify the local file name for saving the WAV file
    local_audio_wav = "temp_audio.wav"
    
    # Step 1: Download the audio file
    response = requests.get(audio_url, stream=True)
    if response.status_code == 200:
        with open(local_audio_wav, "wb") as audio_file:
            for chunk in response.iter_content(chunk_size=1024):
                audio_file.write(chunk)
        return local_audio_wav
    else:
        raise Exception("Failed to download audio file.")

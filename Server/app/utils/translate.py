import os
from google.cloud import texttospeech
import speech_recognition as sr
from google.cloud import speech
from google.cloud import translate_v2 as translate
from pydub import AudioSegment 

# Set up Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./app/api_token.json"  # Replace with your API key path

class SpeechTranslate:
    def __init__(self, source_lang='en', target_lang='te'):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.recognizer = sr.Recognizer()
        self.tts_client = texttospeech.TextToSpeechClient()
        self.translate_client = translate.Client()

    def recognize_speech(self, audio_file):
        # Convert audio to mono
        audio_segment = AudioSegment.from_wav(audio_file)
        mono_audio_file = "mono_audio.wav"
        audio_segment = audio_segment.set_channels(1)
        audio_segment.export(mono_audio_file, format="wav")

        client = speech.SpeechClient()
        
        with open(mono_audio_file, "rb") as audio_file:
            content = audio_file.read()

        audio = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=48000,
            language_code="en-US",
            enable_word_time_offsets=True
        )
        
        response = client.recognize(config=config, audio=audio)
        
        recognized_text = ""
        timestamps = []
        for result in response.results:
            recognized_text += result.alternatives[0].transcript + " "
            for word_info in result.alternatives[0].words:
                timestamps.append((word_info.word, word_info.start_time.total_seconds(), word_info.end_time.total_seconds()))

        return recognized_text.strip(), timestamps

    def translate_text(self, text):
        result = self.translate_client.translate(text, source_language=self.source_lang, target_language=self.target_lang)
        translated_text = result['translatedText']
        return translated_text

    def text_to_speech_with_ssml(self, translated_text, timestamps, lang_code='te-IN'):
        ssml = "<speak>"
        last_end_time = 0 
        current_index = 0

        translated_words = translated_text.split() 

        # Generate Telugu timestamps with corresponding words
        telugu_timestamps = []  
        for i, (word, start, end) in enumerate(timestamps):
            pause_duration = start - last_end_time
            if pause_duration > 0: 
                ssml += f"<break time='{pause_duration:.2f}s'/>" 

            if current_index < len(translated_words):
                ssml += f"<s>{translated_words[current_index]}</s>"
                telugu_timestamps.append((translated_words[current_index], start, end)) 
                current_index += 1 

            last_end_time = end

        ssml += "</speak>"

        print("Generated SSML:", ssml)
        print("Telugu Timestamps:", telugu_timestamps)  # Print Telugu timestamps

        synthesis_input = texttospeech.SynthesisInput(ssml=ssml)
        voice = texttospeech.VoiceSelectionParams(
            language_code=lang_code,
            name="te-IN-Standard-D", 
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        try:
            response = self.tts_client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

            if response.audio_content:
                with open("telugu_output.mp3", "wb") as out:
                    out.write(response.audio_content)
                print("Telugu audio content written to telugu_output.mp3")
                return "telugu_output.mp3"
            else:
                print("No audio content received from the API.")
        except Exception as e:
            print(f"An error occurred during synthesis: {e}")

    def translate_audio(self, audio_file):
        recognized_text, timestamps = self.recognize_speech(audio_file)

        print("Recognized Text:", recognized_text)
        print("Timestamps:", timestamps)

        edit_choice = input(f"Do you want to edit the transcript? (yes/no): ").strip().lower()
        
        if edit_choice == 'yes':
            with open("transcript.txt", "w", encoding='utf-8') as f:
                f.write(recognized_text)
            print("Transcript written to transcript.txt. Please edit the file and save it.")
            os.startfile("transcript.txt")
            input("Press Enter after you have finished editing the transcript...")
            with open("transcript.txt", "r", encoding='utf-8') as f:
                recognized_text = f.read()

        # Translate the text to Telugu
        translated_text = self.translate_text(recognized_text) 

        edit_choice_telugu = input(f"Do you want to edit the Telugu translation? (yes/no): ").strip().lower()
        
        if edit_choice_telugu == 'yes':
            with open("translated_transcript.txt", "w", encoding='utf-8') as f:
                f.write(translated_text)  # Write only the translated text
            print("Translated transcript written to translated_transcript.txt. Please edit the file and save it.")
            os.startfile("translated_transcript.txt")
            input("Press Enter after you have finished editing the translated transcript...")
            with open("translated_transcript.txt", "r", encoding='utf-8') as f:
                translated_text = f.read().splitlines()[0]  # Read only the first line

        # Generate Telugu audio from the translated text with timestamps
        return self.text_to_speech_with_ssml(translated_text, timestamps, lang_code='te-IN') 


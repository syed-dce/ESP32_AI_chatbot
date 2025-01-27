import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
# import openai

recognizer = sr.Recognizer()

def record_audio(timeout=3, phrase_time_limit=50, retries=3):
    for attempt in range(retries):
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Recording started. Speak now...")
                audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                print("Recording complete")
                return audio_data
        except sr.WaitTimeoutError:
            print(f"Listening timed out, retrying... ({attempt + 1}/{retries})")
    return None

def transcribe_audio(audio_data_bytes):
    try:
        print("Processing speech...")
        # Wrap bytes in a file-like object
        audio_file = BytesIO(audio_data_bytes)

        # Use AudioFile to read it properly
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        return text
    except Exception as e:
        print(f"Transcription error: {e}")
        return "Error in transcribing audio"

# def transcribe_audio_with_whisper(audio_bytes: bytes) -> str:
#     audio_file = BytesIO(audio_bytes)
#     audio_file.name = "input.mp3"  # whisper needs a filename with extension
    
#     response = openai.Audio.transcribe(
#         model="whisper-1",
#         file=audio_file,
#     )
#     return response["text"]

#testing
if __name__=="__main__":
    audio = record_audio()
    print(transcribe_audio(audio))
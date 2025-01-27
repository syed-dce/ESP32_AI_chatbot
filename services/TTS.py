import pyttsx3
from gtts import gTTS
from io import BytesIO

engine = pyttsx3.init()
engine.setProperty('rate', 150)
def speak(text):
    engine.say(text)
    engine.runAndWait()

def synthesize_audio(text: str) -> bytes:
    tts = gTTS(text)
    buffer = BytesIO()
    tts.write_to_fp(buffer)
    return buffer.getvalue()

def save_mp3_file(audio_bytes: bytes, filename: str):
    with open(filename, "wb") as f:
        f.write(audio_bytes)

#testing
if __name__ =="__main__":
    speak("hello how are you doing?")
    audio_bytes  = synthesize_audio("Do you know what my name is?")
    save_mp3_file(audio_bytes, "test3.mp3") 
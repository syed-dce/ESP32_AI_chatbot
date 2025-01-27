import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import requests
import os
from tempfile import NamedTemporaryFile

# Recording settings
SAMPLE_RATE = 16000  # Match server's expected rate
CHANNELS = 1
DURATION = 5  # seconds

def record_audio_to_wav(file_path, duration=DURATION):
    print("Recording started. Speak now...")
    recording = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16')
    sd.wait()  # Wait until recording is done
    print("Recording complete")
    wav.write(file_path, SAMPLE_RATE, recording)

def send_audio_to_server(file_path, url="http://localhost:8000/convert", output_file="response.wav"):
    with open(file_path, 'rb') as f:
        files = {'audio': (os.path.basename(file_path), f, 'audio/wav')}
        response = requests.post(url, files=files)
        if response.status_code == 200:
            with open(output_file, 'wb') as out_f:
                out_f.write(response.content)
            print(f"✅ Response audio saved as {output_file}")
        else:
            print(f"❌ Server returned an error: {response.status_code} - {response.text}")

def main():
    with NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
        temp_path = temp_wav.name

    try:
        record_audio_to_wav(temp_path)
        send_audio_to_server(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    main()

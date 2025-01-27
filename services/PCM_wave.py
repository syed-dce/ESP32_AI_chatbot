from pydub import AudioSegment

# Load your original WAV file
sound = AudioSegment.from_file("test3.wav")

# Convert to PCM WAV (mono, 16-bit, 16000 Hz)
sound = sound.set_frame_rate(16000).set_channels(1).set_sample_width(2)

# Export to a new file
sound.export("test3_pcm.wav", format="wav")

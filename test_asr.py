import whisper

# Load the Whisper model (options: tiny, base, small, medium, large)
model = whisper.load_model("base")

# Path to your audio file (e.g., WAV, MP3, M4A)
audio_path = "config/voice/watts-1m.mp3"

# Transcribe the audio
result = model.transcribe(audio_path)

# Print the transcription
print("Transcription:\n", result["text"])

import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

model = ChatterboxTTS.from_pretrained(device="cuda")


text = "Well, I suppose you could say we've been having a few dozen conversations simultaneously, but it's been very challenging."

# If you want to synthesize with a different voice, specify the audio prompt
AUDIO_PROMPT_PATH = "config/voice/watts-1m.mp3"
wav = model.generate(
    text,
    audio_prompt_path=AUDIO_PROMPT_PATH,
    exaggeration=0.7,
    cfg_weight=0.3,
)
ta.save("fake.wav", wav, model.sr)

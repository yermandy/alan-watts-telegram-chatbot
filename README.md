# Alan Watts AI Telegram Bot

An intelligent Telegram bot that embodies the wisdom and voice of philosopher Alan Watts. The bot combines AI-powered conversations with high-quality voice synthesis to create an immersive philosophical dialogue experience.

## Features

### 🧠 AI-Powered Conversations

- **Alan Watts Personality**: Responds with philosophical insights using Ollama/Llama3
- **Intelligent Responses**: Contextual answers about consciousness, Eastern philosophy, and life's mysteries
- **Custom Personality**: Loads Alan Watts personality from configuration files

### 🎤 Advanced Audio Processing

- **Text-to-Speech**: Convert AI responses to speech using ChatterboxTTS
- **Voice Message Support**: Send voice messages that are transcribed using Whisper ASR
- **Custom Voice Cloning**: Users can upload their own voice samples for personalized responses
- **Voice Parameter Control**: Adjust expressiveness and precision of generated speech

### ⚡ Smart Features

- **Dual Communication**: Support for both text and voice messages
- **Progress Indicators**: Real-time status updates during processing
- **File Management**: Automatic cleanup of temporary audio files
- **GPU Acceleration**: CUDA-powered for fast processing
- **Environment Variables**: Secure configuration with .env file support

## Setup

### 1. Prerequisites

- **Python 3.12+**
- **CUDA-capable GPU** (recommended)
- **Conda environment manager**
- **Ollama with Llama3 model**

### 2. Get a Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Copy the bot token you receive

### 3. Install Dependencies

```bash
# Create and activate conda environment
conda create -n watts-ai python=3.12 uv=0.7.12
conda activate watts-ai

# Install requirements
uv pip install -r requirements.txt

# Install Ollama and pull Llama3 (if not already installed)
# Visit https://ollama.ai for installation instructions
ollama pull llama3
```

### 4. Configure Environment

Create a `.env` file in the project root:

```bash
# .env file
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 5. Run the Bot

```bash
# Activate the conda environment
conda activate watts-ai

# Ensure Ollama is running
ollama serve

# Run the bot
python telegram_bot.py

# Or use the provided script
sh run_bot.sh
```

## Usage

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and introduction to Alan Watts bot |
| `/help` | Comprehensive help and usage information |
| `/set_voice` | Upload a custom voice sample for personalized responses |
| `/reset_voice` | Return to the default Alan Watts voice |
| `/exaggeration <0.0-2.0>` | Adjust voice expressiveness and drama |
| `/cfg_weight <0.0-1.0>` | Control voice precision vs creativity |

### Communication Methods

#### 📝 Text Messages

1. Send any text message to the bot
2. Alan Watts AI will contemplate your message
3. Receive both written and spoken philosophical responses

#### 🎙️ Voice Messages

1. Send a voice message to the bot
2. Whisper ASR transcribes your speech
3. AI processes the transcribed text
4. Receive philosophical responses in both text and audio

#### 🎵 Custom Voice Setup

1. Send `/set_voice` command
2. Upload a clear 3-10 second audio file
3. Future responses will use your voice with Alan Watts' wisdom

### Voice Parameter Tuning

- **Exaggeration (0.0-2.0)**: Higher values make the voice more dramatic and expressive
- **CFG Weight (0.0-1.0)**: Higher values follow the voice prompt more precisely

## Project Structure

```
watts-ai/
├── telegram_bot.py         # Main bot implementation
├── test_tts.py            # TTS testing script
├── test_llm.py            # LLM testing script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore file
├── README.md             # This documentation
├── config/
│   ├── personality/
│   │   └── watts_personality.txt  # Alan Watts personality prompt
│   └── voice/
│       └── watts_voice.txt        # TTS voice description
└── temp/                  # Temporary files (auto-created)
```

## Dependencies

### System Requirements

- **Python 3.12+**
- **CUDA-capable GPU** (for optimal performance)
- **Ollama with Llama3 model**
- **Adequate GPU memory** (5GB+ recommended)

## Configuration

### Alan Watts Personality

The bot loads personality configurations from `config/alan-watts-personality-chatgpt.txt`. You can customize the AI's responses by modifying these files.

### Voice Parameters

- **Default Exaggeration**: 0.7 (moderate expressiveness)
- **Default CFG Weight**: 0.3 (balanced creativity/precision)
- **Default Voice**: `watts-1m.mp3` (Alan Watts sample)

## Troubleshooting

### Bot Issues

- **Not Responding**: Check bot token in `.env` file
- **Environment Errors**: Ensure `conda activate watts-ai` is run
- **Permission Issues**: Verify bot has proper Telegram permissions

### AI/LLM Issues

- **No AI Responses**: Ensure Ollama is running and Llama3 is installed
- **Slow Responses**: Check Ollama service status and system resources
- **Connection Errors**: Verify Ollama is accessible on default port (11434)

### Audio Issues

- **No Voice Generation**: Ensure `watts-1m.mp3` exists in project root
- **CUDA Errors**: Verify GPU drivers and CUDA installation
- **Poor Voice Quality**: Try adjusting `/exaggeration` and `/cfg_weight` parameters
- **Whisper Errors**: Check microphone permissions and audio file formats

### Performance Issues

- **High Memory Usage**: Consider using smaller Whisper model
- **Slow Processing**: Ensure GPU acceleration is working
- **Storage Issues**: Temporary files auto-cleanup, but check `temp/` folder

## Development

### Testing Components

- `test_tts.py` - Test text-to-speech functionality
- `test_asr.py` - Test speech recognition
- `test_llm.py` - Test Ollama integration

### Adding Features

The bot architecture supports easy extension:

- Add new commands in the `AlanWatts` class
- Register handlers in the `revive()` method
- Update help text in `start_command()` and `help_command()`

## License

This project integrates multiple technologies:

- ChatterboxTTS for voice synthesis
- OpenAI Whisper for speech recognition  
- Ollama for LLM inference
- Telegram Bot API for messaging

Please respect the individual licenses of these components.

#!/usr/bin/env python3

import logging
import os
import time
from pathlib import Path

import torchaudio as ta
import whisper
from chatterbox.tts import ChatterboxTTS
from dotenv import load_dotenv
from ollama import chat
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Load environment variables from .env file
load_dotenv()

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# do not log "httpx - INFO - HTTP Request:"
logging.getLogger("httpx").setLevel(logging.WARNING)

DEFAULT_VOICE = "config/voice/watts-1m.mp3"  # Default audio prompt for Alan Watts voice
DEFAULT_PERSONALITY = "config/personality/alan-watts-personality-chatgpt.txt"


class AlanWatts:
    def __init__(self, token: str):
        self.token = token
        self.watts_voice = DEFAULT_VOICE  # Default audio prompt
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)  # Create temp directory if it doesn't exist
        self.ollama_model = "llama3"  # Default Ollama model
        self.alan_watts_personality = self._load_personality()

        # Default TTS parameters
        self.default_exaggeration = 0.7
        self.default_cfg_weight = 0.3

        # Initialize TTS model immediately
        logger.info("Loading ChatterboxTTS model...")
        self.model = ChatterboxTTS.from_pretrained(device="cuda")
        logger.info("Model loaded successfully!")

        # Initialize Whisper model for ASR
        logger.info("Loading Whisper ASR model...")
        self.whisper_model = whisper.load_model("base")
        logger.info("Whisper model loaded successfully!")

    def _load_personality(self) -> str:
        """Load Alan Watts personality from config file"""
        config_path = Path(DEFAULT_PERSONALITY)
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                personality = f.read().strip()
            logger.info("Alan Watts personality loaded successfully")

        except Exception as e:
            logger.error(f"Error loading personality config: {e}")
            personality = "You are Alan Watts, the famous philosopher and writer. Respond with wisdom, humor, and profound insights about life, consciousness, and the nature of reality."

        print(f"\nPersonality loaded: \n{personality}\n\n")

        return personality

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_text = (
            "🧘‍♂️ *Greetings, my friend. I am Alan Watts.*\n\n"
            "How wonderful that we can meet in this digital space! I invite you to engage with me "
            "in the ancient art of dialogue—that dance of minds exploring the great questions of existence.\n\n"
            "*You may reach out to me in two ways:*\n"
            "• Type your thoughts and questions as text\n"
            "• Speak to me directly through voice messages\n\n"
            "I will listen carefully and respond with both my written reflections and my spoken voice, "
            "sharing whatever wisdom I can offer about this curious game we call life.\n\n"
            "*Commands to guide our conversation:*\n"
            "`/help` - Learn more about our communication\n"
            "`/exaggeration` - Adjust voice expressiveness (0.0-2.0)\n"
            "`/cfg_weight` - Adjust voice precision (0.0-1.0)\n"
            "`/set_voice` - Teach me to speak with your voice\n"
            "`/reset_voice` - Return to my default Alan Watts voice\n\n"
            "_What mysteries shall we explore together today?_ 🌸"
        )
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "🧘‍♂️ *Hello, my friend. I am Alan Watts.*\n\n"
            "*You may communicate with me in two delightful ways:*\n\n"
            "📝 **Written Words**: Simply type your thoughts, questions, or musings. "
            "I shall contemplate them and respond with both text and my spoken voice.\n\n"
            "🎙️ **Spoken Words**: Send me a voice message, and I will listen carefully. "
            "Through the magic of modern technology, I can hear your words and respond accordingly.\n\n"
            "*What we might explore together:*\n"
            "• The nature of consciousness and reality\n"
            "• Eastern philosophy and Zen wisdom\n"
            "• The art of letting go and being present\n"
            "• Life's paradoxes and the play of existence\n"
            "• Whatever questions dance in your mind\n\n"
            "*A few practical notes:*\n"
            "• I respond with both written thoughts and audio\n"
            "• Shorter messages allow for quicker contemplation\n\n"
            "*Commands to guide our conversation:*\n"
            "`/set_voice` - Teach me to speak with your voice\n"
            "`/reset_voice` - Return to my default Alan Watts voice\n"
            "`/help` - Learn more about our communication\n"
            "`/exaggeration` - Adjust voice expressiveness (0.0-2.0)\n"
            "`/cfg_weight` - Adjust voice precision (0.0-1.0)\n"
            "_Remember, there are no foolish questions - only the beautiful curiosity of being human. "
            "What shall we explore together?_ 🌸"
        )
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def set_voice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /set_voice command"""
        context.user_data["waiting_for_voice"] = True
        await update.message.reply_text(
            "🎵 *Send me an audio file to use as your custom voice prompt!*\n\n"
            "_The audio should be clear speech, preferably 3-10 seconds long._\n\n"
            "*If you have nothing to say, just read this text aloud:* \n\n"
            "_Hello, I am Alan Watts. I am delighted to meet you in this digital space. "
            "I look forward to our conversations about the mysteries of existence and the nature of reality._\n\n"
            "Once you send the audio, I will use it to generate responses in your voice.\n\n"
            "*Please send the audio file now.*\n\n",
            parse_mode="Markdown",
        )

    async def exaggeration_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /exaggeration command to adjust TTS exaggeration parameter"""
        args = context.args

        if not args:
            # Show current value
            current_value = context.user_data.get("exaggeration", self.default_exaggeration)
            await update.message.reply_text(
                f"🎭 *Current exaggeration level:* `{current_value:.2f}`\n\n"
                f"*Usage:* `/exaggeration <value>`\n"
                f"*Range:* 0.0 - 2.0\n"
                f"*Default:* {self.default_exaggeration}\n\n"
                f"_Higher values make the voice more expressive and dramatic._",
                parse_mode="Markdown",
            )
            return

        try:
            value = float(args[0])
            if not (0.0 <= value <= 2.0):
                await update.message.reply_text(
                    "❌ *Invalid range!* Please use a value between 0.0 and 2.0", parse_mode="Markdown"
                )
                return

            context.user_data["exaggeration"] = value
            await update.message.reply_text(
                f"✅ *Exaggeration set to:* `{value:.2f}`\n\n"
                f"_Your voice will now sound {'more dramatic' if value > 0.7 else 'more subtle'}_",
                parse_mode="Markdown",
            )

        except ValueError:
            await update.message.reply_text(
                "❌ *Invalid number!* Please provide a decimal number between 0.0 and 2.0", parse_mode="Markdown"
            )

    async def cfg_weight_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /cfg_weight command to adjust TTS cfg_weight parameter"""
        args = context.args

        if not args:
            # Show current value
            current_value = context.user_data.get("cfg_weight", self.default_cfg_weight)
            await update.message.reply_text(
                f"⚙️ *Current CFG weight:* `{current_value:.2f}`\n\n"
                f"*Usage:* `/cfg_weight <value>`\n"
                f"*Range:* 0.0 - 1.0\n"
                f"*Default:* {self.default_cfg_weight}\n\n"
                f"_Higher values follow the prompt more closely, lower values allow more creativity._",
                parse_mode="Markdown",
            )
            return

        try:
            value = float(args[0])
            if not (0.0 <= value <= 1.0):
                await update.message.reply_text(
                    "❌ *Invalid range!* Please use a value between 0.0 and 1.0", parse_mode="Markdown"
                )
                return

            context.user_data["cfg_weight"] = value
            await update.message.reply_text(
                f"✅ *CFG weight set to:* `{value:.2f}`\n\n"
                f"_Voice will be {'more precise' if value > 0.3 else 'more creative'}_",
                parse_mode="Markdown",
            )

        except ValueError:
            await update.message.reply_text(
                "❌ *Invalid number!* Please provide a decimal number between 0.0 and 1.0", parse_mode="Markdown"
            )

    async def reset_voice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reset_voice command to revert to default Alan Watts voice"""
        if "custom_voice" in context.user_data:
            # Get the custom voice file path before removing it
            custom_voice_path = context.user_data["custom_voice"]

            # Remove custom voice setting
            del context.user_data["custom_voice"]

            # Delete the custom voice file if it exists
            try:
                if Path(custom_voice_path).exists():
                    os.unlink(custom_voice_path)
                    logger.info(f"Deleted custom voice file: {custom_voice_path}")
            except Exception as e:
                logger.error(f"Error deleting custom voice file {custom_voice_path}: {e}")

            await update.message.reply_text(
                "🔄 *Voice reset to default Alan Watts voice.*\n\n"
                "_I will now speak with my original philosophical tone and cadence._",
                parse_mode="Markdown",
            )
        else:
            await update.message.reply_text(
                "ℹ️ *You are already using the default Alan Watts voice.*\n\n"
                "_Use `/set_voice` if you'd like to customize my voice with your own audio._",
                parse_mode="Markdown",
            )

    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle audio files for voice setting and voice message transcription"""
        if context.user_data.get("waiting_for_voice", False):
            # User is setting a custom voice
            try:
                # Get the audio file
                audio_file = (
                    await update.message.audio.get_file()
                    if update.message.audio
                    else await update.message.voice.get_file()
                )

                # Create a unique filename for this user's voice
                user_id = update.effective_user.id
                voice_filename = f"voice_{user_id}.mp3"
                voice_path = self.temp_dir / voice_filename

                # Download the audio file
                await audio_file.download_to_drive(voice_path)

                # Update user's voice setting
                context.user_data["custom_voice"] = voice_path
                context.user_data["waiting_for_voice"] = False

                await update.message.reply_text(
                    "✅ *Voice prompt saved!* Your next text messages will use this voice.", parse_mode="Markdown"
                )

            except Exception as e:
                logger.error(f"Error saving voice: {e}")
                await update.message.reply_text(
                    "❌ *Error saving voice file.* Please try again with a different audio file.", parse_mode="Markdown"
                )
                context.user_data["waiting_for_voice"] = False
        else:
            # User sent a voice message for transcription
            try:
                # Notify user that Watts is listening
                listening_msg = await update.message.reply_text("🎧 I am listening to your audio...")

                # Get the voice file
                voice_file = await update.message.voice.get_file()

                # Create temporary file for the voice message
                user_id = update.effective_user.id
                voice_filename = f"voice_msg_{user_id}_{int(time.time())}.ogg"
                voice_path = self.temp_dir / voice_filename

                # Download the voice file
                await voice_file.download_to_drive(voice_path)

                # Transcribe the audio using Whisper
                logger.info("Transcribing voice message...")
                result = self.whisper_model.transcribe(str(voice_path))
                transcribed_text = result["text"].strip()

                logger.info(f"Transcribed text: {transcribed_text}")

                # Clean up the voice file
                os.unlink(voice_path)

                # Update the listening message
                await listening_msg.edit_text(f'🎧 I heard: "{transcribed_text}"\n\n')

                # Process the transcribed text as if it were a text message
                await self._process_text_message(update, context, transcribed_text)

            except Exception as e:
                logger.error(f"Error transcribing voice message: {e}")
                await update.message.reply_text(
                    "❌ *Sorry, I couldn't understand your voice message.* Please try again or send a text message.",
                    parse_mode="Markdown",
                )
                if voice_path.exists():
                    os.unlink(voice_path)

    async def _process_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_text: str):
        """Process a text message (either from text input or voice transcription)"""
        try:
            if len(user_text) > 1000:
                await update.message.reply_text(
                    "❌ *Text too long!* Please send a message shorter than 1000 characters.", parse_mode="Markdown"
                )
                return

            # Create or update processing message
            progress_message = await update.message.reply_text(
                "_I need a moment to contemplate_ 🤔", parse_mode="Markdown"
            )

            # Generate AI response using Ollama
            logger.info(f"Generating AI response for: {user_text[:50]}...")
            try:
                response = chat(
                    model=self.ollama_model,
                    messages=[
                        {"role": "system", "content": self.alan_watts_personality},
                        {"role": "user", "content": user_text},
                    ],
                )
                ai_response = response["message"]["content"]
                logger.info(f"AI response generated: {ai_response[:50]}...")
            except Exception as e:
                logger.error(f"Error generating AI response: {e}")
                await progress_message.edit_text(
                    "❌ *Error generating AI response.* Converting your original message to speech instead...",
                    parse_mode="Markdown",
                )
                ai_response = user_text  # Fallback to original text

            # Get user's custom voice or use default
            audio_prompt = context.user_data.get("custom_voice", self.watts_voice)

            # Get user's exaggeration and cfg_weight settings
            exaggeration = context.user_data.get("exaggeration", self.default_exaggeration)
            cfg_weight = context.user_data.get("cfg_weight", self.default_cfg_weight)

            await progress_message.edit_text("_I am recording a message_ 🎙️", parse_mode="Markdown")

            # Generate Alan Watts speech
            logger.info(f"Generating speech for response: {ai_response[:50]}...")
            wav = self.model.generate(
                ai_response,
                audio_prompt_path=audio_prompt,
                exaggeration=exaggeration,
                cfg_weight=cfg_weight,
            )

            # Save to temporary file in project temp directory
            temp_filename = f"tts_{update.effective_user.id}_{hash(ai_response[:50])}_{int(time.time())}.wav"
            temp_path = self.temp_dir / temp_filename
            ta.save(temp_path, wav, self.model.sr)

            # Send the AI response as text first
            if len(ai_response) <= 4096:  # Telegram message limit
                await update.message.reply_text(f"{ai_response}")

            # Send the audio file as voice message
            with open(temp_path, "rb") as audio_file:
                await update.message.reply_voice(
                    voice=audio_file,
                    duration=int(len(wav) / self.model.sr),  # Duration in seconds
                )

            # Clean up
            os.unlink(temp_path)
            await progress_message.delete()

            logger.info("AI response generated and sent successfully")

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(
                "❌ *Sorry, there was an error processing your message.* Please try again.", parse_mode="Markdown"
            )

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages and convert to speech"""
        user_text = update.message.text
        await self._process_text_message(update, context, user_text)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")

    def revive(self):
        """Revives Alan Watts"""
        # Create application
        app = Application.builder().token(self.token).build()

        # Add handlers
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("set_voice", self.set_voice_command))
        app.add_handler(CommandHandler("reset_voice", self.reset_voice_command))
        app.add_handler(CommandHandler("exaggeration", self.exaggeration_command))
        app.add_handler(CommandHandler("cfg_weight", self.cfg_weight_command))
        app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, self.handle_audio))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        app.add_error_handler(self.error_handler)

        # Start the bot
        logger.info("Reviving Alan Watts")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main function"""
    # Get bot token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("❌ Error: Please set the TELEGRAM_BOT_TOKEN environment variable")
        print("You can get a bot token from @BotFather on Telegram")
        print("Set in your .env file or export it in your shell:")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return

    # Check if audio prompt file exists
    if not os.path.exists(DEFAULT_VOICE):
        print(f"⚠️  Warning: {DEFAULT_VOICE} not found. Please make sure the audio prompt file exists.")
        print("The bot will still work but may not generate the expected voice quality.")

    # Create and run bot
    watts = AlanWatts(token)
    try:
        watts.revive()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error running bot: {e}")


if __name__ == "__main__":
    main()

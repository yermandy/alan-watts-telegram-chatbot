#!/bin/bash

# Telegram TTS Bot Setup Script

echo "🤖 Telegram TTS Bot Setup"
echo "=========================="

# Check if conda environment is active
if [[ "$CONDA_DEFAULT_ENV" != "watts-ai" ]]; then
    echo "⚠️  Please activate the watts-ai conda environment first:"
    echo "conda activate watts-ai"
    exit 1
fi

# Check if bot token is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo ""
    echo "❌ TELEGRAM_BOT_TOKEN not found!"
    echo ""
    echo "To get a bot token:"
    echo "1. Open Telegram and search for @BotFather"
    echo "2. Send /newbot and follow the instructions"
    echo "3. Copy the token you receive"
    echo ""
    echo "Then set the token by running:"
    echo "export TELEGRAM_BOT_TOKEN='your_bot_token_here'"
    echo ""
    echo "Or create a .env file with:"
    echo "echo 'export TELEGRAM_BOT_TOKEN=\"your_bot_token_here\"' > .env"
    echo "source .env"
    echo ""
    exit 1
fi

echo "✅ Environment looks good!"
echo "🚀 Starting Telegram TTS Bot..."
echo "Press Ctrl+C to stop the bot"
echo ""

# Run the bot
python telegram_bot.py

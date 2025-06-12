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

# Check if .env file exists and contains TELEGRAM_BOT_TOKEN
if [ ! -f ".env" ] || ! grep -q "TELEGRAM_BOT_TOKEN" ".env"; then
    echo ""
    echo "❌ .env file with TELEGRAM_BOT_TOKEN not found!"
    echo ""
    echo "To get a bot token:"
    echo "1. Open Telegram and search for @BotFather"
    echo "2. Send /newbot and follow the instructions"
    echo "3. Copy the token you receive"
    echo ""
    echo "Then create a .env file with:"
    echo "echo 'TELEGRAM_BOT_TOKEN=\"your_bot_token_here\"' > .env"
    echo ""
    echo "Or set as environment variable:"
    echo "export TELEGRAM_BOT_TOKEN='your_bot_token_here'"
    echo ""
    exit 1
fi

echo "✅ Environment looks good!"
echo "🚀 Starting Telegram TTS Bot..."
echo "Press Ctrl+C to stop the bot"
echo ""

# Run the bot
python telegram_bot.py

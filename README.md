# Telegram Channel Cloner

An improved Telegram channel cloning tool with comprehensive error handling, logging, configuration management, and resume functionality.

## Features

- **Complete Message Cloning**: Clone text messages, media files, and mixed content
- **Error Handling & Recovery**: Robust error handling with automatic retry mechanisms
- **Rate Limiting**: Built-in rate limiting to respect Telegram API limits
- **Progress Tracking**: Resume interrupted transfers from where they left off
- **Comprehensive Logging**: Detailed logging with both file and console output
- **Configuration Management**: Environment-based configuration for security
- **Batch Processing**: Process messages in configurable batches
- **Dry Run Mode**: Preview what will be cloned without actually sending messages
- **Command-Line Interface**: Easy-to-use CLI with multiple options

## Installation

1. Clone or download this project
2. Install required Python packages:
   ```bash
   pip install telethon python-dotenv
   ```

3. Set up your Telegram API credentials:
   - Go to https://my.telegram.org/auth
   - Create a new application to get your `api_id` and `api_hash`
   - Copy `.env.example` to `.env` and fill in your credentials

## Configuration

Copy `.env.example` to `.env` and configure the following:

```env
# Required - Get from https://my.telegram.org/auth
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here

# Optional - Customize as needed
TELEGRAM_SESSION_NAME=telegram_cloner
RATE_LIMIT_DELAY=1.0
BATCH_SIZE=10
MAX_RETRIES=3
RETRY_DELAY=5.0
LOG_FILE=telegram_cloner.log
LOG_LEVEL=INFO
PROGRESS_FILE=clone_progress.json
SAVE_PROGRESS_INTERVAL=50
DOWNLOAD_MEDIA=true
MEDIA_TIMEOUT=300

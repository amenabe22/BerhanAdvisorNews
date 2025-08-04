# Credentials Directory

This directory is for storing sensitive credentials and API keys. **Never commit these files to git!**

## Files to add here:

### Google Cloud Service Account Key
- **File:** `travel-buddy-b8e9e-25cab73cdc59.json` (or your own service account key)
- **Purpose:** Google Cloud Storage access
- **How to get:** 
  1. Go to Google Cloud Console
  2. Navigate to IAM & Admin > Service Accounts
  3. Create or select a service account
  4. Create a new key (JSON format)
  5. Download and place here

### Other credentials you might need:
- `resend-api-key.txt` - For email service
- `telegram-bot-token.txt` - For Telegram bot
- `openai-api-key.txt` - For AI services

## Security Notes:
- ✅ This directory is in `.gitignore`
- ✅ Never commit these files
- ✅ Keep backups in a secure location
- ✅ Rotate keys regularly
- ✅ Use environment variables in production

## Environment Variables:
Make sure your `.env` file points to the correct credential files:

```bash
# Google Cloud Storage
GCS_CREDENTIALS_FILE=credentials/travel-buddy-b8e9e-25cab73cdc59.json

# Email Service
RESEND_API_KEY=your_resend_api_key_here

# Other services
TELEGRAM_BOT_TOKEN=your_telegram_token_here
``` 
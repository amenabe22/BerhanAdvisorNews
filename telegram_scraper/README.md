# Telegram News Scraper

A professional, modular Telegram scraper for Ethiopian news channels. This tool scrapes the latest posts from configured Telegram channels, downloads images, and stores everything in a structured database.

## Features

- 🔍 **Multi-channel scraping** from Ethiopian Telegram channels
- 📸 **Image processing** with automatic download and GCS upload
- 🗄️ **Structured database** with SQLAlchemy ORM
- 📊 **Rich CLI interface** with progress tracking and statistics
- 🔄 **Deduplication** to avoid duplicate posts
- 📝 **Comprehensive logging** with file and console output
- ⚡ **Rate limiting** to respect Telegram API limits
- 🎯 **Modular architecture** for easy maintenance and extension

## Supported Channels

- **Shega Media** (@shegamediaet) - Tech & Startup news
- **Tikvah Ethiopia** (@tikvahethiopia) - General news
- **Addis Reporter** (@Addis_Reporter) - News
- **ESAT** (@Esat_tv1) - News
- **Fana Media Corporation** (@fanatelevision) - News
- **Addis Neger** (@Addis_News) - News

## Installation

1. **Clone the repository:**
   ```bash
   cd telegram_scraper
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## Configuration

### Required Environment Variables

Create a `.env` file with the following variables:

```env
# Telegram API Credentials
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number

# Database
DATABASE_URL=sqlite:///./telegram_news.db

# Google Cloud Storage (Optional)
GCS_BUCKET_NAME=telegram-news-images
GCS_CREDENTIALS_PATH=path/to/credentials.json

# Logging
LOG_LEVEL=INFO
```

### Getting Telegram API Credentials

1. Go to https://my.telegram.org/
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Copy the `api_id` and `api_hash`

## Usage

### Initialize Database

```bash
python main.py init
```

### Scrape All Channels

```bash
python main.py scrape
```

### Scrape Specific Channels

```bash
python main.py scrape --channel shegamediaet --channel tikvahethiopia
```

### Scrape with Custom Settings

```bash
python main.py scrape --posts 20 --concurrent 5
```

### Check Status

```bash
python main.py status
```

### List Configured Channels

```bash
python main.py channels
```

### Show Configuration

```bash
python main.py config
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `init` | Initialize database tables |
| `scrape` | Scrape posts from channels |
| `status` | Show scraping statistics |
| `channels` | List configured channels |
| `config` | Show current configuration |

### Scrape Options

- `--channel, -c`: Specific channels to scrape
- `--posts, -p`: Number of posts per channel (default: 10)
- `--concurrent, -n`: Concurrent channel scrapes (default: 3)

## Database Schema

### Tables

- **telegram_channels**: Channel information
- **telegram_posts**: Post data with content and metadata
- **scraping_logs**: Scraping activity logs

### Key Fields

- `telegram_id`: Unique Telegram message ID
- `content_hash`: Hash for deduplication
- `gcs_image_url`: Google Cloud Storage image URL
- `moderation_status`: Post moderation status

## Architecture

```
telegram_scraper/
├── src/
│   ├── config/          # Configuration settings
│   ├── core/            # Database and core functionality
│   ├── models/          # Database models
│   ├── scrapers/        # Telegram scraping logic
│   └── utils/           # Utilities (logging, image processing)
├── data/                # Database files
├── logs/                # Log files
├── images/              # Temporary image storage
├── main.py              # CLI entry point
└── requirements.txt     # Dependencies
```

## Features in Detail

### Image Processing

- Downloads images from Telegram posts
- Processes and optimizes images with PIL
- Uploads to Google Cloud Storage
- Automatic cleanup of local files

### Deduplication

- Content-based deduplication using SHA256 hashes
- Title-based similarity detection
- Configurable similarity thresholds

### Rate Limiting

- Respects Telegram API rate limits
- Configurable delays between requests
- Automatic retry on rate limit errors

### Logging

- Structured logging with loguru
- File rotation and compression
- Console output with colors
- Comprehensive error tracking

## Development

### Adding New Channels

Edit `src/config/settings.py` and add to `TELEGRAM_CHANNELS`:

```python
TelegramChannel(
    name="New Channel",
    username="newchannel",
    url="https://t.me/newchannel",
    category="news",
    language="en",
    max_posts=10
)
```

### Extending Functionality

The modular architecture makes it easy to extend:

- Add new scrapers in `src/scrapers/`
- Extend models in `src/models/`
- Add utilities in `src/utils/`

## Troubleshooting

### Common Issues

1. **Telegram API errors**: Check your API credentials
2. **Private channels**: Some channels may be private
3. **Rate limiting**: Increase delays in configuration
4. **GCS upload failures**: Check credentials and bucket permissions

### Debug Mode

Set log level to DEBUG:

```bash
export LOG_LEVEL=DEBUG
python main.py scrape
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub. 
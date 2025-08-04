# Telegram Scraper API Documentation

A comprehensive REST API for the Telegram news scraper with full CRUD operations, filtering, and scraping capabilities.

## 🚀 Quick Start

### Start the API Server

```bash
# Install dependencies
pip3 install -r requirements.txt

# Start the API server
python3 api.py
```

The API will be available at:
- **Base URL**: `http://localhost:8000`
- **API Documentation**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/api/v1/health`

## 📋 API Endpoints

### Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-05T00:30:00"
}
```

### Statistics
```http
GET /api/v1/statistics
```

**Response:**
```json
{
  "total_channels": 6,
  "total_posts": 48,
  "total_logs": 12,
  "posts_by_category": {
    "news": 25,
    "tech_startup": 15,
    "general": 8
  },
  "posts_by_language": {
    "en": 20,
    "am": 28
  },
  "recent_activity": {
    "posts_last_7_days": 15,
    "logs_last_7_days": 8
  }
}
```

### Channels

#### Get All Channels
```http
GET /api/v1/channels
```

#### Get Channel by ID
```http
GET /api/v1/channels/{channel_id}
```

#### Get Channel by Username
```http
GET /api/v1/channels/username/{username}
```

**Response:**
```json
{
  "id": 1,
  "name": "Shega Media",
  "username": "shegamediaet",
  "url": "https://t.me/shegamediaet",
  "category": "tech_startup",
  "language": "en",
  "is_active": true,
  "last_scraped": "2025-08-05T00:25:00",
  "created_at": "2025-08-05T00:20:00",
  "updated_at": "2025-08-05T00:25:00"
}
```

### Posts

#### Get Posts with Pagination and Filtering
```http
GET /api/v1/posts?page=1&size=20&category=news&language=en&has_media=true
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `size` (int): Page size, max 100 (default: 20)
- `channel_id` (int): Filter by channel ID
- `category` (string): Filter by category
- `language` (string): Filter by language
- `moderation_status` (string): Filter by moderation status
- `has_media` (boolean): Filter by media presence
- `search` (string): Search in title, content, and excerpt
- `date_from` (datetime): Filter by date from
- `date_to` (datetime): Filter by date to

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "telegram_id": 2079,
      "title": "Ethiopian Youth Ride TikTok's Reach",
      "content": "Full post content...",
      "excerpt": "In a tightening job market...",
      "url": null,
      "image_url": null,
      "gcs_image_url": "https://storage.googleapis.com/bucket/telegram_images/photo.jpg",
      "published_date": "2025-08-04T14:53:21",
      "scraped_date": "2025-08-05T00:25:00",
      "channel_id": 1,
      "category": "tech_startup",
      "language": "en",
      "is_duplicate": false,
      "similarity_score": null,
      "views": 721,
      "forwards": 6,
      "replies": null,
      "has_media": true,
      "media_type": "photo",
      "moderation_status": "PENDING",
      "channel": {
        "id": 1,
        "name": "Shega Media",
        "username": "shegamediaet",
        "url": "https://t.me/shegamediaet",
        "category": "tech_startup",
        "language": "en",
        "is_active": true,
        "last_scraped": "2025-08-05T00:25:00",
        "created_at": "2025-08-05T00:20:00",
        "updated_at": "2025-08-05T00:25:00"
      }
    }
  ],
  "total": 48,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

#### Get Post by ID
```http
GET /api/v1/posts/{post_id}
```

#### Get Recent Posts
```http
GET /api/v1/posts/recent/{limit}
```

### Scraping

#### Scrape Channels
```http
POST /api/v1/scrape
```

**Request Body:**
```json
{
  "channels": ["shegamediaet", "tikvahethiopia"],
  "posts_per_channel": 10,
  "force": false
}
```

**Response:**
```json
[
  {
    "channel_name": "Shega Media",
    "posts_found": 10,
    "posts_new": 2,
    "posts_duplicate": 8,
    "images_downloaded": 2,
    "error": null,
    "status": "success"
  },
  {
    "channel_name": "Tikvah Ethiopia",
    "posts_found": 10,
    "posts_new": 5,
    "posts_duplicate": 5,
    "images_downloaded": 3,
    "error": null,
    "status": "success"
  }
]
```

### Logs

#### Get Scraping Logs
```http
GET /api/v1/logs?page=1&size=20
```

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "channel_id": 1,
      "status": "success",
      "posts_found": 10,
      "posts_new": 2,
      "posts_duplicate": 8,
      "images_downloaded": 2,
      "error_message": null,
      "duration": 15.5,
      "created_at": "2025-08-05T00:25:00",
      "channel": {
        "id": 1,
        "name": "Shega Media",
        "username": "shegamediaet",
        "url": "https://t.me/shegamediaet",
        "category": "tech_startup",
        "language": "en",
        "is_active": true,
        "last_scraped": "2025-08-05T00:25:00",
        "created_at": "2025-08-05T00:20:00",
        "updated_at": "2025-08-05T00:25:00"
      }
    }
  ],
  "total": 12,
  "page": 1,
  "size": 20,
  "pages": 1
}
```

## 🔍 Advanced Filtering Examples

### Search Posts by Text
```http
GET /api/v1/posts?search=ethiopia&size=10
```

### Filter by Date Range
```http
GET /api/v1/posts?date_from=2025-08-01T00:00:00&date_to=2025-08-05T23:59:59
```

### Filter by Category and Language
```http
GET /api/v1/posts?category=news&language=am&has_media=true
```

### Get Posts with Media Only
```http
GET /api/v1/posts?has_media=true&size=20
```

## 🛠️ Usage Examples

### Python Client Example

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api/v1"

# Get statistics
response = requests.get(f"{BASE_URL}/statistics")
stats = response.json()
print(f"Total posts: {stats['total_posts']}")

# Get recent posts
response = requests.get(f"{BASE_URL}/posts/recent/5")
posts = response.json()
for post in posts:
    print(f"- {post['title']}")

# Scrape channels
payload = {
    "channels": ["shegamediaet"],
    "posts_per_channel": 10,
    "force": False
}
response = requests.post(f"{BASE_URL}/scrape", json=payload)
results = response.json()
for result in results:
    print(f"{result['channel_name']}: {result['posts_new']} new posts")
```

### cURL Examples

```bash
# Get all channels
curl http://localhost:8000/api/v1/channels

# Get posts with filtering
curl "http://localhost:8000/api/v1/posts?category=news&size=10"

# Scrape channels
curl -X POST http://localhost:8000/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{"channels": ["shegamediaet"], "posts_per_channel": 5}'

# Search posts
curl "http://localhost:8000/api/v1/posts?search=ethiopia&size=20"
```

### JavaScript/Fetch Example

```javascript
// Get statistics
const response = await fetch('http://localhost:8000/api/v1/statistics');
const stats = await response.json();
console.log(`Total posts: ${stats.total_posts}`);

// Scrape channels
const scrapeResponse = await fetch('http://localhost:8000/api/v1/scrape', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    channels: ['shegamediaet'],
    posts_per_channel: 10,
    force: false
  })
});
const results = await scrapeResponse.json();
results.forEach(result => {
  console.log(`${result.channel_name}: ${result.posts_new} new posts`);
});
```

## 🔧 Configuration

### Environment Variables

```env
# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Database
DATABASE_URL=sqlite:///./telegram_news.db

# Telegram API
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number

# Logging
LOG_LEVEL=INFO
```

## 📊 Response Formats

### Pagination
All list endpoints return paginated responses with:
- `items`: Array of results
- `total`: Total number of items
- `page`: Current page number
- `size`: Page size
- `pages`: Total number of pages

### Error Responses
```json
{
  "detail": "Error message"
}
```

### Success Responses
All successful responses include the requested data in a structured format with proper typing.

## 🚀 Deployment

### Development
```bash
python3 api.py
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "api.py"]
```

## 🔒 Security

- CORS is enabled for development (configure appropriately for production)
- Input validation on all endpoints
- SQL injection protection via SQLAlchemy
- Rate limiting can be added via middleware

## 📈 Monitoring

- Health check endpoint for monitoring
- Comprehensive logging
- Error tracking and reporting
- Performance metrics available

## 🎯 Features

- ✅ **RESTful API**: Clean, consistent endpoints
- ✅ **Pagination**: Efficient data retrieval
- ✅ **Filtering**: Advanced search and filter capabilities
- ✅ **Real-time Scraping**: Trigger scraping via API
- ✅ **Statistics**: Comprehensive analytics
- ✅ **Documentation**: Auto-generated OpenAPI docs
- ✅ **Type Safety**: Full Pydantic model validation
- ✅ **Error Handling**: Comprehensive error responses
- ✅ **CORS Support**: Cross-origin requests
- ✅ **Health Monitoring**: System status endpoints 
# n8n Workflow Popularity Tracker

A production-ready system that identifies the most popular n8n workflows across multiple platforms (YouTube, n8n Forum, Google Trends) and exposes results via a REST API with the exact JSON schema format you specified.

## Features

- **Multi-Platform Data Collection**: Collects data from YouTube, n8n Forum, and Google Trends
- **Popularity Scoring**: Advanced algorithms to calculate workflow popularity across platforms
- **REST API**: FastAPI-based API with comprehensive endpoints
- **Real-time Analysis**: Background data collection and processing
- **Database Storage**: SQLite database for persistent data storage
- **Configurable**: Environment-based configuration for API keys and settings

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   YouTube API   │    │  n8n Forum API  │    │ Google Trends   │
│                 │    │                 │    │                 │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Collectors                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   YouTube   │  │   Forum     │  │   Trends    │            │
│  │  Collector  │  │  Collector  │  │  Collector  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQLite Database                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  YouTube    │  │   Forum     │  │   Trends    │            │
│  │   Videos    │  │   Posts     │  │    Data     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                Popularity Analyzer                              │
│              (Scoring & Analysis)                               │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI REST API                             │
│              (Endpoints & Documentation)                        │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.11+
- YouTube Data API v3 key
- n8n Forum API key (optional)

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd assignment
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   ```bash
   cp env_example.txt .env
   ```

   Edit `.env` file with your API keys:

   ```env
   YOUTUBE_API_KEY=your_youtube_api_key_here
   N8N_FORUM_API_KEY=your_n8n_forum_api_key_here
   N8N_FORUM_BASE_URL=https://community.n8n.io
   DATABASE_URL=sqlite:///./workflow_data.db
   DEBUG=True
   LOG_LEVEL=INFO
   ```

4. **Run the application**

   ```bash
   python main.py
   ```

   Or using uvicorn directly:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Run the Streamlit frontend** (optional)

   ```bash
   # Basic frontend
   python run_streamlit.py --app basic

   # Advanced frontend with more features
   python run_streamlit.py --app advanced

   # Or run directly with streamlit
   streamlit run streamlit_app.py
   ```

## API Documentation

Once the server is running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **Streamlit Frontend**: http://localhost:8501

## Data Schema (JSON Format)

Each workflow follows this exact JSON format:

```json
{
  "workflow": "Google Sheets → Slack Automation",
  "platform": "YouTube",
  "popularity_metrics": {
    "views": 12500,
    "likes": 630,
    "comments": 88,
    "like_to_view_ratio": 0.05,
    "comment_to_view_ratio": 0.007
  },
  "country": "US",
  "last_updated": "2025-09-04"
}
```

## Main API Endpoints

### Core Workflow Endpoints

#### Get All Workflows

```http
GET /workflows
```

Returns all workflows from all platforms in the specified JSON format.

#### Get Workflows by Platform

```http
GET /workflows/{platform}
```

Filter workflows by platform. Supported platforms:

- `YouTube` or `yt`
- `Forum` or `discourse`
- `Google` or `trends` or `google trends`

#### Get Top N Workflows

```http
GET /workflows/top/{n}
```

Returns top N workflows ranked by engagement score.

#### Get Workflow Statistics

```http
GET /workflows/stats
```

Returns summary statistics about workflows.

### Data Collection Endpoints

#### Collect YouTube Data

```http
POST /collect/youtube?max_results=50
```

#### Collect Forum Data

```http
POST /collect/forum?max_results=100
```

#### Collect Trends Data

```http
POST /collect/trends
```

#### Collect All Data

```http
POST /collect/all?youtube_max=50&forum_max=100
```

### Additional Endpoints

#### Get Popular YouTube Videos

```http
GET /youtube/popular?limit=10
```

#### Get High Engagement YouTube Videos

```http
GET /youtube/engagement?limit=10
```

#### Get Popular Forum Posts

```http
GET /forum/popular?limit=10
```

#### Get High Engagement Forum Posts

```http
GET /forum/engagement?limit=10
```

#### Get Forum Categories

```http
GET /forum/categories
```

#### Get Trending Queries

```http
GET /trends/popular?limit=10
```

#### Get Country Trends

```http
GET /trends/countries
```

#### Get Recent Trends

```http
GET /trends/recent?days=30
```

#### Get Trend Analysis

```http
GET /trends/analysis/{query}
```

#### Get Platform Summary

```http
GET /summary
```

## Data Models

### YouTube Video

- `video_id`: Unique YouTube video identifier
- `title`: Video title
- `channel_title`: Channel name
- `view_count`: Number of views
- `like_count`: Number of likes
- `comment_count`: Number of comments
- `like_to_view_ratio`: Engagement ratio (likes/views)
- `comment_to_view_ratio`: Comment engagement ratio
- `search_query`: Query used to find the video

### Forum Post

- `post_id`: Unique forum post identifier
- `title`: Post title
- `author`: Post author
- `category`: Forum category
- `reply_count`: Number of replies
- `like_count`: Number of likes
- `view_count`: Number of views
- `unique_contributors`: Number of unique contributors

### Trend Data

- `query`: Search query
- `country`: Country code (US, IN, etc.)
- `interest_score`: Google Trends interest score
- `date`: Date of the trend data

## Popularity Scoring Algorithm

The system uses a weighted scoring algorithm to calculate workflow popularity:

```python
popularity_score = (
    youtube_score * 0.3 +
    youtube_engagement * 0.2 +
    forum_activity * 0.2 +
    trends_interest * 0.3
)
```

### YouTube Scoring

- **Views Score**: Normalized view count (capped at 100M views)
- **Engagement Score**: Average of like-to-view and comment-to-view ratios

### Forum Scoring

- **Views Score**: Normalized view count (capped at 10K views)
- **Activity Score**: Combined replies and likes (capped at 100 interactions)

### Trends Scoring

- **Interest Score**: Average of mean and peak interest scores from Google Trends

## Streamlit Frontend

The system includes a beautiful Streamlit frontend for interactive data visualization and analysis.

### Features

- **📊 Interactive Dashboard**: Real-time workflow statistics and metrics
- **📈 Data Visualization**: Charts, graphs, and trend analysis
- **🔄 Data Collection**: Trigger data updates directly from the UI
- **📤 Export Options**: Download data in CSV, JSON, and Excel formats
- **🎯 Platform Filtering**: Filter workflows by platform (YouTube, Forum, Google)
- **⚡ Auto-refresh**: Automatic data updates every 30 seconds
- **💾 Caching**: Smart caching for better performance
- **📱 Responsive Design**: Works on desktop and mobile devices

### Running the Frontend

#### Basic Frontend

```bash
python run_streamlit.py --app basic
# or
streamlit run streamlit_app.py
```

#### Advanced Frontend

```bash
python run_streamlit.py --app advanced
# or
streamlit run streamlit_advanced.py
```

#### Custom Configuration

```bash
# Run on different port
python run_streamlit.py --port 8502

# Run on different host
python run_streamlit.py --host 0.0.0.0
```

### Frontend Screenshots

The Streamlit frontend provides:

1. **Main Dashboard**: Overview of all workflows with statistics
2. **Platform Filtering**: Filter by YouTube, Forum, or Google Trends
3. **Top Workflows**: Ranked list of most popular workflows
4. **Engagement Metrics**: Visual analysis of views, likes, and comments
5. **Trends Analysis**: Historical trend data and country analysis
6. **Export Options**: Download data in multiple formats

### Frontend Architecture

```
Streamlit App
├── Main Dashboard (streamlit_app.py)
│   ├── Statistics Cards
│   ├── Top Workflows List
│   ├── Platform Distribution Charts
│   └── Engagement Metrics
├── Advanced Dashboard (streamlit_advanced.py)
│   ├── Caching System
│   ├── Trends Analysis
│   ├── Forum Analysis
│   ├── Workflow Comparison
│   ├── Insights Generation
│   └── Export Options
└── API Integration
    ├── REST API Calls
    ├── Error Handling
    └── Data Transformation
```

## Usage Examples

### 1. Get All Workflows (Main Endpoint)

```bash
curl -X GET "http://localhost:8000/workflows"
```

**Response:**

```json
[
  {
    "workflow": "Google Sheets → Slack Automation",
    "platform": "YouTube",
    "popularity_metrics": {
      "views": 12500,
      "likes": 630,
      "comments": 88,
      "like_to_view_ratio": 0.05,
      "comment_to_view_ratio": 0.007
    },
    "country": "US",
    "last_updated": "2025-01-04"
  }
]
```

### 2. Get Workflows by Platform

```bash
# Get YouTube workflows
curl -X GET "http://localhost:8000/workflows/YouTube"

# Get Forum workflows
curl -X GET "http://localhost:8000/workflows/Forum"

# Get Google Trends workflows
curl -X GET "http://localhost:8000/workflows/Google"
```

### 3. Get Top N Workflows

```bash
# Get top 10 workflows by engagement
curl -X GET "http://localhost:8000/workflows/top/10"

# Get top 5 workflows
curl -X GET "http://localhost:8000/workflows/top/5"
```

### 4. Get Workflow Statistics

```bash
curl -X GET "http://localhost:8000/workflows/stats"
```

**Response:**

```json
{
  "total_workflows": 60,
  "youtube_workflows": 20,
  "forum_workflows": 20,
  "trends_workflows": 20,
  "platforms": ["YouTube", "Forum", "Google"],
  "last_updated": "2025-01-04"
}
```

### 5. Collect Data from All Platforms

```bash
curl -X POST "http://localhost:8000/collect/all?youtube_max=50&forum_max=100"
```

### 6. Generate Sample Data

```bash
python generate_sample_data.py
```

### 7. Update Data (Automation)

```bash
python update_data.py --youtube-max 50 --forum-max 100
```

## Configuration

### Environment Variables

| Variable                 | Description                    | Default                                                   |
| ------------------------ | ------------------------------ | --------------------------------------------------------- |
| `YOUTUBE_API_KEY`        | YouTube Data API v3 key        | Required                                                  |
| `N8N_FORUM_API_KEY`      | n8n Forum API key              | Optional                                                  |
| `N8N_FORUM_BASE_URL`     | n8n Forum base URL             | `https://community.n8n.io`                                |
| `DATABASE_URL`           | Database connection string     | `sqlite:///./workflow_data.db`                            |
| `DEBUG`                  | Enable debug mode              | `True`                                                    |
| `LOG_LEVEL`              | Logging level                  | `INFO`                                                    |
| `YOUTUBE_SEARCH_QUERIES` | Comma-separated search queries | `n8n workflow,n8n automation,n8n integration`             |
| `TRENDS_QUERIES`         | Comma-separated trend queries  | `n8n Slack integration,n8n Gmail automation,n8n workflow` |
| `TRENDS_COUNTRIES`       | Comma-separated country codes  | `US,IN`                                                   |

## Development

### Project Structure

```
assignment/
├── main.py                 # FastAPI application
├── config.py              # Configuration management
├── database.py            # Database setup
├── models.py              # SQLAlchemy models
├── requirements.txt       # Python dependencies
├── env_example.txt        # Environment variables template
├── README.md             # This file
├── setup.py              # Setup script
├── run.py                # Run script
├── test_api.py           # Test script
├── streamlit_app.py      # Basic Streamlit frontend
├── streamlit_advanced.py # Advanced Streamlit frontend
├── run_streamlit.py      # Streamlit launcher script
├── update_data.py        # Data update automation script
├── generate_sample_data.py # Sample data generator
├── crontab_example.txt   # Cron job examples
├── .github/workflows/    # GitHub Actions
│   └── update-data.yml
├── collectors/           # Data collection modules
│   ├── __init__.py
│   ├── youtube_collector.py
│   ├── forum_collector.py
│   └── trends_collector.py
├── processing/           # Data processing modules
│   ├── __init__.py
│   └── popularity_analyzer.py
├── services/             # Business logic services
│   ├── __init__.py
│   └── workflow_service.py
└── frontend/             # Frontend components
    ├── __init__.py
    └── dashboard.py
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Database Management

```bash
# Create tables
python -c "from database import create_tables; create_tables()"

# View database
sqlite3 workflow_data.db
```

## API Keys Setup

### YouTube Data API v3

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add the API key to your `.env` file

### n8n Forum API (Optional)

1. Go to [n8n Community](https://community.n8n.io)
2. Create an account and log in
3. Go to your profile settings
4. Generate an API key
5. Add the API key to your `.env` file

## Automation & Cron Jobs

### Automated Data Updates

The system includes automated data update capabilities:

#### 1. Manual Update Script

```bash
# Update all data
python update_data.py --youtube-max 50 --forum-max 100

# Update with cleanup of old data
python update_data.py --youtube-max 50 --forum-max 100 --cleanup --cleanup-days 30

# Dry run to see what would be updated
python update_data.py --dry-run
```

#### 2. Cron Job Setup

```bash
# Edit crontab
crontab -e

# Add daily update at 2 AM
0 2 * * * cd /path/to/assignment && python update_data.py --youtube-max 50 --forum-max 100

# Add weekly update with cleanup on Sundays at 3 AM
0 3 * * 0 cd /path/to/assignment && python update_data.py --youtube-max 100 --forum-max 200 --cleanup --cleanup-days 30
```

#### 3. GitHub Actions (Automated)

The repository includes a GitHub Actions workflow (`.github/workflows/update-data.yml`) that:

- Runs daily at 2 AM UTC
- Updates data from all platforms
- Commits database changes back to the repository
- Can be triggered manually via GitHub UI

**Setup GitHub Actions:**

1. Add secrets to your GitHub repository:
   - `YOUTUBE_API_KEY`
   - `N8N_FORUM_API_KEY`
2. The workflow will run automatically

### Sample Data Generation

Generate at least 50 sample workflows for testing:

```bash
python generate_sample_data.py
```

This creates:

- 20 YouTube video workflows
- 20 Forum post workflows
- 20 Google Trends workflows
- Total: 60+ sample workflows

## Production Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Docker Compose

```yaml
version: "3.8"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - YOUTUBE_API_KEY=${YOUTUBE_API_KEY}
      - N8N_FORUM_API_KEY=${N8N_FORUM_API_KEY}
    volumes:
      - ./data:/app/data
```

## Monitoring and Logging

The application includes comprehensive logging:

- **INFO**: General application flow
- **WARNING**: Non-critical issues
- **ERROR**: Critical errors and exceptions

Logs are written to stdout and can be redirected to files in production.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:

- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for error details

# News Jungle Configuration

## Project Overview
News Jungle is an advanced news aggregation and exploration platform with an integrated AI-powered chat interface, designed to provide comprehensive insights into the American media landscape.

## Technology Stack
- **Frontend**: Streamlit
- **Database**: PostgreSQL
- **AI Integration**: Anthropic Claude AI (Latest model: claude-3-5-sonnet-20241022)
- **Core Dependencies**:
```toml
[project]
name = "news-jungle"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "anthropic>=0.46.0",
    "nltk>=3.9.1",
    "openai>=1.63.2",
    "pandas>=2.2.3",
    "plotly>=6.0.0",
    "psycopg2-binary>=2.9.9",
    "requests>=2.31.0",
    "streamlit>=1.42.0",
    "trafilatura>=2.0.0",
    "twilio>=9.4.1",
]
```

## Database Schema
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY DEFAULT nextval('articles_id_seq'),
    title TEXT NOT NULL,
    content TEXT,
    url TEXT UNIQUE NOT NULL,
    source TEXT NOT NULL,
    published_at TIMESTAMP NOT NULL,
    bias_score FLOAT,
    sentiment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Key Components

### 1. News Assistant (Anthropic Claude Integration)
```python
# chatbot.py
class NewsAssistant:
    system_prompt = """You are a helpful news assistant for News Jungle. Keep responses concise and friendly.
Your purpose is to:
1. Help users find news on specific topics
2. Explain how to use the news filters
3. Provide brief summaries of news topics
4. Answer questions about news sources and bias ratings"""
```

### 2. News Filtering System
Available filters:
- Topics: Technology, Politics, Business, Science, Health, Sports, Entertainment, Environment, Education, World News
- Outlet Sizes: Large, Medium, Small
- Political Leanings: Left, Center, Right
- Keyword Search

### 3. Chat Interface
- Sidebar implementation with Streamlit
- Real-time message updates
- Context-aware responses based on current filters
- Error handling and graceful fallbacks

## Required Environment Variables
```
DATABASE_URL=postgresql://[username]:[password]@[host]:[port]/[database]
ANTHROPIC_API_KEY=[your-anthropic-api-key]
```

## Setup Instructions
1. Clone the repository
2. Install Python 3.11 or higher
3. Install dependencies from pyproject.toml
4. Set up required environment variables
5. Initialize PostgreSQL database
6. Run the application:
```bash
streamlit run main.py
```

## Application Structure
```
├── main.py                 # Main Streamlit application
├── chatbot.py             # Anthropic AI integration
├── chat_interface.py      # Chat UI components
├── database.py            # Database operations
├── news_fetcher.py        # News aggregation
├── bias_analyzer.py       # Sentiment and bias analysis
├── news_summarizer.py     # Article summarization
└── utils.py              # Helper functions
```

## Features
1. Real-time news aggregation
2. AI-powered chat assistance
3. Multi-dimensional news filtering
4. Bias and sentiment analysis
5. Article summarization
6. Responsive design
7. PostgreSQL data persistence

## Development Guidelines
1. The app runs on port 5000 by default
2. Chat interface is implemented in the sidebar
3. News articles are cached in PostgreSQL
4. All API calls include error handling
5. UI updates are real-time
6. Database operations use connection pooling

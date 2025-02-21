from typing import List, Dict, Any
from datetime import datetime, timedelta
from news_sources import get_news_sources
import time
import concurrent.futures

def fetch_news(query: str, days_ago: int, source_count: int) -> List[Dict[str, Any]]:
    """
    Fetch news articles from multiple sources based on query and time range
    with rate limiting and error handling
    """
    all_articles = []
    error_count = 0
    MAX_RETRIES = 2  # Reduced retries for faster response
    RETRY_DELAY = 0.5  # Reduced delay

    # Get configured news sources
    news_sources = get_news_sources()

    def fetch_from_source(source):
        retries = 0
        while retries < MAX_RETRIES:
            try:
                articles = source.fetch_articles(query, days_ago)
                # Early filtering - only return articles matching query if specified
                if query and query != "All":
                    articles = [
                        article for article in articles
                        if query.lower() in article['title'].lower() or
                           query.lower() in article['content'].lower()
                    ]
                return articles
            except Exception as e:
                retries += 1
                print(f"Error fetching from source (attempt {retries}): {e}")
                if retries < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                continue
        return []

    # Fetch from all sources in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_source = {executor.submit(fetch_from_source, source): source 
                          for source in news_sources}

        for future in concurrent.futures.as_completed(future_to_source):
            articles = future.result()
            all_articles.extend(articles)

    # Deduplicate articles based on title and source
    seen = set()
    unique_articles = []
    for article in all_articles:
        key = (article['title'], article['source'])
        if key not in seen:
            seen.add(key)
            unique_articles.append(article)

    # Sort by published date (newest first)
    def get_datetime(article):
        try:
            date_str = article['published_at']
            if date_str.endswith('Z'):
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            elif '+' in date_str or '-' in date_str[10:]:
                return datetime.fromisoformat(date_str)
            else:
                return datetime.fromisoformat(date_str + '+00:00')
        except Exception:
            return datetime.now().astimezone()

    # Only sort if we have articles
    if unique_articles:
        unique_articles.sort(
            key=get_datetime,
            reverse=True
        )

        # Limit to requested number of sources earlier in the process
        return unique_articles[:source_count]

    return []
import requests

def fetch_gdelt_news():
    url = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": "All",
        "mode": "artlist",
        "format": "json",
        "timespan": "1440",
        "sort": "DateDesc"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("articles", [])
    else:
        print("Error fetching from GDELT:", response.status_code, response.text)
        return []

if __name__ == "__main__":
    articles = fetch_gdelt_news()
    print(articles[:5])

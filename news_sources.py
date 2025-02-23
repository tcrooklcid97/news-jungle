import os
from typing import List, Dict, Any
import requests
from datetime import datetime, timedelta
import trafilatura
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from urllib.error import URLError
import time
import re

def get_datetime(date_str):
    """Convert string to timezone-aware datetime"""
    try:
        if date_str.endswith('Z'):
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        elif '+' in date_str or '-' in date_str[10:]:
            return datetime.fromisoformat(date_str)
        else:
            return datetime.fromisoformat(date_str + '+00:00')
    except Exception:
        return datetime.now().astimezone()

class NewsSource:
    """Base class for news sources"""
    def fetch_articles(self, query: str, days: int) -> List[Dict[str, Any]]:
        raise NotImplementedError

def clean_search_term(query: str) -> str:
    """Clean and prepare search terms for advanced matching"""
    # Common variations and misspellings
    corrections = {
        'vollyball': 'volleyball',
        'basket ball': 'basketball',
        'base ball': 'baseball',
        'foot ball': 'football',
        'volley ball': 'volleyball',
        'bball': 'basketball',
        'bsball': 'baseball',
        'fball': 'football'
    }

    # Clean the query
    query = query.lower().strip()

    # Apply corrections
    for misspelling, correction in corrections.items():
        if misspelling in query:
            query = query.replace(misspelling, correction)

    return query

def is_relevant_content(text: str, search_terms: List[str]) -> bool:
    """
    Enhanced relevance checking with support for multiple terms
    """
    if not text or not search_terms:
        return False

    text = text.lower()

    # Handle special search operators
    for term in search_terms:
        if term.startswith('"') and term.endswith('"'):
            # Exact phrase match
            phrase = term.strip('"').lower()
            if phrase not in text:
                return False
        elif '|' in term:
            # OR operator
            alternatives = [alt.strip().lower() for alt in term.split('|')]
            if not any(alt in text for alt in alternatives):
                return False
        else:
            # Regular term match
            if term not in text:
                return False

    return True

class RSSNewsSource(NewsSource):
    """RSS Feed news source using trafilatura"""
    def __init__(self, feed_urls: List[str]):
        self.feed_urls = feed_urls

    def fetch_articles(self, query: str, days: int) -> List[Dict[str, Any]]:
        # Clean and prepare search terms
        query = clean_search_term(query)
        search_terms = [term.strip() for term in query.split()]

        articles = []
        cutoff_date = datetime.now().astimezone() - timedelta(days=days)

        for feed_url in self.feed_urls:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(feed_url, headers=headers, timeout=10)
                response.raise_for_status()

                tree = ET.fromstring(response.content)

                # Handle different RSS versions
                if 'rss' in tree.tag:
                    items = tree.findall('.//item')
                else:  # Atom feed
                    items = tree.findall('.//{http://www.w3.org/2005/Atom}entry')

                for item in items:
                    try:
                        # Extract data based on feed type
                        if 'rss' in tree.tag:
                            title = item.find('title').text if item.find('title') is not None else ''
                            link = item.find('link').text if item.find('link') is not None else ''
                            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                            description = item.find('description').text if item.find('description') is not None else ''
                        else:  # Atom feed
                            title = item.find('{http://www.w3.org/2005/Atom}title').text if item.find('{http://www.w3.org/2005/Atom}title') is not None else ''
                            link = item.find('{http://www.w3.org/2005/Atom}link').get('href') if item.find('{http://www.w3.org/2005/Atom}link') is not None else ''
                            pub_date = item.find('{http://www.w3.org/2005/Atom}updated').text if item.find('{http://www.w3.org/2005/Atom}updated') is not None else ''
                            description = item.find('{http://www.w3.org/2005/Atom}summary').text if item.find('{http://www.w3.org/2005/Atom}summary') is not None else ''

                        if not all([title, link, pub_date]):
                            continue

                        published = get_datetime(pub_date)

                        if published < cutoff_date:
                            continue

                        # Enhanced relevance checking
                        content_to_check = f"{title} {description}".lower()
                        if query.lower() == "all" or is_relevant_content(content_to_check, search_terms):
                            try:
                                content = description
                                if link:
                                    article_response = requests.get(link, headers=headers, timeout=5)
                                    if article_response.status_code == 200:
                                        extracted = trafilatura.extract(article_response.text)
                                        if extracted:
                                            content = extracted
                            except Exception as e:
                                print(f"Error extracting content from {link}: {e}")
                                content = description

                            articles.append({
                                'title': title,
                                'source': feed_url.split('/')[2],
                                'content': content,
                                'url': link,
                                'published_at': published.isoformat()
                            })

                    except Exception as e:
                        print(f"Error processing RSS item: {e}")
                        continue

            except Exception as e:
                print(f"Error fetching RSS feed {feed_url}: {e}")
                continue

        return articles

def get_news_sources() -> List[NewsSource]:
    """Get list of configured news sources with most reliable feeds"""
    rss_feeds = [
        # Sports-specific sources
        "https://www.volleyball.world/en/feed",
        "https://www.fivb.com/en/feed",
        "https://volleyballmag.com/feed/",
        "https://www.espn.com/espn/rss/volleyball/news",
        "https://www.espn.com/espn/rss/news",
        "https://sports.yahoo.com/rss/volleyball",
        "https://sports.yahoo.com/rss/",
        "https://rss.nbcsports.com/",
        "https://www.cbssports.com/rss/headlines/",
        "https://www.teamusa.org/USA-Volleyball/RSS",

        # Major broadcast networks
        "https://feeds.nbcnews.com/nbcnews/public/news",
        "https://www.cbsnews.com/latest/rss/main",
        "https://abcnews.go.com/abcnews/usheadlines",

        # Major newspapers
        "https://rss.nytimes.com/services/xml/rss/nyt/Sports.xml",
        "https://feeds.washingtonpost.com/rss/sports",

        # News magazines and digital outlets
        "https://www.economist.com/united-states/rss.xml",
        "https://feeds.bloomberg.com/politics/news.rss",
        "https://feeds.npr.org/1001/rss.xml",
        "https://www.vox.com/rss/index.xml"
    ]

    return [
        RSSNewsSource(rss_feeds),
        GDELTNewsSource(),
        GoogleNewsSource()
    ]

class GDELTNewsSource(NewsSource):
    """GDELT news source with rate limiting"""
    def __init__(self):
        self.base_url = "https://api.gdeltproject.org/api/v2/doc/doc"
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum time between requests in seconds

    def fetch_articles(self, query: str, days: int) -> List[Dict[str, Any]]:
        try:
            # Implement rate limiting
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last_request)

            timespan = str(int(days * 24 * 60))

            params = {
                'query': f"{query} sourceloc:USA",
                'mode': 'artlist',
                'format': 'json',
                'timespan': timespan,
                'sort': 'DateDesc',
                'maxrecords': 50  # Limit results to avoid rate limiting
            }

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
            self.last_request_time = time.time()

            if response.status_code == 429:  # Too Many Requests
                print("Rate limited by GDELT, backing off...")
                return []

            response.raise_for_status()
            data = response.json()
            articles = []

            if 'articles' in data:
                for article in data['articles']:
                    try:
                        # Only include articles from US domains
                        domain = article.get('domain', '')
                        if domain.endswith('.com') or domain.endswith('.org') or domain.endswith('.edu'):
                            articles.append({
                                'title': article.get('title', ''),
                                'source': domain,
                                'content': article.get('excerpt', ''),
                                'url': article.get('url', ''),
                                'published_at': article.get('seendate', datetime.now().isoformat())
                            })
                    except Exception as e:
                        print(f"Error processing GDELT article: {e}")
                        continue

            return articles

        except Exception as e:
            print(f"Error fetching from GDELT: {e}")
            return []

class GoogleNewsSource(NewsSource):
    """Google Custom Search news source"""
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_SEARCH_API_KEY")
        self.search_engine_id = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum time between requests

    def fetch_articles(self, query: str, days: int) -> List[Dict[str, Any]]:
        if not self.api_key or not self.search_engine_id:
            print("Google Search credentials not configured")
            return []

        try:
            # Implement rate limiting
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last_request)

            # Prepare search query
            # If query is in quotes, keep it as is; otherwise, add news-related terms
            if not (query.startswith('"') and query.endswith('"')):
                query = f"{query} news articles"

            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'dateRestrict': f'd{days}',  # Restrict to last N days
                'num': 10,  # Number of results per request
                'safe': 'active'
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            self.last_request_time = time.time()

            if response.status_code == 429:  # Too Many Requests
                print("Rate limited by Google Search API, backing off...")
                return []

            response.raise_for_status()
            data = response.json()
            articles = []

            if 'items' in data:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }

                for item in data['items']:
                    try:
                        url = item.get('link', '')
                        if not url:
                            continue

                        # Extract full article content
                        content = item.get('snippet', '')
                        try:
                            article_response = requests.get(url, headers=headers, timeout=5)
                            if article_response.status_code == 200:
                                extracted = trafilatura.extract(article_response.text)
                                if extracted:
                                    content = extracted
                        except Exception as e:
                            print(f"Error extracting content from {url}: {e}")

                        articles.append({
                            'title': item.get('title', ''),
                            'source': item.get('displayLink', url.split('/')[2]),
                            'content': content,
                            'url': url,
                            'published_at': datetime.now().isoformat()  # Use current time as fallback
                        })

                    except Exception as e:
                        print(f"Error processing Google Search result: {e}")
                        continue

            return articles

        except Exception as e:
            print(f"Error fetching from Google Search: {e}")
            return []
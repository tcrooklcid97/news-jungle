from typing import List, Dict, Any
import requests
from datetime import datetime, timedelta
import os
import trafilatura
import xml.etree.ElementTree as ET
from urllib.request import urlopen
from urllib.error import URLError

def get_datetime(date_str):
    """Convert string to timezone-aware datetime"""
    try:
        if date_str.endswith('Z'):
            # Parse UTC date
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        elif '+' in date_str or '-' in date_str[10:]:  # Check for timezone offset
            # Parse date with timezone
            return datetime.fromisoformat(date_str)
        else:
            # Assume UTC for naive dates
            return datetime.fromisoformat(date_str + '+00:00')
    except Exception:
        # Use timezone-aware datetime for consistency
        return datetime.now().astimezone()

class NewsSource:
    """Base class for news sources"""
    def fetch_articles(self, query: str, days: int) -> List[Dict[str, Any]]:
        raise NotImplementedError

class RSSNewsSource(NewsSource):
    """RSS Feed news source using trafilatura"""
    def __init__(self, feed_urls: List[str]):
        self.feed_urls = feed_urls

    def fetch_articles(self, query: str, days: int) -> List[Dict[str, Any]]:
        articles = []
        cutoff_date = datetime.now().astimezone() - timedelta(days=days)

        for feed_url in self.feed_urls:
            try:
                response = urlopen(feed_url, timeout=5)  # Reduced timeout
                tree = ET.parse(response)
                root = tree.getroot()

                # Handle different RSS versions
                if root.tag == 'rss':
                    items = root.findall('.//item')
                else:  # Atom feed
                    items = root.findall('.//{http://www.w3.org/2005/Atom}entry')

                for item in items:
                    # Extract data based on feed type
                    if root.tag == 'rss':
                        title = item.find('title').text if item.find('title') is not None else ''
                        link = item.find('link').text if item.find('link') is not None else ''
                        pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                        description = item.find('description').text if item.find('description') is not None else ''
                    else:  # Atom feed
                        title = item.find('{http://www.w3.org/2005/Atom}title').text if item.find('{http://www.w3.org/2005/Atom}title') is not None else ''
                        link = item.find('{http://www.w3.org/2005/Atom}link').get('href') if item.find('{http://www.w3.org/2005/Atom}link') is not None else ''
                        pub_date = item.find('{http://www.w3.org/2005/Atom}updated').text if item.find('{http://www.w3.org/2005/Atom}updated') is not None else ''
                        description = item.find('{http://www.w3.org/2005/Atom}summary').text if item.find('{http://www.w3.org/2005/Atom}summary') is not None else ''

                    published = get_datetime(pub_date)

                    # Skip old articles
                    if published < cutoff_date:
                        continue

                    # Check if article matches query
                    if query == "All" or query.lower() in title.lower() or query.lower() in description.lower():
                        try:
                            # Reduce content fetch timeout
                            content = trafilatura.extract(requests.get(link, timeout=3).text)
                            if not content:
                                content = description
                        except Exception:
                            content = description

                        articles.append({
                            'title': title,
                            'source': feed_url.split('/')[2],  # Extract domain as source
                            'content': content,
                            'url': link,
                            'published_at': published.isoformat()
                        })

            except (URLError, ET.ParseError) as e:
                print(f"Error fetching RSS feed {feed_url}: {e}")
                continue

        return articles

class MediaStackNewsSource(NewsSource):
    """MediaStack news source"""
    def __init__(self):
        self.api_key = os.environ.get('MEDIASTACK_API_KEY')
        self.base_url = "http://api.mediastack.com/v1/news"

    def fetch_articles(self, query: str, days: int) -> List[Dict[str, Any]]:
        if not self.api_key:
            print("MediaStack API key not found")
            return []

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            params = {
                'access_key': self.api_key,
                'keywords': query,
                'countries': 'us',  # Only US news
                'languages': 'en',
                'date': f"{start_date.strftime('%Y-%m-%d')},{end_date.strftime('%Y-%m-%d')}",
                'sort': 'published_desc',
                'limit': 100  # Increased from 25 to 100
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = []
            if 'data' in data:
                for article in data['data']:
                    # Only include articles from US sources
                    if article.get('country') == 'us':
                        articles.append({
                            'title': article.get('title', ''),
                            'source': article.get('source', 'MediaStack'),
                            'author': article.get('author', 'Unknown'),
                            'content': article.get('description', ''),
                            'url': article.get('url', ''),
                            'published_at': article.get('published_at', datetime.now().isoformat())
                        })

            return articles

        except Exception as e:
            print(f"Error fetching from MediaStack: {e}")
            return []

class GDELTNewsSource(NewsSource):
    """GDELT news source"""
    def __init__(self):
        self.base_url = "https://api.gdeltproject.org/api/v2/doc/doc"

    def fetch_articles(self, query: str, days: int) -> List[Dict[str, Any]]:
        try:
            timespan = str(int(days * 24 * 60))

            params = {
                'query': f"{query} sourceloc:USA",  # Only US sources
                'mode': 'artlist',
                'format': 'json',
                'timespan': timespan,
                'sort': 'DateDesc'
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            articles = []

            if 'articles' in data:
                for article in data['articles']:
                    # Only include articles from US domains
                    domain = article.get('domain', '')
                    if domain.endswith('.com') or domain.endswith('.org') or domain.endswith('.edu'):
                        articles.append({
                            'title': article.get('title', ''),
                            'source': domain,
                            'author': domain,
                            'content': article.get('excerpt', ''),
                            'url': article.get('url', ''),
                            'published_at': article.get('seendate', datetime.now().isoformat())
                        })

            return articles

        except Exception as e:
            print(f"Error fetching from GDELT: {e}")
            return []

def get_news_sources() -> List[NewsSource]:
    """Get list of configured news sources"""
    # Expanded list of major American news outlets
    rss_feeds = [
        # Major broadcast networks
        "http://rss.cnn.com/rss/cnn_topstories.rss",
        "https://feeds.foxnews.com/foxnews/latest",
        "https://feeds.nbcnews.com/nbcnews/public/news",
        "https://www.cbsnews.com/latest/rss/main",
        "https://abcnews.go.com/abcnews/usheadlines",

        # Major newspapers
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://feeds.washingtonpost.com/rss/national",
        "https://www.latimes.com/rss2.0.xml",
        "https://nypost.com/feed",

        # News magazines and analysis
        "https://www.economist.com/united-states/rss.xml",
        "https://www.newyorker.com/feed/news",
        "https://feeds.bloomberg.com/politics/news.rss",

        # Digital-native outlets
        "https://rss.politico.com/politics-news.xml",
        "https://feeds.npr.org/1001/rss.xml",
        "https://www.vox.com/rss/index.xml",
        "https://www.buzzfeed.com/news.xml",

        # Business news
        "https://www.wsj.com/xml/rss/3_7085.xml",
        "https://www.forbes.com/real-time/feed2/",
        "https://feeds.marketwatch.com/marketwatch/topstories/"
    ]

    return [
        RSSNewsSource(rss_feeds),
        MediaStackNewsSource(),
        GDELTNewsSource()  # Added GDELT as an active source
    ]
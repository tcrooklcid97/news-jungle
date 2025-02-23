import os
import nltk
from openai import OpenAI
from typing import List, Dict, Any
import psycopg2
from datetime import datetime, timedelta
from nltk.tokenize import sent_tokenize
from hashlib import md5
import json

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai = OpenAI(api_key=OPENAI_API_KEY)

def get_cached_summary(cache_key: str) -> str:
    """Get a cached summary if available and not expired"""
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()

        # Create cache table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS summary_cache (
                cache_key TEXT PRIMARY KEY,
                summary TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        # Get cached summary if not older than 24 hours
        cur.execute("""
            SELECT summary FROM summary_cache 
            WHERE cache_key = %s 
            AND created_at > NOW() - INTERVAL '24 hours'
        """, (cache_key,))

        result = cur.fetchone()
        if result:
            return result[0]
    except Exception as e:
        print(f"Cache error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
    return None

def save_cached_summary(cache_key: str, summary: str):
    """Save a summary to cache"""
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO summary_cache (cache_key, summary)
            VALUES (%s, %s)
            ON CONFLICT (cache_key) 
            DO UPDATE SET summary = EXCLUDED.summary, created_at = CURRENT_TIMESTAMP
        """, (cache_key, summary))

        conn.commit()
    except Exception as e:
        print(f"Cache save error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def fallback_summarize(articles: List[Dict[str, Any]], max_sentences: int = 2) -> dict:
    """Generate a concise summary using key information from multiple articles"""
    try:
        # Create lists to store points and their associated URLs
        key_points = []
        point_urls = []

        # Process up to 5 articles
        for article in articles[:5]:
            # Get the title as it's usually the most important information
            title = article['title'].strip()
            url = article['url']

            # Add title if it's not already included
            if title and title not in key_points and len(key_points) < max_sentences:
                key_points.append(title)
                point_urls.append(url)

        # Format the summary
        if key_points:
            return {
                'points': key_points,
                'urls': point_urls,
                'is_ai': False
            }
        else:
            return {
                'points': ["No key points found"],
                'urls': [],
                'is_ai': False
            }

    except Exception as e:
        return {
            'points': [f"Fallback summarization failed: {str(e)}"],
            'urls': [],
            'is_ai': False
        }

def summarize_articles(articles: List[Dict[str, Any]], topic: str) -> dict:
    """
    Generate a summary of multiple news articles using OpenAI, with caching and fallback.
    Returns a dict with summary points and their associated URLs.
    """
    if not articles:
        return {
            'points': ["No articles available for summarization."],
            'urls': [],
            'is_ai': False
        }

    # Generate cache key from article titles and topic
    cache_input = topic + "".join(sorted([article['title'] for article in articles[:5]]))
    cache_key = md5(cache_input.encode()).hexdigest()

    # Try to get cached summary
    cached_summary = get_cached_summary(cache_key)
    if cached_summary:
        return json.loads(cached_summary)

    # If no OpenAI key, use fallback
    if not OPENAI_API_KEY:
        return fallback_summarize(articles)

    # Prepare article information
    articles_text = "\n\n".join([
        f"Title: {article['title']}\nSource: {article['source']}\nContent: {article['content'][:500]}..."
        for article in articles[:5]
    ])

    try:
        prompt = f"""Analyze these news articles about {topic} and provide a VERY concise summary.
Return the response in this exact JSON format:
{{
    "points": ["point 1", "point 2"],  // 2-3 key points, each 10-15 words
    "article_indices": [0, 1]  // indices of articles that best match each point
}}

Articles to analyze:
{articles_text}

Requirements:
1. Maximum 2-3 key points
2. Each point should be 10-15 words maximum
3. Focus on the most important developments only
4. Keep it objective and factual
5. For each point, specify which article (0-4) best represents that point
"""

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=200,
            temperature=0.7
        )

        result = json.loads(response.choices[0].message.content)

        # Map article indices to URLs
        urls = [articles[idx]['url'] for idx in result['article_indices']]

        summary_dict = {
            'points': result['points'],
            'urls': urls,
            'is_ai': True
        }

        # Cache the successful summary
        save_cached_summary(cache_key, json.dumps(summary_dict))

        return summary_dict

    except Exception as e:
        error_message = str(e)
        if any(err in error_message for err in ["insufficient_quota", "invalid_api_key", "rate_limit_exceeded"]):
            return fallback_summarize(articles)
        else:
            return fallback_summarize(articles)
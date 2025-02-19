from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db_connection():
    """Create a database connection"""
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Drop existing sequence if exists
        cur.execute('''
            DROP SEQUENCE IF EXISTS articles_id_seq CASCADE;
            CREATE SEQUENCE articles_id_seq;
        ''')

        # Create articles table with proper sequence
        cur.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY DEFAULT nextval('articles_id_seq'),
                title TEXT NOT NULL,
                content TEXT,
                url TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                published_at TIMESTAMP NOT NULL,
                bias_score FLOAT,
                sentiment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Set sequence ownership
        cur.execute('''
            ALTER SEQUENCE articles_id_seq OWNED BY articles.id;
        ''')

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def save_article(article_data):
    """Save an article to the database"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Use INSERT ... ON CONFLICT to handle duplicates
        cur.execute('''
            INSERT INTO articles (title, content, url, source, published_at, bias_score, sentiment)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO UPDATE SET
                title = EXCLUDED.title,
                content = EXCLUDED.content,
                bias_score = EXCLUDED.bias_score,
                sentiment = EXCLUDED.sentiment,
                published_at = EXCLUDED.published_at
            RETURNING id
        ''', (
            article_data['title'],
            article_data['content'],
            article_data['url'],
            article_data['source'],
            article_data['published_at'],
            article_data['bias_score'],
            article_data['sentiment']
        ))
        conn.commit()
    except Exception as e:
        print(f"Error saving article: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def get_cached_analysis(topic, max_age_hours=1):
    """Get cached analysis results if they exist and are recent"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute('''
            SELECT data FROM analysis_cache
            WHERE topic = %s AND last_updated > NOW() - INTERVAL '%s hours'
        ''', (topic, max_age_hours))

        result = cur.fetchone()
        return result['data'] if result else None
    finally:
        cur.close()
        conn.close()
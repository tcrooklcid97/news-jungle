from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os

def get_db_connection():
    """Create a database connection"""
    return psycopg2.connect(os.getenv('DATABASE_URL'))

def init_db():
    """Initialize database tables and indexes"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Create sequence if not exists
        cur.execute('''
            CREATE SEQUENCE IF NOT EXISTS articles_id_seq;
        ''')

        # Create articles table if not exists
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

        # Create indexes for frequently searched columns
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
            CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
            CREATE INDEX IF NOT EXISTS idx_articles_title_trgm ON articles USING GIN (title gin_trgm_ops);
        ''')

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()

def get_paginated_articles(filters, page=1, per_page=10):
    """Get paginated articles with filters"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    offset = (page - 1) * per_page

    try:
        # Base query with pagination
        query = '''
            SELECT *
            FROM articles
            WHERE published_at >= NOW() - INTERVAL '7 days'
        '''
        params = []

        # Add filters if provided
        if filters.get('source'):
            query += ' AND source = %s'
            params.append(filters['source'])

        if filters.get('topic') and filters['topic'] != 'All':
            query += ' AND title ILIKE %s'
            params.append(f'%{filters["topic"]}%')

        # Add ordering and pagination
        query += '''
            ORDER BY published_at DESC
            LIMIT %s OFFSET %s
        '''
        params.extend([per_page, offset])

        # Get total count
        count_query = query.replace('SELECT *', 'SELECT COUNT(*)')
        count_query = count_query[:count_query.find('LIMIT')]
        cur.execute(count_query, params[:-2])
        total_count = cur.fetchone()['count']

        # Get paginated results
        cur.execute(query, params)
        articles = cur.fetchall()

        return {
            'articles': articles,
            'total': total_count,
            'pages': (total_count + per_page - 1) // per_page,
            'current_page': page
        }
    finally:
        cur.close()
        conn.close()

def save_article(article_data):
    """Save an article to the database"""
    conn = get_db_connection()
    cur = conn.cursor()

    try:
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
from datetime import datetime
import re

def format_date(date_str: str) -> str:
    """
    Format date string to readable format
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return date_obj.strftime("%B %d, %Y %I:%M %p")
    except:
        return date_str

def clean_text(text: str) -> str:
    """
    Clean and format article text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())

    # Remove special characters
    text = re.sub(r'[^\w\s.,!?-]', '', text)

    # Ensure proper spacing after punctuation
    text = re.sub(r'([.,!?])([^\s])', r'\1 \2', text)

    return text

def sentiment_to_emoji(sentiment: str) -> str:
    """
    Convert sentiment label to appropriate emoji
    """
    sentiment_map = {
        'Positive': '😊',
        'Negative': '😔',
        'Neutral': '😐'
    }
    return sentiment_map.get(sentiment, '❓')  # Default to question mark if sentiment not found
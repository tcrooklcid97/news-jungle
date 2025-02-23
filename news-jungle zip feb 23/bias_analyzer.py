import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
import re

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('sentiment/vader_lexicon.zip')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt')
    nltk.download('vader_lexicon')
    nltk.download('punkt_tab')

# Define major US news outlets based on December 2024 traffic data
# Sources: Statista, Press Gazette, and Visual Capitalist
LARGE_OUTLETS = {
    # Top tier (300M+ monthly visits)
    'cnn', 'nytimes', 'new york times', 'foxnews', 'fox news', 'yahoo news',
    'msn news', 'google news',

    # Second tier (100M-300M monthly visits)
    'washington post', 'wsj', 'wall street journal', 'usa today', 
    'nbcnews', 'nbc news', 'bbc', 'abc news', 'cbs news',
    'nypost', 'new york post', 'huffpost', 'forbes'
}

MEDIUM_OUTLETS = {
    # 50M-100M monthly visits
    'politico', 'the hill', 'bloomberg', 'reuters', 'business insider',
    'los angeles times', 'latimes', 'newsweek', 'the atlantic',

    # 20M-50M monthly visits
    'vox', 'axios', 'buzzfeed news', 'daily beast', 'slate',
    'marketwatch', 'cnbc', 'npr', 'time', 'economist'
}

def get_outlet_size(source: str) -> float:
    """
    Classify news outlet size on a scale of 0 (smallest) to 1 (largest)
    Based on monthly traffic data from Statista and Press Gazette
    """
    source_lower = source.lower()
    if any(outlet in source_lower for outlet in LARGE_OUTLETS):
        return 1.0
    elif any(outlet in source_lower for outlet in MEDIUM_OUTLETS):
        return 0.5
    return 0.0  # Small outlets or unknown sources

def analyze_bias(text: str, source: str = "") -> dict:
    """
    Analyze text for bias using various metrics
    """
    # Initialize analyzer
    sia = SentimentIntensityAnalyzer()

    try:
        # Clean text
        clean_text = re.sub(r'[^\w\s]', '', text)

        # Tokenize with error handling
        try:
            words = word_tokenize(clean_text.lower())
            sentences = sent_tokenize(text)
        except Exception as e:
            print(f"Tokenization error: {e}")
            words = clean_text.lower().split()
            sentences = [text]

        # Sentiment analysis
        sentiment_scores = sia.polarity_scores(text)

        # Bias indicators
        conservative_words = {
            'radical', 'socialist', 'leftist', 'communist', 'liberal agenda',
            'traditional values', 'patriot', 'freedom', 'liberty'
        }

        liberal_words = {
            'progressive', 'conservative agenda', 'right-wing', 'alt-right',
            'social justice', 'equality', 'reform', 'diversity'
        }

        # Calculate political bias (-1 = liberal, 1 = conservative)
        conservative_count = sum(1 for word in words if word in conservative_words)
        liberal_count = sum(1 for word in words if word in liberal_words)
        political_bias = (conservative_count - liberal_count) / max(len(words), 1)

        # Determine sentiment label
        if sentiment_scores['compound'] >= 0.05:
            sentiment = 'Positive'
        elif sentiment_scores['compound'] <= -0.05:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        # Get outlet size
        outlet_size = get_outlet_size(source)

        return {
            'bias_score': abs(political_bias),
            'political_bias': political_bias,
            'outlet_size': outlet_size,
            'sentiment': sentiment
        }
    except Exception as e:
        print(f"Error in analyze_bias: {e}")
        return {
            'bias_score': 0.0,
            'political_bias': 0.0,
            'outlet_size': get_outlet_size(source),
            'sentiment': 'Neutral'
        }
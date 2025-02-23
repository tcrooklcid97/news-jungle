import re
import nltk
from nltk.tokenize import sent_tokenize
from transformers import pipeline

# Load RoBERTa sentiment model
bias_model = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-sentiment", tokenizer="cardiffnlp/twitter-roberta-base-sentiment")

# Define biased words/phrases list
BIASED_WORDS = {"radical", "corrupt", "fake news", "propaganda", "agenda", "elites", "deep state", "witch hunt"}

def highlight_biased_phrases(text: str):
    """Identifies and highlights biased words/phrases in a given text."""
    sentences = sent_tokenize(text)
    biased_sentences = []
    
    for sent in sentences:
        words = set(re.findall(r"\b\w+\b", sent.lower()))
        common_biased_words = words.intersection(BIASED_WORDS)
        if common_biased_words:
            biased_sentences.append((sent, list(common_biased_words)))
    
    return biased_sentences

def analyze_bias(text: str) -> dict:
    """Improved bias analysis function using RoBERTa and biased phrase detection."""
    clean_text = re.sub(r'[^\\w\\s]', '', text)
    bias_result = bias_model(clean_text[:512])  # Limit input to first 512 tokens
    bias_score = bias_result[0]['score'] * 10 if bias_result else 5  # Scale bias score 0-10
    
    # Identify biased phrases
    biased_phrases = highlight_biased_phrases(text)
    
    return {
        "bias_score": round(bias_score, 2),
        "bias_label": bias_result[0]['label'],
        "biased_phrases": biased_phrases
    }

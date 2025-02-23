import os
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
from news_sources import get_news_sources
import time
from openai import OpenAI
from search_agent import SearchAgent
import concurrent.futures
import streamlit as st
from functools import partial

# Initialize OpenAI client with better error handling
client = None
try:
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    if openai_api_key:
        client = OpenAI(api_key=openai_api_key)
    else:
        print("Warning: OPENAI_API_KEY not found in environment variables")
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")

# Initialize search agent with retry mechanism
max_retries = 3
for attempt in range(max_retries):
    try:
        search_agent = SearchAgent()
        break
    except Exception as e:
        if attempt == max_retries - 1:
            print(f"Failed to initialize search agent after {max_retries} attempts: {e}")
            search_agent = None
        time.sleep(2 ** attempt)  # Exponential backoff

@st.cache_data(ttl=300)  # Cache results for 5 minutes
def fetch_from_source(source, query: str, days_ago: int) -> List[Dict[str, Any]]:
    """Fetch articles from a single source with caching"""
    try:
        articles = source.fetch_articles(query, days_ago)
        return articles
    except Exception as e:
        print(f"Error fetching from source: {e}")
        return []

def fetch_news(query: str, days_ago: int, source_count: int) -> List[Dict[str, Any]]:
    """
    Main function to fetch and process news articles using multiple sources with parallel processing
    """
    try:
        print(f"Fetching news for query: {query}")

        # Get all configured news sources
        news_sources = get_news_sources()

        # Use ThreadPoolExecutor for parallel fetching
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Create partial function with fixed arguments
            fetch_func = partial(fetch_from_source, query=query, days_ago=days_ago)

            # Submit all fetch tasks
            future_to_source = {executor.submit(fetch_func, source): source 
                              for source in news_sources}

            # Collect results as they complete
            all_articles = []
            for future in concurrent.futures.as_completed(future_to_source):
                try:
                    articles = future.result()
                    all_articles.extend(articles)
                except Exception as e:
                    print(f"Source fetch failed: {e}")

        print(f"Total articles retrieved: {len(all_articles)}")

        if not all_articles:
            return []

        # Pre-filter articles before AI processing
        filtered_articles = all_articles
        if search_agent:
            try:
                filtered_articles = search_agent.process_articles(all_articles, query)
                print(f"Search agent filtered to {len(filtered_articles)} relevant articles")
            except Exception as e:
                print(f"Error in search agent processing: {e}")

        # Skip AI enhancement if OpenAI client is not available
        if client is None:
            print("Skipping AI enhancement due to missing OpenAI API key")
            return filtered_articles[:source_count]

        # Process articles in parallel batches
        try:
            enhanced_articles = []
            batch_size = 10  # Smaller batch size for better parallelization

            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                # Split articles into batches
                batches = [filtered_articles[i:i + batch_size] 
                          for i in range(0, len(filtered_articles), batch_size)]

                # Submit batch processing tasks
                future_to_batch = {executor.submit(enhance_articles_batch, batch, query): batch 
                                 for batch in batches}

                # Collect results as they complete
                for future in concurrent.futures.as_completed(future_to_batch):
                    try:
                        enhanced_batch = future.result()
                        enhanced_articles.extend(enhanced_batch)
                    except Exception as e:
                        print(f"Batch enhancement failed: {e}")
                        # Add unenhanced batch on failure
                        batch = future_to_batch[future]
                        enhanced_articles.extend(batch)

            print(f"Enhanced {len(enhanced_articles)} articles")
            return enhanced_articles[:source_count]

        except Exception as e:
            print(f"Error in AI enhancement: {e}")
            return filtered_articles[:source_count]

    except Exception as e:
        print(f"Error in fetch_news: {str(e)}")
        return []

@st.cache_data(ttl=900)  # Cache for 15 minutes
def enhance_articles_batch(batch: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Helper function to enhance a batch of articles with AI processing"""
    if not client:  # Skip if OpenAI client is not available
        return batch

    try:
        content_for_analysis = {
            "articles": [{
                "title": article["title"],
                "content": article["content"][:500],
                "source": article["source"]
            } for article in batch],
            "query": query
        }

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": """You are a news analysis AI. For each article provide:
                1. bias_score (-1 to 1, where -1 is far left, 0 is center, 1 is far right)
                2. sentiment (positive, negative, neutral)
                3. political_bias (numeric value matching bias_score)
                4. outlet_size (1.0 for large, 0.5 for medium, 0.0 for small outlets)
                Return as JSON array with the original article data plus these new fields."""
            }, {
                "role": "user",
                "content": json.dumps(content_for_analysis)
            }],
            response_format={"type": "json_object"}
        )

        # Parse and merge enhanced results
        result = json.loads(response.choices[0].message.content)
        enhanced_batch = result.get("articles", [])

        # Merge enhanced data with original articles
        for i, enhanced in enumerate(enhanced_batch):
            if i < len(batch):
                batch[i].update(enhanced)

        return batch
    except Exception as e:
        print(f"Error in batch enhancement: {e}")
        return batch  # Return original batch on error
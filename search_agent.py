import os
from typing import List, Dict, Any
from anthropic import Anthropic
import json

# the newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
# do not change this unless explicitly requested by the user
anthropic = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

class SearchAgent:
    def __init__(self):
        self.model = "claude-3-5-sonnet-20241022"

    def validate_topic_relevance(self, articles: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        """Filter articles based on topic relevance using Claude."""
        if not articles:
            return []

        try:
            # Split compound topics (e.g., "trump health")
            topics = topic.lower().split()

            # Prepare articles for analysis
            content_for_analysis = {
                "topics": topics,
                "articles": [{
                    "title": article["title"],
                    "content": article["content"][:1000] if article.get("content") else "",  # Increased context
                } for article in articles]
            }

            # Get Claude's analysis
            response = anthropic.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": f"""Analyze these news articles and determine if they substantively discuss ALL of the following topics: {topics}.
                    Return a JSON array of indices of relevant articles only.

                    Rules for relevance:
                    1. Article must meaningfully discuss ALL specified topics together
                    2. Just mentioning a topic in passing is not enough
                    3. Topics should be semantically related in the content
                    4. The relationship between topics should be a main focus

                    Articles: {json.dumps(content_for_analysis)}

                    Respond with a JSON object in this format:
                    {{"relevant_indices": [0, 2, 3]}}"""
                }],
            )

            # Parse response and filter articles
            result = json.loads(response.content)
            relevant_indices = result.get("relevant_indices", [])

            # Return only relevant articles
            return [articles[i] for i in relevant_indices if i < len(articles)]

        except Exception as e:
            print(f"Error in topic validation: {e}")
            return articles  # Return original articles if analysis fails

    def rank_articles(self, articles: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        """Rank articles by relevance and quality using Claude."""
        if not articles:
            return []

        try:
            topics = topic.lower().split()
            content_for_analysis = {
                "topics": topics,
                "articles": [{
                    "title": article["title"],
                    "content": article["content"][:1000] if article.get("content") else "",
                } for article in articles]
            }

            response = anthropic.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": f"""Rank these news articles by their relevance to ALL topics: {topics}.
                    Consider:
                    1. How central are ALL topics to the article's main focus
                    2. Strength of relationship between the topics
                    3. Depth of coverage for each topic
                    4. Recency and timeliness
                    5. Source credibility

                    Return a JSON array of indices in order of relevance.
                    Articles: {json.dumps(content_for_analysis)}

                    Respond with a JSON object in this format:
                    {{"ranked_indices": [2, 0, 3, 1]}}"""
                }],
            )

            # Parse response and reorder articles
            result = json.loads(response.content)
            ranked_indices = result.get("ranked_indices", [])

            # Return ranked articles
            return [articles[i] for i in ranked_indices if i < len(articles)]

        except Exception as e:
            print(f"Error in article ranking: {e}")
            return articles  # Return original order if ranking fails

    def process_articles(self, articles: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        """Main method to process and improve article results."""
        # First validate topic relevance with stricter filtering
        relevant_articles = self.validate_topic_relevance(articles, topic)

        # Then rank the relevant articles
        ranked_articles = self.rank_articles(relevant_articles, topic)

        return ranked_articles
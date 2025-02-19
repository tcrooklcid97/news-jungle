import os
import anthropic
from typing import List, Dict, Any, Optional

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

class NewsAssistant:
    def __init__(self):
        self.system_prompt = """You are a helpful news assistant for News Jungle. Keep responses concise and friendly.
Your purpose is to:
1. Help users find news on specific topics
2. Explain how to use the news filters
3. Provide brief summaries of news topics
4. Answer questions about news sources and bias ratings

Always keep responses focused on news-related queries."""

    def get_response(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response to user message with optional context"""
        try:
            # Format the complete message with context if available
            message_content = user_message
            if context:
                context_str = "\nCurrent filters:\n"
                for key, value in context.items():
                    if value and value not in ['All', 'All Sizes', 'All Views']:
                        context_str += f"- {key}: {value}\n"
                message_content += context_str

            # Call Anthropic API with the latest model
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",  # Latest model as of Oct 2024
                max_tokens=300,  # Keep responses concise
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": message_content}
                ]
            )

            return response.content[0].text

        except Exception as e:
            print(f"Error in get_response: {e}")
            return "I apologize, but I'm having trouble responding right now. Please try again."
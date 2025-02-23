import os
import base64
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_app_logo():
    """Generate the app logo using DALL-E"""
    try:
        if OPENAI_API_KEY:
            response = client.images.generate(
                model="dall-e-3",
                prompt="Create a modern, professional logo for 'News Jungle' - a news aggregation platform. Use imagery that combines journalism and jungle themes in a subtle way. The design should be minimalist and suitable for a website header.",
                n=1,
                size="256x256"
            )
            return response.data[0].url
    except Exception as e:
        print(f"Failed to generate logo: {e}")
        return get_fallback_logo()

    return get_fallback_logo()

def generate_background_image(page="main"):
    """Generate a background image based on the page type"""
    themes = {
        "main": "subtle jungle pattern with muted green tones, perfect for a news website background",
        "filters": "abstract pattern suggesting filters and organization, with gentle jungle-inspired colors",
        "results": "professional news-themed background with subtle jungle elements, perfect for content display"
    }

    try:
        if OPENAI_API_KEY:
            theme = themes.get(page, themes["main"])
            response = client.images.generate(
                model="dall-e-3",
                prompt=f"Create a subtle, professional background texture for a news website. {theme}. Make it very light and suitable for text overlay.",
                n=1,
                size="1024x1024"
            )
            return response.data[0].url
    except Exception as e:
        print(f"Failed to generate background: {e}")
        return get_fallback_background(page)

    return get_fallback_background(page)

def get_fallback_logo():
    """Generate a simple SVG logo for fallback"""
    svg = '''
        <svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#4A7B4B;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#2C3E2D;stop-opacity:1" />
                </linearGradient>
            </defs>
            <circle cx="128" cy="128" r="120" fill="url(#grad)"/>
            <text x="50%" y="50%" font-family="Arial" font-size="40" 
                fill="white" text-anchor="middle" dominant-baseline="middle">
                NEWS
            </text>
            <text x="50%" y="65%" font-family="Arial" font-size="32" 
                fill="white" text-anchor="middle" dominant-baseline="middle">
                JUNGLE
            </text>
        </svg>
    '''
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

def get_fallback_background(page="main"):
    """Generate a fallback background pattern based on the page"""
    colors = {
        "main": ("#4A7B4B", "#2C3E2D"),
        "filters": ("#3B614C", "#1E2F2E"),
        "results": ("#456B46", "#2A3C2B")
    }

    color1, color2 = colors.get(page, colors["main"])

    svg = f'''
        <svg width="1200" height="800" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:{color1};stop-opacity:0.2" />
                    <stop offset="100%" style="stop-color:{color2};stop-opacity:0.1" />
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#grad)"/>
        </svg>
    '''
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

def get_background_image():
    """Main function to get background image"""
    return generate_background_image()
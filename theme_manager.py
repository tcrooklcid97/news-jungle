import os
from typing import Dict, Any
import json
from PIL import Image
import io
import base64

class ThemeManager:
    def __init__(self):
        self.brand_assets = {
            'logo': {
                'color': 'NJ Logo/Logo Files/For Web/Color logo - no background.svg',
                'white': 'NJ Logo/Logo Files/For Web/White logo - no background.svg',
                'black': 'NJ Logo/Logo Files/For Web/Black logo - no background.svg',
                'background': 'attached_assets/symbol.png'
            },
            'favicon': 'static/brand/favicons/browser.png'
        }

        # Updated theme colors based on the new brand assets
        self.default_theme = {
            'primary_color': '#1E2F2E',    # Dark jungle green
            'secondary_color': '#3B614C',   # Forest green
            'background': '#F0F5F9',        # Light blue-grey background
            'card_background': '#FFFFFF',    # White for cards
            'text_color': '#2C3E2D',        # Dark green text
            'accent_color': '#4A7B4B',      # Lighter green accents
            'dropdown_bg': '#E8E1D5'        # Light warm grey for dropdowns
        }

    def _get_image_data_url(self, image_path: str) -> str:
        """Convert image file to base64 data URL"""
        try:
            with open(image_path, 'rb') as img_file:
                img_data = img_file.read()
                img_base64 = base64.b64encode(img_data).decode()
                ext = os.path.splitext(image_path)[1][1:]  # Get extension without dot
                return f'data:image/{ext};base64,{img_base64}'
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return ''

    def get_enhanced_styles(self) -> str:
        """Return enhanced CSS styles for the application with new branding"""
        bg_image_url = self._get_image_data_url(self.brand_assets['logo']['background'])

        return f"""
        <style>
        /* Global styles */
        .stApp {{
            background-image: url('{bg_image_url}');
            background-size: 50%;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-color: #F0F5F9;
            min-height: 100vh;
        }}

        /* Semi-transparent overlay for better readability */
        .stApp::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.92);
            z-index: 0;
        }}

        /* Ensure content stays above the overlay */
        .stApp > * {{
            position: relative;
            z-index: 1;
        }}

        /* Logo styling */
        .app-logo {{
            max-width: 200px;
            height: auto;
            margin: 1rem auto;
            display: block;
        }}

        /* Form submit button styling */
        .stButton > button,
        button[data-testid="baseButton-primary"],
        [data-testid="stFormSubmitButton"] button {{
            background: {self.default_theme['primary_color']} !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 0.5rem 1.5rem !important;
            border: none !important;
            transition: all 0.3s ease !important;
            background-image: linear-gradient(135deg, {self.default_theme['primary_color']}, {self.default_theme['secondary_color']}) !important;
            width: 100% !important;
            margin: 1rem 0 !important;
            font-size: 1.1rem !important;
        }}

        /* Button hover effects */
        .stButton > button:hover,
        button[data-testid="baseButton-primary"]:hover,
        [data-testid="stFormSubmitButton"] button:hover {{
            transform: translateY(-2px);
            background-image: linear-gradient(135deg, {self.default_theme['secondary_color']}, {self.default_theme['primary_color']}) !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        }}

        /* News card styling */
        .news-card {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: flex;
            gap: 1.5rem;
            align-items: flex-start;
            transition: transform 0.2s ease;
        }}

        .news-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        }}

        .news-logo {{
            width: 60px;
            height: 60px;
            object-fit: contain;
            border-radius: 8px;
        }}

        .news-content {{
            flex: 1;
        }}

        .news-content h3 {{
            margin: 0 0 0.5rem 0;
            color: {self.default_theme['primary_color']};
            font-weight: 600;
        }}

        .news-content p {{
            margin: 0.5rem 0;
            color: {self.default_theme['text_color']};
            line-height: 1.5;
        }}

        .news-content a {{
            color: {self.default_theme['secondary_color']};
            text-decoration: none;
            font-weight: bold;
            display: inline-block;
            margin-top: 0.5rem;
            transition: color 0.2s ease;
        }}

        .news-content a:hover {{
            color: {self.default_theme['primary_color']};
            text-decoration: underline;
        }}

        /* Dropdown and text input styling */
        .stSelectbox > div > div,
        .stTextInput input {{
            background-color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 8px !important;
        }}
        </style>
        """
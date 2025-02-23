import streamlit as st
st.set_page_config(
    page_title="News Jungle",
    page_icon="browser.png",
    layout="wide",
    menu_items=None
)

import json
import pandas as pd
from news_fetcher import fetch_news
from bias_analyzer import analyze_bias
from utils import format_date, clean_text, sentiment_to_emoji
from database import init_db, save_article, get_cached_analysis
from news_sources import get_news_sources
from theme_manager import ThemeManager

# Initialize theme manager and apply styles
theme_manager = ThemeManager()
st.markdown(theme_manager.get_enhanced_styles(), unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'filters'  # Default to filters page directly
if 'cached_news' not in st.session_state:
    st.session_state.cached_news = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = None
if 'filters' not in st.session_state:
    st.session_state.filters = {
        'topic': 'All',
        'size': 'All Sizes',
        'leaning': 'All Views'
    }

# Initialize database connection
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization error: {str(e)}")
    st.warning("Continuing without database support. Some features may be limited.")

if st.session_state.page == 'filters':
    # Topic filter with search capability
    topics = [
        "All",
        "Technology",
        "Politics",
        "Business",
        "Science",
        "Health",
        "Sports",
        "Entertainment",
        "Environment",
        "Education",
        "World News"
    ]

    st.title("News Jungle")

    col1, col2 = st.columns(2)

    with st.form(key='search_form'):
        with col1:
            selected_topic = st.selectbox("Select from common topics", topics, index=0)

        with col2:
            custom_topic = st.text_input(
                "Enter Key Word Search", "",
                help="""Search tips:
                - Use quotes for exact phrases: "women's volleyball"
                - Use | for alternatives: volleyball|volley
                - Combine terms: pro volleyball women
                """)

        # Update topic in session state
        final_topic = custom_topic if custom_topic else selected_topic
        if st.session_state.get('topic') != final_topic:
            st.session_state.topic = final_topic
            # Reset cached news when topic changes
            st.session_state.cached_news = None
            st.session_state.last_query = None

        # Outlet size filter
        outlet_sizes = ["All Sizes", "Large Outlets", "Medium Outlets", "Small Outlets"]
        selected_size = st.selectbox("Select News Outlet Size", outlet_sizes, index=0)

        # Political leaning filter
        political_leanings = ["All Views", "Left Leaning", "Center", "Right Leaning"]
        selected_leaning = st.selectbox("Select Political Leaning", political_leanings, index=0)

        # Submit button inside form
        submit_button = st.form_submit_button("Show Results", type="primary", use_container_width=True)

        if submit_button:
            st.session_state.filters = {
                'topic': final_topic,
                'size': selected_size,
                'leaning': selected_leaning
            }
            st.session_state.cached_news = None
            st.session_state.last_query = None
            st.session_state.page = 'results'
            st.rerun()

else:  # Results page
    # Add a "Back to Filters" button at the top
    if st.button("← Back to Filters"):
        st.session_state.page = 'filters'
        st.rerun()

    st.title("News Results")

    def get_paginated_articles(filters, page, per_page):
        """Get paginated articles with optimized caching"""
        if st.session_state.cached_news is None or st.session_state.last_query != filters['topic']:
            search_term = filters['topic']
            with st.spinner("Fetching latest news..."):
                articles = fetch_news(search_term, days_ago=5, source_count=50)
                if articles:
                    st.session_state.cached_news = articles
                    st.session_state.last_query = search_term
                else:
                    st.session_state.cached_news = []
                    st.session_state.last_query = search_term

        articles = st.session_state.cached_news
        df = pd.DataFrame(articles)

        # Apply filters
        if filters['size'] != "All Sizes":
            if 'outlet_size' not in df.columns:
                df['outlet_size'] = None
            size_map = {
                "Large Outlets": 1.0,
                "Medium Outlets": 0.5,
                "Small Outlets": 0.0
            }
            size_value = size_map[filters['size']]
            df = df[df['outlet_size'].notna() & (df['outlet_size'] == size_value)]

        if filters['leaning'] != "All Views":
            if 'political_bias' not in df.columns:
                df['political_bias'] = 0.0
            leaning_filters = {
                "Left Leaning": lambda x: x < -0.2,
                "Center": lambda x: abs(x) <= 0.2,
                "Right Leaning": lambda x: x > 0.2
            }
            df = df[df['political_bias'].apply(leaning_filters[filters['leaning']])]

        total_articles = len(df)
        start_index = (page - 1) * per_page
        end_index = min(start_index + per_page, total_articles)
        paginated_articles = df[start_index:end_index].to_dict(orient='records')
        total_pages = (total_articles + per_page - 1) // per_page

        return {
            'articles': paginated_articles,
            'total': total_articles,
            'current_page': page,
            'pages': total_pages
        }

    if hasattr(st.session_state, 'filters'):
        # Get current page from session state
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1

        # Get paginated results
        results = get_paginated_articles(
            st.session_state.filters,
            page=st.session_state.current_page,
            per_page=10
        )

        if results['articles']:
            # Display results count and pagination info
            st.write(f"Found {results['total']} articles • Page {results['current_page']} of {results['pages']}")

            # Display articles
            for article in results['articles']:
                try:
                    source_domain = article['source'].split('/')[0]
                    logo_url = f"https://logo.clearbit.com/{source_domain}"

                    # Create article card with error handling
                    st.markdown(f"""
                        <div class="news-card">
                            <img src="{logo_url}" class="news-logo" onerror="this.src='https://placehold.co/60x60?text=📰'">
                            <div class="news-content">
                                <h3>{article['title']}</h3>
                                <p>Source: {article['source']} | Published: {format_date(article['published_at'])}</p>
                                <p>{article.get('content', '')[:200]}...</p>
                                <a href="{article['url']}" target="_blank">Read More</a>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    print(f"Error displaying article: {e}")
                    continue

            # Pagination controls
            cols = st.columns(4)
            with cols[1]:
                if st.session_state.current_page > 1:
                    if st.button("← Previous"):
                        st.session_state.current_page -= 1
                        st.rerun()
            with cols[2]:
                if st.session_state.current_page < results['pages']:
                    if st.button("Next →"):
                        st.session_state.current_page += 1
                        st.rerun()
        else:
            st.warning("""No articles found matching your search criteria. 

            This could be because:
            1. There are no recent articles on this topic
            2. The topic might be misspelled
            3. Try broadening your search or using different keywords
            """)

    else:
        st.warning("Please set your filters first.")
        if st.button("Go to Filters"):
            st.session_state.page = 'filters'

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <p style='color: #666; font-size: 0.9em;'>
            News Jungle aggregates content from various news sources via Google Custom Search API.
            All articles remain the property of their respective publishers.
        </p>
    </div>
""", unsafe_allow_html=True)
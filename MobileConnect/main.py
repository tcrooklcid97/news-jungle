import streamlit as st

# Simple authentication
def authenticate():
    st.sidebar.header("Login")
    password = st.sidebar.text_input("Enter Password:", type="password")
    
    if password == "Tc100573!":
        return True
    else:
        st.sidebar.warning("Incorrect password. Access denied.")
        return False

if not authenticate():
    st.stop()  # Stop the app if authentication fails

# Main app content
st.title("News Jungle")
st.write("Welcome to the restricted News Jungle app!")

import streamlit as st
import json
import base64
from chat_interface import display_chat_interface # Added import statement

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="News Jungle",
    page_icon="🌴",
    layout="wide",
    menu_items=None
)

# Initialize and display chat interface # Added function call
display_chat_interface()

import pandas as pd
from news_fetcher import fetch_news
from bias_analyzer import analyze_bias
from utils import format_date, clean_text, sentiment_to_emoji
from database import init_db, save_article, get_cached_analysis
from image_generator import get_background_image, generate_app_logo, generate_background_image
from news_summarizer import summarize_articles
from chatbot import NewsAssistant

# Initialize chatbot
news_assistant = NewsAssistant()

# Initialize session state for chat
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
    # Add welcome message
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": "Welcome to News Jungle! How can I help you explore the news today?"
    })

# Initialize filters in session state
if 'filters' not in st.session_state:
    st.session_state.filters = {
        'topic': 'All',
        'size': 'All Sizes',
        'leaning': 'All Views',
        'search_query': ''
    }

# Handle incoming chat messages
if query := st.query_params.get("message"):
    print(f"Received message: {query}")  # Debug logging
    # Add user message to chat history
    st.session_state.chat_messages.append({"role": "user", "content": query})

    # Get chatbot response with current context
    try:
        context = st.session_state.get('filters', {})
        print(f"Getting response with context: {context}")  # Debug logging
        response = news_assistant.get_response(query, context)
        print(f"Got response: {response}")  # Debug logging

        # Add assistant response to chat history
        st.session_state.chat_messages.append({"role": "assistant", "content": response})

    except Exception as e:
        print(f"Error getting response: {e}")  # Debug logging
        error_message = "I'm having trouble responding right now. Please try again later."
        st.session_state.chat_messages.append({"role": "assistant", "content": error_message})

    # Clear the query parameter
    st.query_params.clear()

# Initialize database
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization error: {str(e)}")

# Get custom app logo and background
app_logo = generate_app_logo()
background_image = get_background_image()

# Enhanced CSS with custom logo
st.markdown(r"""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Custom logo styling */
    .app-logo {
        width: 80px;
        height: 80px;
        margin-right: 1rem;
        border-radius: 10px;
    }

    /* Background and global styles */
    .stApp {
        background-image: linear-gradient(
            rgba(240, 245, 249, 0.95),
            rgba(240, 245, 249, 0.95)
        ), url(""" + f"{background_image}" + r""");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Rest of your CSS remains unchanged */
    .news-card {
        padding: 1rem;
        border-radius: 10px;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        display: flex;
        align-items: center;
    }

    .news-logo {
        width: 60px;
        height: 60px;
        margin-right: 1rem;
        object-fit: contain;
    }

    .news-content {
        flex: 1;
    }

    /* Global transitions */
    * {
        transition: all 0.3s ease-in-out;
    }

    /* Custom styling for sliders */
    .stSlider {
        padding: 2rem 1rem !important;
        touch-action: none !important;
    }

    .stSlider > div > div > div {
        height: 1rem !important;
        border-radius: 0.5rem !important;
    }

    /* Slider thumb styling with improved stability */
    .stSlider > div > div > div > div {
        width: 2.5rem !important;
        height: 2.5rem !important;
        background-color: #4A7B4B !important;
        border: 3px solid white !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        transition: none !important;
        touch-action: none !important;
        cursor: grab !important;
    }

    /* Hover state */
    .stSlider > div > div > div > div:hover {
        background-color: #5B8C5C !important;
        transform: scale(1.1) !important;
        transition: transform 0.1s ease-out !important;
    }

    /* Active/dragging state */
    .stSlider > div > div > div > div:active {
        cursor: grabbing !important;
        transform: scale(1.05) !important;
        background-color: #3A6B3B !important;
        border-width: 4px !important;
        transition: none !important;
    }

    /* Slider track styling */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, 
            rgba(255, 99, 71, 0.8),
            rgba(74, 123, 75, 0.8)
        ) !important;
    }

    .reportview-container .main .block-container {
        padding: clamp(1rem, 3vw, 2rem);
        max-width: 100%;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        background-color: rgba(240, 245, 249, 0.8);
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 0.5rem;
    }

    /* Card animations */
    .streamlit-expanderHeader {
        transition: background-color 0.3s ease, transform 0.3s ease;
        border-radius: 8px;
        margin: 0.5rem 0;
    }

    .streamlit-expanderHeader:hover {
        background-color: rgba(74, 123, 75, 0.1);
        transform: translateX(5px);
    }

    /* Updated floating chat container styling */
    .floating-chat-container {
        position: fixed;
        bottom: 20px;          
        right: 20px;
        width: 250px;          
        height: 300px;         
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;      
        display: flex;
        flex-direction: column;
        overflow: hidden;   
        transition: all 0.3s ease;
        touch-action: none;  /* Enable touch events */
        cursor: move;       /* Show move cursor */
        user-select: none;  /* Prevent text selection while dragging */
    }

    .chat-header {
        padding: 10px;
        background: #4A7B4B;
        color: white;
        font-size: 14px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        cursor: move;      /* Show move cursor on header */
        display: flex;
        align-items: center;
        justify-content: space-between;
        touch-action: none;
    }

    .chat-messages {
        flex: 1;
        overflow-y: auto;
        padding: 10px;
        font-size: 12px;      
        background: #f5f5f5;
        min-height: 150px;    
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .chat-input {
        display: flex;
        padding: 10px;
        background: white;
        border-top: 1px solid #eee;
        gap: 8px;
    }

    .chat-input input {
        flex: 1;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 12px;
    }

    .chat-input button {
        padding: 8px 16px;
        background: #4A7B4B;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
    }

    .chat-input button:hover {
        background: #5B8C5C;
    }

    .user-message {
        align-self: flex-end;
        background: #4A7B4B;
        color: white;
        padding: 8px 12px;
        border-radius: 12px;
        max-width: 80%;
        word-wrap: break-word;
    }

    .assistant-message {
        align-self: flex-start;
        background: white;
        color: #333;
        padding: 8px 12px;
        border-radius: 12px;
        max-width: 80%;
        word-wrap: break-word;
    }
    /* Minimize/Maximize functionality */
    .chat-minimized {
        height: 40px !important;
        overflow: hidden;
    }

    /* Chat toggle button when minimized */
    .chat-toggle-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #4A7B4B;
        color: white;
        padding: 10px 20px;
        border-radius: 20px;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        z-index: 9998;
        display: none;
    }

    /* Show toggle button when chat is fully hidden */
    .chat-hidden .chat-toggle-button {
        display: block;
    }

    .chat-hidden .floating-chat-container {
        display: none;
    }

    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .floating-chat-container {
            width: 200px;          /* Even smaller on mobile */
            height: 250px;         /* Shorter on mobile */
            bottom: 10px;          /* Closer to bottom */
            right: 10px;           /* Closer to right */
        }

        .chat-messages {
            font-size: 11px;       /* Smaller font on mobile */
            min-height: 100px;     /* Shorter messages area */
        }
    }

    /* Updated parakeet styling */
    .parakeet {
        width: 24px;
        height: 24px;
        margin-right: 8px;
    }


    @keyframes bob {
        0% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0); }
    }

    </style>
""", unsafe_allow_html=True)

# Initialize session state for page navigation
if 'page' not in st.session_state:
    st.session_state.page = 'filters'

# Main content area
# Convert chat messages to JSON and encode in base64
try:
    chat_messages_json = json.dumps(st.session_state.chat_messages)
    chat_messages_b64 = base64.b64encode(chat_messages_json.encode('utf-8')).decode('utf-8')
except Exception as e:
    print(f"Error encoding chat messages: {e}")  # Debug logging
    chat_messages_b64 = base64.b64encode(json.dumps([{"role": "assistant", "content": "Chat system is temporarily unavailable"}]).encode('utf-8')).decode('utf-8')

st.markdown("""
    <div class="floating-chat-container" id="chatContainer">
        <div class="chat-header" id="chatHeader">
            <div style="display: flex; align-items: center;">
                <span>News Assistant</span>
            </div>
            <span id="toggleIcon" style="cursor: pointer;" onclick="toggleChat()">−</span>
        </div>
        <div class="chat-messages" id="chatMessages">
            <script>
                function loadMessages() {
                    const messages = JSON.parse(atob('""" + chat_messages_b64 + """'));
                    const container = document.getElementById('chatMessages');
                    container.innerHTML = '';
                    messages.forEach(msg => {
                        const div = document.createElement('div');
                        div.className = msg.role + '-message';
                        div.textContent = msg.content;
                        container.appendChild(div);
                    });
                    container.scrollTop = container.scrollHeight;
                }
                loadMessages();
            </script>
        </div>
        <div class="chat-input">
            <input type="text" id="chatInput" placeholder="Type your message..." />
            <button id="sendButton">Send</button>
        </div>
    </div>
    <button class="chat-toggle-button" onclick="toggleChat()">Chat</button>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            let isDragging = false;
            let currentX;
            let currentY;
            let initialX;
            let initialY;
            let xOffset = 0;
            let yOffset = 0;

            const container = document.getElementById('chatContainer');
            const header = document.getElementById('chatHeader');

            if (!container || !header) {
                console.error('Chat elements not found');
                return;
            }

            function dragStart(e) {
                if (e.type === "touchstart") {
                    initialX = e.touches[0].clientX - xOffset;
                    initialY = e.touches[0].clientY - yOffset;
                } else {
                    initialX = e.clientX - xOffset;
                    initialY = e.clientY - yOffset;
                }

                if (e.target === header || header.contains(e.target)) {
                    isDragging = true;
                }
            }

            function dragEnd(e) {
                initialX = currentX;
                initialY = currentY;
                isDragging = false;
            }

            function drag(e) {
                if (isDragging) {
                    e.preventDefault();

                    if (e.type === "touchmove") {
                        currentX = e.touches[0].clientX - initialX;
                        currentY = e.touches[0].clientY - initialY;
                    } else {
                        currentX = e.clientX - initialX;
                        currentY = e.clientY - initialY;
                    }

                    xOffset = currentX;
                    yOffset = currentY;

                    // Ensure the chat box stays within viewport bounds
                    const rect = container.getBoundingClientRect();
                    const viewportWidth = window.innerWidth;
                    const viewportHeight = window.innerHeight;

                    if (currentX < 0) currentX = 0;
                    if (currentY < 0) currentY = 0;
                    if (currentX + rect.width > viewportWidth) currentX = viewportWidth - rect.width;
                    if (currentY + rect.height > viewportHeight) currentY = viewportHeight - rect.height;

                    setTranslate(currentX, currentY, container);
                }
            }

            function setTranslate(xPos, yPos, el) {
                el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
            }

            // Add event listeners
            header.addEventListener("touchstart", dragStart, { passive: false });
            header.addEventListener("touchend", dragEnd, { passive: false });
            header.addEventListener("touchmove", drag, { passive: false });

            header.addEventListener("mousedown", dragStart, false);
            document.addEventListener("mousemove", drag, false);
            document.addEventListener("mouseup", dragEnd, false);

            // Toggle chat function
            window.toggleChat = function() {
                const container = document.getElementById('chatContainer');
                const icon = document.getElementById('toggleIcon');
                const toggleButton = document.querySelector('.chat-toggle-button');

                if (container.classList.contains('chat-minimized')) {
                    container.classList.remove('chat-minimized');
                    container.classList.remove('chat-hidden');
                    icon.textContent = '−';
                    toggleButton.style.display = 'none';
                } else {
                    container.classList.add('chat-minimized');
                    container.classList.add('chat-hidden');
                    icon.textContent = '+';
                    toggleButton.style.display = 'block';
                }
            }
        });

        // Add message handling
        window.addEventListener('load', function() {
            const chatInput = document.getElementById('chatInput');
            const sendButton = document.getElementById('sendButton');
            const chatMessages = document.getElementById('chatMessages');

            function sendMessage() {
                const message = chatInput.value.trim();
                if (message) {
                    // Add user message to chat
                    const userDiv = document.createElement('div');
                    userDiv.className = 'user-message';
                    userDiv.textContent = message;
                    chatMessages.appendChild(userDiv);

                    // Clear input
                    chatInput.value = '';

                    // Scroll to bottom
                    chatMessages.scrollTop = chatMessages.scrollHeight;

                    // Update URL with message parameter
                    const url = new URL(window.location.href);
                    url.searchParams.set('message', message);
                    window.history.pushState({}, '', url);

                    // Reload the page to process the message
                    window.location.reload();
                }
            }

            // Send message on button click
            sendButton.addEventListener('click', sendMessage);

            // Send message on Enter key
            chatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        });

    </script>
""", unsafe_allow_html=True)

# Page 1: Filters
if st.session_state.page == 'filters':
    st.header("Select Your News")

    # Topic filter
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
    selected_topic = st.selectbox("1. Select Topic", topics, index=0)

    # Outlet size filter
    outlet_sizes = ["All Sizes", "Large Outlets", "Medium Outlets", "Small Outlets"]
    selected_size = st.selectbox("2. Select News Outlet Size", outlet_sizes, index=0)

    # Political leaning filter
    political_leanings = ["All Views", "Left Leaning", "Center", "Right Leaning"]
    selected_leaning = st.selectbox("3. Select Political Leaning", political_leanings, index=0)

    # Search field before the "Show Results" button
    search_query = st.text_input("Search articles by keyword")

    # Store selections in session state
    if st.button("Show Results"):
        st.session_state.filters = {
            'topic': selected_topic if not search_query else "All",
            'size': selected_size if not search_query else "All Sizes",
            'leaning': selected_leaning if not search_query else "All Views",
            'search_query': search_query
        }
        st.session_state.page = 'results'

# Page 2: Results
else:
    # Add a "Back to Filters" button at the top
    if st.button("← Back to Filters"):
        st.session_state.page = 'filters'
        st.rerun()

    st.header("Your News Feed")

    if hasattr(st.session_state, 'filters'):
        # Fetch and filter articles
        articles = fetch_news(
            st.session_state.filters['topic'], 
            days_ago=5,  
            source_count=50  
        )

        if articles:
            # Generate summary for the topic
            with st.spinner("Generating topic summary..."):
                summary = summarize_articles(articles, st.session_state.filters['topic'])
                if summary['points']:
                    st.markdown("""
                        <div style="padding: 1rem; background-color: rgba(255, 255, 255, 0.9); 
                        border-radius: 10px; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <h3>Top Stories</h3>
                    """, unsafe_allow_html=True)

                    # Display each point as a clickable link if URL is available
                    for i, (point, url) in enumerate(zip(summary['points'], summary.get('urls', []))):
                        if url:
                            st.markdown(f"• [{point}]({url})")
                        else:
                            st.markdown(f"• {point}")

                    if not summary.get('is_ai', False):
                        st.info("Note: AI summarization temporarily unavailable")

                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("Could not generate summary")


            # Create DataFrame only once and filter efficiently
            df = pd.DataFrame(articles)

            # If there's a search query, ignore other filters and only search
            if st.session_state.filters.get('search_query'):
                search_terms = st.session_state.filters['search_query'].lower().split()
                if search_terms:
                    # Combine all terms into a single regex pattern for faster searching
                    pattern = '|'.join(search_terms)
                    mask = (
                        df['title'].str.lower().str.contains(pattern, na=False) |
                        df['content'].str.lower().str.contains(pattern, na=False)
                    )
                    df = df[mask]
                    # Sort search results by publication date
                    df = df.sort_values('published_at', ascending=False)
            else:
                # Only analyze and apply filters if not doing a text search
                if not df.empty:
                    # Analyze in smaller batches for better performance
                    batch_size = 10
                    for i in range(0, len(df), batch_size):
                        batch = df.iloc[i:i+batch_size]
                        for idx, row in batch.iterrows():
                            bias_metrics = analyze_bias(row['content'], row['source'])
                            df.at[idx, 'bias_score'] = bias_metrics['bias_score']
                            df.at[idx, 'sentiment'] = bias_metrics['sentiment']
                            df.at[idx, 'outlet_size'] = bias_metrics['outlet_size']
                            df.at[idx, 'political_bias'] = bias_metrics['political_bias']

                    # Apply filters only if not doing a text search
                    if st.session_state.filters['size'] != "All Sizes":
                        size_map = {
                            "Large Outlets": 1.0,
                            "Medium Outlets": 0.5,
                            "Small Outlets": 0.0
                        }
                        size_value = size_map[st.session_state.filters['size']]
                        df = df[df['outlet_size'] == size_value]

                    if st.session_state.filters['leaning'] != "All Views":
                        leaning_filters = {
                            "Left Leaning": lambda x: x < -0.2,
                            "Center": lambda x: abs(x) <= 0.2,
                            "Right Leaning": lambda x: x > 0.2
                        }
                        df = df[df['political_bias'].apply(leaning_filters[st.session_state.filters['leaning']])]

                    # Sort by outlet size only when we have analyzed the articles
                    df = df.sort_values('outlet_size', ascending=False)

            # Display all articles that match the criteria
            for _, article in df.iterrows():
                source_domain = article['source'].split('/')[0]
                logo_url = f"https://logo.clearbit.com/{source_domain}"

                st.markdown(f"""
                    <div class="news-card">
                        <img src="{logo_url}" class="news-logo">
                        <div class="news-content">
                            <h3>{article['title']}</h3>
                            <p>Source: {article['source']} | Published: {format_date(article['published_at'])}</p>
                            <p>Topic: {st.session_state.filters['topic']}</p>
                            <a href="{article['url']}" target="_blank">Read More</a>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            if len(df) == 0:
                st.warning("No articles found matching your criteria. Try adjusting your filters.")
        else:
            st.error("No articles found. Please try different filter selections.")
    else:
        st.warning("Please set your filters first.")
        if st.button("Go to Filters"):
            st.session_state.page = 'filters'

# Mobile-friendly footer with disclaimer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <p style='color: #666; font-size: 0.9em; max-width: 800px; margin: 0 auto;'>
            News Jungle aggregates content from various news sources for informational purposes only. 
            All articles remain the property of their respective publishers. We do not guarantee 
            the accuracy, completeness, or timeliness of any information presented. Please verify 
            all information with the original sources by following the provided links. News feeds 
            are updated regularly but may not reflect real-time changes.
        </p>
        <p style='color: #888; font-size: 0.8em; margin-top: 1rem;'>
            © 2025 News Jungle | Content Attribution: Respective Publishers
        </p>
    </div>
""", unsafe_allow_html=True)

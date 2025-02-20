import streamlit as st
from chatbot import NewsAssistant

def initialize_chat():
    """Initialize chat session state"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'news_assistant' not in st.session_state:
        st.session_state.news_assistant = NewsAssistant()

def display_chat_interface():
    """Display the chat interface in the sidebar"""
    initialize_chat()
    
    st.sidebar.title("News Assistant 🤖")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.sidebar.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.sidebar.chat_input("Ask about news..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get context from current filters
        context = st.session_state.get('filters', {})
        
        # Get bot response
        with st.sidebar.chat_message("assistant"):
            response = st.session_state.news_assistant.get_response(prompt, context)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

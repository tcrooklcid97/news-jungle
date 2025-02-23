import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from database import get_db_connection

def get_sentiment_distribution(df):
    """Calculate sentiment distribution from articles"""
    sentiment_counts = df['sentiment'].value_counts()
    fig = px.pie(
        values=sentiment_counts.values,
        names=sentiment_counts.index,
        title='News Sentiment Distribution'
    )
    return fig

def get_source_diversity(df):
    """Create source diversity visualization"""
    source_counts = df['source'].value_counts().head(10)
    fig = px.bar(
        x=source_counts.index,
        y=source_counts.values,
        title='Top News Sources',
        labels={'x': 'Source', 'y': 'Number of Articles'}
    )
    fig.update_layout(xaxis_tickangle=45)
    return fig

def get_topic_trends(df):
    """Visualize topic trends over time"""
    df['date'] = pd.to_datetime(df['published_at']).dt.date
    daily_counts = df.groupby('date').size().reset_index(name='count')
    fig = px.line(
        daily_counts,
        x='date',
        y='count',
        title='Article Volume Over Time'
    )
    return fig

def get_bias_distribution(df):
    """Visualize bias score distribution"""
    fig = px.histogram(
        df,
        x='bias_score',
        nbins=20,
        title='Distribution of Political Bias Scores',
        labels={'bias_score': 'Bias Score (-1: Left, 0: Center, 1: Right)'}
    )
    return fig

def display_analytics_dashboard():
    """Display the analytics dashboard"""
    st.title("News Analytics Dashboard")
    
    # Get data from database
    conn = get_db_connection()
    query = """
        SELECT title, content, source, published_at, bias_score, sentiment
        FROM articles
        WHERE published_at >= NOW() - INTERVAL '7 days'
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if len(df) == 0:
        st.warning("No data available for analysis in the selected time period.")
        return
        
    # Create layout
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment distribution
        st.plotly_chart(get_sentiment_distribution(df), use_container_width=True)
        # Topic trends
        st.plotly_chart(get_topic_trends(df), use_container_width=True)
        
    with col2:
        # Source diversity
        st.plotly_chart(get_source_diversity(df), use_container_width=True)
        # Bias distribution
        st.plotly_chart(get_bias_distribution(df), use_container_width=True)
    
    # Summary statistics
    st.subheader("Summary Statistics")
    st.markdown(f"""
    - Total Articles: {len(df)}
    - Unique Sources: {df['source'].nunique()}
    - Date Range: {df['published_at'].min().date()} to {df['published_at'].max().date()}
    - Most Common Source: {df['source'].mode().iloc[0]}
    """)

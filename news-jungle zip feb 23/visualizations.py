import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_bias_plot(df: pd.DataFrame) -> go.Figure:
    """
    Create a mobile-friendly interactive scatter plot of bias scores vs sentiment
    """
    fig = px.scatter(
        df,
        x='bias_score',
        y='sentiment',
        color='source',
        size=[20] * len(df),  # Larger points for touch
        hover_data=['title'],
        title='Bias Analysis by Source'
    )

    # Mobile-friendly layout
    fig.update_layout(
        title_x=0.5,  # Center title
        xaxis_title="Bias Score",
        yaxis_title="Sentiment",
        showlegend=True,
        height=300,  # Shorter height for mobile
        margin=dict(l=20, r=20, t=40, b=20),  # Tighter margins
        legend=dict(
            orientation="h",  # Horizontal legend
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        # Mobile-friendly interaction
        dragmode='pan',  # Better for touch
        clickmode='select'
    )

    # Touch-friendly axis
    fig.update_xaxes(tickangle=0)
    fig.update_yaxes(tickangle=0)

    return fig

def create_source_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Create a mobile-friendly bar chart showing distribution of articles by source
    """
    source_counts = df['source'].value_counts()

    fig = px.bar(
        x=source_counts.index,
        y=source_counts.values,
        title='Sources Overview',
        labels={'x': 'Source', 'y': 'Articles'}
    )

    # Mobile-friendly layout
    fig.update_layout(
        title_x=0.5,  # Center title
        height=300,  # Shorter height for mobile
        margin=dict(l=20, r=20, t=40, b=80),  # Space for labels
        xaxis_tickangle=45,  # Angled labels for better fit
        showlegend=False,
        # Touch-friendly
        dragmode='pan',
        clickmode='select'
    )

    # Responsive text size
    fig.update_traces(
        textposition='outside',
        textangle=0,
        textfont_size=12
    )

    return fig
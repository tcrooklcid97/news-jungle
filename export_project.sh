#!/bin/bash

# Create directory structure
mkdir -p news_jungle_export/{chatbot,database,news,utils}

# Copy main application files
cp main.py news_jungle_export/
cp pyproject.toml news_jungle_export/

# Copy chatbot files
cp chatbot.py news_jungle_export/chatbot/
cp chat_interface.py news_jungle_export/chatbot/

# Copy database files
cp database.py news_jungle_export/database/

# Copy news processing files
cp news_fetcher.py news_jungle_export/news/
cp bias_analyzer.py news_jungle_export/news/
cp news_summarizer.py news_jungle_export/news/

# Copy utility files
cp utils.py news_jungle_export/utils/

# Create zip archive
zip -r news_jungle_export.zip news_jungle_export/

# Clean up temporary directory
rm -rf news_jungle_export/

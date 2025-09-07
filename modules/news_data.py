import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from vnstock import Vnstock


@st.cache_data(ttl=1800)  # Cache for 30 minutes
def fetch_stock_news(ticker: str, limit: int = 5) -> list:
    """
    Fetch latest news for a specific stock ticker using vnstock
    
    Args:
        ticker (str): Stock ticker symbol
        limit (int): Maximum number of news items to fetch
        
    Returns:
        list: List of news items with structured data
    """
    try:
        # Create vnstock instance and fetch news
        vs = Vnstock(ticker)
        news_data = vs.stock(ticker).company.news()
        
        if news_data is None or len(news_data) == 0:
            return []
        
        # Limit the results
        news_data = news_data.head(limit)
        
        formatted_news = []
        for _, row in news_data.iterrows():
            # Parse published date
            pub_date = row.get('public_date', row.get('created_at', datetime.now()))
            if isinstance(pub_date, str):
                try:
                    pub_date = pd.to_datetime(pub_date)
                except:
                    pub_date = datetime.now()
            
            # Create clean content summary
            full_content = str(row.get('news_full_content', ''))
            short_content = str(row.get('news_short_content', ''))
            
            # Use short content or create summary from full content
            if short_content and short_content != 'nan':
                summary = short_content
            elif len(full_content) > 200:
                summary = full_content[:200] + '...'
            else:
                summary = full_content
            
            news_item = {
                'ticker': ticker,
                'title': str(row.get('news_title', 'No title')),
                'subtitle': str(row.get('news_sub_title', '')),
                'content': full_content,
                'summary': summary,
                'published_date': pub_date,
                'source': 'VnStock',
                'url': str(row.get('news_source_link', '')),
                'image_url': str(row.get('news_image_url', '')),
                'news_id': str(row.get('news_id', ''))
            }
            formatted_news.append(news_item)
        
        return formatted_news
        
    except Exception as e:
        st.warning(f"Error fetching news for {ticker}: {str(e)}")
        return []


@st.cache_data(ttl=1800)
def get_news_for_impact_stocks(impact_stocks: list, limit_per_stock: int = 3) -> dict:
    """
    Fetch news for multiple impact stocks
    
    Args:
        impact_stocks (list): List of stock ticker symbols
        limit_per_stock (int): Maximum news items per stock
        
    Returns:
        dict: Dictionary with ticker as key and news list as value
    """
    if not impact_stocks:
        return {}
    
    stock_news = {}
    total_stocks = len(impact_stocks)
    
    # Progress indicator for news fetching
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, ticker in enumerate(impact_stocks):
        status_text.text(f"📰 Fetching news for {ticker}... ({i+1}/{total_stocks})")
        
        # Fetch news for this ticker
        news_items = fetch_stock_news(ticker, limit_per_stock)
        
        if news_items:
            stock_news[ticker] = news_items
        
        # Update progress
        progress = (i + 1) / total_stocks
        progress_bar.progress(progress)
        
        # Rate limiting - wait between requests
        if i < total_stocks - 1:
            time.sleep(0.3)  # 300ms delay between requests
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    return stock_news


def format_news_data(stock_news: dict) -> pd.DataFrame:
    """
    Format news data into a pandas DataFrame for easier handling
    
    Args:
        stock_news (dict): Dictionary of stock news data
        
    Returns:
        pd.DataFrame: Formatted news data
    """
    if not stock_news:
        return pd.DataFrame()
    
    all_news = []
    for ticker, news_list in stock_news.items():
        for news_item in news_list:
            news_item['ticker'] = ticker
            all_news.append(news_item)
    
    if not all_news:
        return pd.DataFrame()
    
    df = pd.DataFrame(all_news)
    
    # Sort by published date (most recent first)
    if 'published_date' in df.columns:
        df['published_date'] = pd.to_datetime(df['published_date'])
        df = df.sort_values('published_date', ascending=False)
    
    return df


def get_relative_time(published_date) -> str:
    """
    Convert datetime to relative time string (e.g., '2 hours ago')
    
    Args:
        published_date: datetime object
        
    Returns:
        str: Relative time string
    """
    try:
        if isinstance(published_date, str):
            published_date = pd.to_datetime(published_date)
        
        now = datetime.now()
        diff = now - published_date
        
        if diff.days > 0:
            return f"{diff.days} ngày trước"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} giờ trước"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} phút trước"
        else:
            return "Vừa xong"
            
    except Exception:
        return "Unknown time"


def filter_recent_news(stock_news: dict, hours: int = 24) -> dict:
    """
    Filter news to show only recent items
    
    Args:
        stock_news (dict): Dictionary of stock news
        hours (int): Number of hours to look back
        
    Returns:
        dict: Filtered news dictionary
    """
    if not stock_news:
        return {}
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    filtered_news = {}
    
    for ticker, news_list in stock_news.items():
        recent_news = []
        for news_item in news_list:
            try:
                pub_date = news_item.get('published_date')
                if isinstance(pub_date, str):
                    pub_date = pd.to_datetime(pub_date)
                
                if pub_date and pub_date >= cutoff_time:
                    recent_news.append(news_item)
            except Exception:
                # Include news with invalid dates
                recent_news.append(news_item)
        
        if recent_news:
            filtered_news[ticker] = recent_news
    
    return filtered_news


def get_news_summary_stats(stock_news: dict) -> dict:
    """
    Get summary statistics about the news data
    
    Args:
        stock_news (dict): Dictionary of stock news
        
    Returns:
        dict: Summary statistics
    """
    if not stock_news:
        return {'total_stocks': 0, 'total_news': 0, 'latest_news': None}
    
    total_stocks = len(stock_news)
    total_news = sum(len(news_list) for news_list in stock_news.values())
    
    # Find latest news
    latest_news = None
    latest_date = None
    
    for ticker, news_list in stock_news.items():
        for news_item in news_list:
            try:
                pub_date = news_item.get('published_date')
                if isinstance(pub_date, str):
                    pub_date = pd.to_datetime(pub_date)
                
                if latest_date is None or (pub_date and pub_date > latest_date):
                    latest_date = pub_date
                    latest_news = news_item
            except Exception:
                continue
    
    return {
        'total_stocks': total_stocks,
        'total_news': total_news,
        'latest_news': latest_news,
        'latest_date': latest_date
    }
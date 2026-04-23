from flask import Flask, render_template, request, session
import requests
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download required NLTK data
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

app = Flask(__name__)
app.secret_key = 'secret123'
sia = SentimentIntensityAnalyzer()

# Global storage for articles by category
articles_cache = {}
API_KEY = 'pub_adafdf32f2444525b9772637f7776d0d'  # Get free key at https://newsdata.io/

def get_sentiment(text):
    """Analyze sentiment of text using VADER - returns positive/negative/neutral"""
    if not text or len(text.strip()) == 0:
        return {'compound': 0, 'sentiment': 'neutral', 'score': 0}
    
    try:
        # Use VADER for sentiment analysis
        scores = sia.polarity_scores(text)
        compound = scores['compound']
        
        # Classify sentiment based on compound score
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'compound': round(compound, 2),
            'sentiment': sentiment,
            'score': scores
        }
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return {'compound': 0, 'sentiment': 'neutral', 'score': 0}

def format_articles(articles):
    """Transform Newsdata.io articles to expected format with NLP sentiment analysis"""
    if not articles or not isinstance(articles, list):
        return []
    
    formatted = []
    for article in articles:
        if isinstance(article, dict) and article.get('title'):  # Skip articles without title
            # Combine title and description for sentiment analysis
            text_to_analyze = (article.get('title', '') + ' ' + article.get('description', '')).strip()
            sentiment_data = get_sentiment(text_to_analyze)
            
            formatted.append({
                'title': article.get('title', 'No Title'),
                'description': article.get('description', 'No Description'),
                'source_name': article.get('source_name', 'Unknown Source'),
                'pubDate': article.get('pubDate', 'Unknown Date'),
                'image_url': article.get('image_url', ''),
                'link': article.get('link', '#'),
                'sentiment': sentiment_data['sentiment'],
                'sentiment_score': sentiment_data['compound']
            })
    return formatted

def get_news(category):
    """Fetch news from Newsdata.io API - India focused in Hindi and English"""
    try:
        # Map categories to keywords for searching
        keywords = {
            'sports': 'sports cricket football',
            'business': 'business economy market stocks',
            'technology': 'technology tech software IT',
            'science': 'science research discovery',
            'health': 'health medicine healthcare',
            'general': 'news india'
        }
        
        search_term = keywords.get(category, 'news')
        
        # Fetch news for specific category from India in Hindi and English
        url = f"https://newsdata.io/api/1/latest?q={search_term}&country=IN&language=hi,en&apikey={API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, dict):
            articles = data.get('results', [])
        else:
            articles = []
        
        return format_articles(articles)
    except Exception as e:
        print(f"Error fetching news for {category}: {e}")
        return []

@app.route('/')
def index():
    articles = get_news('general')
    articles_cache['general'] = articles
    case = {
        'articles': articles
    }
    return render_template('index.html',cases = case)
@app.route('/sports')
def sports():
    articles = get_news('sports')
    articles_cache['sports'] = articles
    case = {
        'articles': articles
    }
    return render_template('sports.html',cases = case)

@app.route('/business')
def business():
    articles = get_news('business')
    articles_cache['business'] = articles
    case = {
        'articles': articles
    }
    return render_template('business.html',cases = case)

@app.route('/technology')
def technology():
    articles = get_news('technology')
    articles_cache['technology'] = articles
    case = {
        'articles': articles
    }
    return render_template('tech.html',cases = case)

@app.route('/science')
def science():
    articles = get_news('science')
    articles_cache['science'] = articles
    case = {
        'articles': articles
    }
    return render_template('science.html',cases = case)

@app.route('/health')
def health():
    articles = get_news('health')
    articles_cache['health'] = articles
    case = {
        'articles': articles
    }
    return render_template('health.html',cases = case)

@app.route('/article/<category>/<int:article_id>')
def article_detail(category, article_id):
    """Display full article details"""
    articles = articles_cache.get(category, [])
    
    if article_id < 0 or article_id >= len(articles):
        return "Article not found", 404
    
    article = articles[article_id]
    return render_template('article_detail.html', article=article, category=category)

if __name__ == '__main__':
    app.run(debug=True)
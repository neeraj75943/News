from flask import Flask, render_template, request, session
import requests


app = Flask(__name__)
app.secret_key = 'secret123'

# Global storage for articles by category
articles_cache = {}
API_KEY = 'pub_adafdf32f2444525b9772637f7776d0d'  # Get free key at https://newsdata.io/

def format_articles(articles):
    """Transform Newsdata.io articles to expected format"""
    if not articles or not isinstance(articles, list):
        return []
    
    formatted = []
    for article in articles:
        if isinstance(article, dict) and article.get('title'):  # Skip articles without title
            formatted.append({
                'title': article.get('title', 'No Title'),
                'description': article.get('description', 'No Description'),
                'source_name': article.get('source_name', 'Unknown Source'),
                'pubDate': article.get('pubDate', 'Unknown Date'),
                'image_url': article.get('image_url', ''),
                'link': article.get('link', '#')
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
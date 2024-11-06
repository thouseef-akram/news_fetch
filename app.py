from flask import Flask, render_template, request, jsonify
from gnews import GNews
from datetime import datetime

app = Flask(__name__)

# Function to parse date from string format returned by GNews
def parse_date(date_str):
    return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')

def sort_by_date(data):
    sorted_data = sorted(data, key=lambda x: parse_date(x['published date']), reverse=True)
    return sorted_data

# Home route to render the index.html template
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle news category search and return results
@app.route('/predict', methods=['POST'])
def category_news():
    city = request.form.get('City')
    news = request.form.get('news_cat')
    
    # Check if city and news are provided
    if not city or not news:
        return jsonify({'error': 'City and News Category are required fields.'}), 400

    google_news = GNews(language='en', country=city, period='4d', max_results=10)
    
    # Combine keyword and city for a more specific search
    search_keyword = f"{news} {city}"
    
    # Fetch news articles based on combined keyword
    json_resp = google_news.get_news(search_keyword)
    
    # Check if any news articles were found
    if not json_resp:
        return jsonify({'error': 'No articles found for the given city and news category.'}), 404
    
    # Sort and filter articles by date and city in title
    sorted_news = sort_by_date(json_resp)
    results = [
        {
            'url': news_item['url'],
            'title': news_item['title'],
            'publisher': news_item['publisher']['title'],
            'published_date': news_item['published date']
        }
        for news_item in sorted_news if city.lower() in news_item['title'].lower()
    ]
    
    # Return results or indicate no matches if city name not in any titles
    if not results:
        return jsonify({'error': 'No articles found with the city name in the title.'}), 404
    
    return jsonify({'News': results})

if __name__ == '__main__':
    app.run(debug=True)
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from gnews import GNews
from datetime import datetime
import os

# Initialize FastAPI app
app = FastAPI()

# Set up templates folder
templates = Jinja2Templates(directory="templates")

# Function to parse date from string format returned by GNews
def parse_date(date_str):
    return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S GMT')

def sort_by_date(data):
    sorted_data = sorted(data, key=lambda x: parse_date(x['published date']), reverse=True)
    return sorted_data

# Home route to render the index.html template
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Route to handle news category search and return results
@app.post("/predict")
async def category_news(City: str = Form(...), news_cat: str = Form(...)):
    # Check if city and news are provided
    if not City or not news_cat:
        return JSONResponse(content={'error': 'City and News Category are required fields.'}, status_code=400)

    google_news = GNews(language='en', country=City, period='4d', max_results=10)
    
    # Combine keyword and city for a more specific search
    search_keyword = f"{news_cat} {City}"
    
    # Fetch news articles based on combined keyword
    json_resp = google_news.get_news(search_keyword)
    
    # Check if any news articles were found
    if not json_resp:
        return JSONResponse(content={'error': 'No articles found for the given city and news category.'}, status_code=404)
    
    # Sort and filter articles by date and city in title
    sorted_news = sort_by_date(json_resp)
    results = [
        {
            'url': news_item['url'],
            'title': news_item['title'],
            'publisher': news_item['publisher']['title'],
            'published_date': news_item['published date']
        }
        for news_item in sorted_news if City.lower() in news_item['title'].lower()
    ]
    
    # Return results or indicate no matches if city name not in any titles
    if not results:
        return JSONResponse(content={'error': 'No articles found with the city name in the title.'}, status_code=404)
    
    return JSONResponse(content={'News': results})

# To run the app, use this command: `uvicorn app_fastapi:app --reload`

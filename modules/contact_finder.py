import requests
from config import SERPAPI_KEY

def find_ciso_linkedin(company_name):
    query = f'site:linkedin.com/in "CISO" "{company_name}"'
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 3
    }
    res = requests.get(url, params=params)
    people = []
    for result in res.json().get("organic_results", []):
        people.append({
            "name": result.get("title"),
            "title": "CISO",
            "linkedin": result.get("link"),
            "email": "Unknown"
        })
    return people
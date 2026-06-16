import requests
from config import SERPAPI_KEY


def find_ciso_linkedin(company_name):
    query = f'site:linkedin.com/in "CISO" "{company_name}"'
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 3,
    }

    try:
        res = requests.get(url, params=params, timeout=20)
        res.raise_for_status()
        results = res.json().get("organic_results", [])
    except Exception as e:
        print(f"Error finding CISO contacts for {company_name}: {e}")
        return []

    people = []
    for result in results:
        link = result.get("link")
        if not link:
            continue
        people.append({
            "name": result.get("title", "Unknown"),
            "title": "CISO",
            "linkedin": link,
            "email": "Unknown",
        })
    return people

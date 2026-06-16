import requests
from config import SERPAPI_KEY


def search_breach_articles(query="data breach OR cyber attack", tbs="qdr:d", num_results=10):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "tbm": "nws",
        "tbs": tbs,
        "api_key": SERPAPI_KEY,
        "num": num_results,
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        results = response.json()

        if "news_results" not in results:
            print("SerpAPI returned no news_results")
            return []

        articles = []
        for article in results["news_results"]:
            link = article.get("link")
            if not link:
                continue
            articles.append({
                "url": link,
                "source": article.get("source", "Unknown"),
                "date": article.get("date", "Unknown"),
            })

        return articles

    except Exception as e:
        print(f"Error pulling articles from SerpAPI: {e}")
        return []

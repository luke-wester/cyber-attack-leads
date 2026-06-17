import requests
from config import SERPAPI_KEY


def _clean_result_title(title):
    if not title:
        return "Unknown"
    return title.split(" | ")[0].split(" - LinkedIn")[0].strip()


def _company_terms(company_name):
    stopwords = {"inc", "inc.", "corp", "corp.", "corporation", "co", "co.", "company", "llc", "ltd", "ltd."}
    cleaned = company_name.lower().replace(",", " ").replace(".", " ")
    return [part for part in cleaned.split() if part and part not in stopwords]


def _company_matches(result, company_name):
    haystack = " ".join([
        result.get("title", ""),
        result.get("snippet", ""),
        result.get("displayed_link", ""),
    ]).lower()
    terms = _company_terms(company_name)
    return bool(terms) and all(term in haystack for term in terms[:2])


def find_ciso_linkedin(company_name):
    query = (
        'site:linkedin.com/in '
        f'("Chief Information Security Officer" OR CISO) "{company_name}" '
        '-jobs -job -hiring'
    )
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 5,
    }

    try:
        res = requests.get(url, params=params, timeout=20)
        res.raise_for_status()
        results = res.json().get("organic_results", [])
    except Exception as e:
        print(f"Error finding CISO contacts for {company_name}: {e}")
        return []

    for result in results:
        link = result.get("link")
        if not link or "linkedin.com/in" not in link:
            continue
        if not _company_matches(result, company_name):
            continue
        return [{
            "name": _clean_result_title(result.get("title")),
            "title": "CISO",
            "linkedin": link,
            "email": "Unknown",
        }]

    return []

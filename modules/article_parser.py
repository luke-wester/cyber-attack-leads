import openai
from newspaper import Article
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def extract_company_from_article(url):
    article = Article(url)
    try:
        article.download()
        article.parse()
    except Exception as e:
        print(f"Download error: {e}")
        return None, None
    return ask_gpt_for_company(article.text), article.text

def ask_gpt_for_company(content):
    prompt = (
        "Extract the name of the company affected by the breach in this article:\n"
        f"{content[:3000]}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None

def summarize_breach(content):
    prompt = (
        "Summarize the following breach in one concise sentence for a sales rep to understand what happened:\n"
        f"{content}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Summary not available"

def score_breach_severity(summary):
    prompt = (
        "Score this breach summary from 1 to 100 based on how serious the breach sounds:\n"
        f"{summary}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10
        )
        score = int(''.join(filter(str.isdigit, response.choices[0].message.content)))
        return max(1, min(score, 100))
    except Exception:
        return 50

def generate_email_draft(name, title, company, breach_summary, source, date):
    prompt = (
        f"Write a short, professional cold outreach email to {name}, a {title} at {company}. "
        f"The company recently had a breach reported by {source} on {date} with the following summary:\n"
        f"\"{breach_summary}\"\n\n"
        "The tone should be helpful, concise, and friendly. Include a clear reason for reaching out and an invitation to connect. "
        "End with the sender offering value, not a sales pitch. No more than 4 sentences."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Email draft unavailable."

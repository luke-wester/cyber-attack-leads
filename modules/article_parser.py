import openai
from newspaper import Article, Config
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY


def article_config():
    config = Config()
    config.browser_user_agent = "CyberAttackLeads/1.0"
    config.request_timeout = 12
    return config


def clean_company_name(company):
    if not company:
        return None
    cleaned = company.strip().splitlines()[0].strip(' \"\'.:;,-')
    prefixes = [
        "the affected company is ",
        "the impacted company is ",
        "affected company: ",
        "impacted company: ",
        "company: ",
    ]
    lowered = cleaned.lower()
    for prefix in prefixes:
        if lowered.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip(' \"\'.:;,-')
            break
    return cleaned or None


def extract_company_from_article(url):
    article = Article(url, config=article_config())
    try:
        article.download()
        article.parse()
    except Exception as e:
        print(f"Download error for {url}: {e}")
        return None, None
    if not article.text:
        return None, None
    return clean_company_name(ask_gpt_for_company(article.text)), article.text


def ask_gpt_for_company(content):
    prompt = (
        "Extract the name of the company affected by the breach in this article. "
        "Return only the company name:\n"
        f"{content[:3000]}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            request_timeout=20,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI company extraction error: {e}")
        return None


def summarize_breach(content):
    prompt = (
        "Summarize the following breach in one concise sentence for a sales rep to understand what happened:\n"
        f"{content[:5000]}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80,
            request_timeout=20,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI summary error: {e}")
        return "Summary not available"


def score_breach_severity(summary):
    prompt = (
        "Score this breach summary from 1 to 100 based on how serious the breach sounds. "
        "Return only the number:\n"
        f"{summary}"
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            request_timeout=20,
        )
        digits = ''.join(filter(str.isdigit, response.choices[0].message.content))
        score = int(digits) if digits else 50
        return max(1, min(score, 100))
    except Exception as e:
        print(f"OpenAI severity score error: {e}")
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
            max_tokens=200,
            request_timeout=20,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI email draft error: {e}")
        return "Email draft unavailable."

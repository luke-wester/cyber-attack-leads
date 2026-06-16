import io
import os

import pandas as pd
from flask import Flask, render_template_string, request, send_file

from config import missing_required_keys
from modules.article_parser import (
    extract_company_from_article,
    generate_email_draft,
    score_breach_severity,
    summarize_breach,
)
from modules.contact_finder import find_ciso_linkedin
from modules.news_search import search_breach_articles

app = Flask(__name__)

RECENCY_MAP = {
    "Past 24 hours": "qdr:d",
    "Past 3 days": "cdr:1,2",
    "Past week": "qdr:w",
    "Past 2 weeks": "cdr:1,14",
    "Past month": "qdr:m",
    "Past 90 days": "cdr:1,90",
}

PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cyber Attack Leads</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #17202a;
      --muted: #667085;
      --line: #d7dde5;
      --surface: #f6f8fb;
      --accent: #0f766e;
      --accent-dark: #115e59;
      --danger: #b42318;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #ffffff;
    }
    main {
      width: min(1120px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 42px 0 56px;
    }
    header {
      display: flex;
      justify-content: space-between;
      gap: 24px;
      align-items: end;
      padding-bottom: 24px;
      border-bottom: 1px solid var(--line);
    }
    h1 { margin: 0 0 8px; font-size: clamp(2rem, 4vw, 3.5rem); line-height: 1; }
    p { margin: 0; color: var(--muted); line-height: 1.55; }
    form.controls {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      align-items: end;
      padding: 24px 0;
    }
    label { display: grid; gap: 7px; font-weight: 700; font-size: 0.92rem; }
    select, input {
      min-width: 180px;
      min-height: 42px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 11px;
      font: inherit;
      background: white;
    }
    button, .download-link {
      min-height: 42px;
      border: 0;
      border-radius: 6px;
      padding: 10px 14px;
      font: inherit;
      font-weight: 800;
      color: white;
      background: var(--accent);
      cursor: pointer;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
    button:hover, .download-link:hover { background: var(--accent-dark); }
    .alert {
      margin-top: 20px;
      padding: 14px 16px;
      border-radius: 6px;
      border: 1px solid #f1c8c4;
      color: var(--danger);
      background: #fff4f2;
      font-weight: 700;
    }
    .summary {
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
      padding: 18px 0;
      border-top: 1px solid var(--line);
    }
    .table-wrap { overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; }
    table { width: 100%; border-collapse: collapse; min-width: 900px; }
    th, td { padding: 11px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
    th { background: var(--surface); font-size: 0.84rem; text-transform: uppercase; letter-spacing: 0.04em; }
    td { font-size: 0.92rem; }
    tr:last-child td { border-bottom: 0; }
    a { color: #075985; }
    .empty { padding: 24px; background: var(--surface); border-radius: 8px; color: var(--muted); }
    @media (max-width: 720px) {
      header, .summary { display: grid; align-items: start; }
      form.controls { display: grid; }
      select, input, button { width: 100%; }
    }
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>Cyber Attack Leads</h1>
        <p>Generate ranked outreach leads from recent cybersecurity breach and cyber attack news.</p>
      </div>
    </header>

    {% if error %}
      <div class="alert">{{ error }}</div>
    {% endif %}

    <form class="controls" method="post" action="/generate">
      <label>
        Time range
        <select name="recency">
          {% for label in recency_labels %}
            <option value="{{ label }}" {% if label == selected_recency %}selected{% endif %}>{{ label }}</option>
          {% endfor %}
        </select>
      </label>
      <label>
        Articles to analyze
        <input name="article_count" type="number" min="5" max="50" value="{{ article_count }}">
      </label>
      <button type="submit">Generate lead list</button>
    </form>

    {% if rows is not none %}
      <section class="summary">
        <p>{{ rows|length }} lead{{ '' if rows|length == 1 else 's' }} generated.</p>
        {% if csv_text %}
          <form method="post" action="/download">
            <textarea name="csv_text" hidden>{{ csv_text }}</textarea>
            <button type="submit">Download CSV</button>
          </form>
        {% endif %}
      </section>

      {% if rows %}
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Title</th>
                <th>Company</th>
                <th>Severity</th>
                <th>Source</th>
                <th>Article</th>
                <th>Breach Summary</th>
              </tr>
            </thead>
            <tbody>
              {% for row in rows %}
                <tr>
                  <td>{{ row.name }}</td>
                  <td>{{ row.title }}</td>
                  <td>{{ row.company }}</td>
                  <td>{{ row.severity_score }}</td>
                  <td>{{ row.source }}</td>
                  <td><a href="{{ row.article }}" target="_blank" rel="noreferrer">Open</a></td>
                  <td>{{ row.breach_summary }}</td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      {% else %}
        <div class="empty">No leads found. Try a broader time range or fewer article filters.</div>
      {% endif %}
    {% endif %}
  </main>
</body>
</html>
"""


def clamp_article_count(raw_value):
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return 10
    return max(5, min(value, 50))


def generate_leads(recency_label, article_count):
    articles = search_breach_articles(
        tbs=RECENCY_MAP.get(recency_label, RECENCY_MAP["Past 24 hours"]),
        num_results=article_count,
    )
    output = []

    for article in articles:
        url = article["url"]
        source = article.get("source", "Unknown")
        date = article.get("date", "Unknown")

        company, full_text = extract_company_from_article(url)
        if not company or not full_text:
            continue

        breach_summary = summarize_breach(full_text)
        severity_score = score_breach_severity(breach_summary)
        people = find_ciso_linkedin(company)

        for person in people:
            email_draft = generate_email_draft(
                name=person.get("name", "there"),
                title=person.get("title", ""),
                company=company,
                breach_summary=breach_summary,
                source=source,
                date=date,
            )
            person.update({
                "company": company,
                "article": url,
                "source": source,
                "date": date,
                "summary": full_text[:300],
                "breach_summary": breach_summary,
                "severity_score": severity_score,
                "fortune_500": "TBD",
                "email_draft": email_draft,
            })
            output.append(person)

    return output


def rows_to_csv(rows):
    if not rows:
        return ""
    df = pd.DataFrame(rows)
    df.drop_duplicates(subset=["company", "name", "linkedin"], inplace=True)
    df.sort_values(by=["severity_score"], ascending=False, inplace=True)
    return df.to_csv(index=False)


def render_page(error=None, rows=None, csv_text="", selected_recency="Past 24 hours", article_count=10):
    return render_template_string(
        PAGE_TEMPLATE,
        error=error,
        rows=rows,
        csv_text=csv_text,
        selected_recency=selected_recency,
        article_count=article_count,
        recency_labels=list(RECENCY_MAP.keys()),
    )


@app.get("/")
def index():
    return render_page()


@app.post("/generate")
def generate():
    missing_keys = missing_required_keys()
    recency_label = request.form.get("recency", "Past 24 hours")
    article_count = clamp_article_count(request.form.get("article_count"))

    if missing_keys:
        return render_page(
            error="Missing required environment variables: " + ", ".join(missing_keys),
            selected_recency=recency_label,
            article_count=article_count,
        ), 500

    rows = generate_leads(recency_label, article_count)
    csv_text = rows_to_csv(rows)
    return render_page(
        rows=rows,
        csv_text=csv_text,
        selected_recency=recency_label,
        article_count=article_count,
    )


@app.post("/download")
def download():
    csv_text = request.form.get("csv_text", "")
    buffer = io.BytesIO(csv_text.encode("utf-8"))
    return send_file(
        buffer,
        mimetype="text/csv",
        as_attachment=True,
        download_name="cyber-attack-leads.csv",
    )


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)

import streamlit as st
from modules.news_search import search_breach_articles
from modules.article_parser import (
    extract_company_from_article,
    summarize_breach,
    generate_email_draft,
    score_breach_severity,
)
from modules.contact_finder import find_ciso_linkedin
from modules.output_writer import write_to_csv
from config import missing_required_keys

st.set_page_config(page_title="Cyber Attack Leads", layout="centered")

st.title("Cyber Attack Leads")
st.markdown("Get a ranked, downloadable list of leads from recent cybersecurity breach and cyber attack news.")

st.markdown("📥 **CSV includes names, titles, emails, LinkedIn profiles, breach summaries, and personalized outreach drafts.**")

recency_map = {
    "Past 24 hours": "qdr:d",
    "Past 3 days": "cdr:1,2",
    "Past week": "qdr:w",
    "Past 2 weeks": "cdr:1,14",
    "Past month": "qdr:m",
    "Past 90 days": "cdr:1,90"
}

recency = st.selectbox("Time range for breaches:", list(recency_map.keys()))
article_count = st.slider("Number of articles to analyze:", min_value=5, max_value=50, value=10)

if st.button("🚀 Generate Lead List"):
    missing_keys = missing_required_keys()
    if missing_keys:
        st.error("Missing required environment variables: " + ", ".join(missing_keys))
        st.stop()

    st.info("Running... This may take 30-45 seconds.")

    articles = search_breach_articles(tbs=recency_map[recency], num_results=article_count)
    st.write(f"📰 Found {len(articles)} articles")

    output = []

    for i, article in enumerate(articles, start=1):
        url = article["url"]
        source = article.get("source", "Unknown")
        date = article.get("date", "Unknown")

        company, full_text = extract_company_from_article(url)
        if not company:
            continue

        breach_summary = summarize_breach(full_text)
        severity_score = score_breach_severity(breach_summary)

        headline = f"{i}. {company} - {breach_summary[:100]}..." if breach_summary else f"{i}. {company}"
        st.markdown(f"**{headline}**")
        st.markdown(f"[🔗 Read more]({url}) - {source}, {date}")
        st.markdown(f"Severity: **{severity_score}/100**")
        
        people = find_ciso_linkedin(company)

        st.markdown(f"👤 {len(people)} contact(s) found. Stored in CSV.")
        st.markdown("---")

        for person in people:
            email_draft = generate_email_draft(
                name=person.get("name", "there"),
                title=person.get("title", ""),
                company=company,
                breach_summary=breach_summary,
                source=source,
                date=date
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
                "email_draft": email_draft
            })
            output.append(person)

    st.markdown("### 📦 Download the CSV for full lead details")
    if output:
        write_to_csv(output)
        with open("lead_list.csv", "rb") as file:
            st.download_button("📥 Download CSV", file, file_name="cyber-attack-leads.csv")
    else:
        st.warning("No leads found. Try adjusting the filters or checking the API keys.")

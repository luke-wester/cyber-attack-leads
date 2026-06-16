# Cyber Attack Leads

**Cyber Attack Leads** is an AI-powered lead generation app. It automatically discovers recent cybersecurity breaches and cyber attacks, extracts affected companies, identifies their security leadership (like CISOs), and generates personalized cold outreach drafts - all downloadable in a single CSV.

---

## 🔧 How It Works

1. **Searches breach news** using SerpAPI (Google News engine)
2. **Parses articles** using newspaper3k to extract the full text
3. **Extracts the affected company** using GPT-3.5
4. **Generates a 1-sentence breach summary** using GPT-3.5
5. **Scores breach severity from 1 to 100**
   - We ask GPT:  
     > “Score this breach summary from 1 to 100 based on how serious the breach sounds.”
   - The AI evaluates the **type of data exposed**, **scale of the breach**, **public fallout**, and **regulatory implications**.
   - Example:  
     - “2 million medical records breached at a national hospital” → Score ~95  
     - “A few user logins leaked at a small startup” → Score ~35
6. **Finds CISO contacts** via Google-powered LinkedIn searches using SerpAPI
7. **Generates a personalized email draft** to that contact using GPT-3.5
8. **Exports everything to a downloadable CSV**

---

## 📥 What You Get in the CSV

| Column | Description |
|--------|-------------|
| Name | Contact's name |
| Title | Typically CISO or similar |
| Company | Breached company name |
| LinkedIn | Link to LinkedIn profile |
| Email | Placeholder for email (can be enriched) |
| Article | Link to breach news story |
| Source | Publishing company (e.g. Wired, TechCrunch) |
| Date | Publish date of the article |
| Breach Summary | 1-sentence description of what happened |
| Severity Score | 1–100 score based on breach impact |
| Email Draft | Personalized cold email tailored to this contact and breach |

---

## 💡 Features

- Select time range: 24h, 3d, 7d, 14d, 30d, 90d
- Control how many articles to analyze
- Real-time progress logging in the app
- Clean UI with plain-English summaries
- Flask web interface ready for Render hosting

---

## 🔍 Technologies Used

- **Flask** - App interface
- **OpenAI GPT-3.5** - Breach summaries, severity scores, and email drafts
- **SerpAPI** - Google News + LinkedIn search
- **newspaper3k** - Article parsing
- **pandas** - CSV generation

---

## 🚀 How to Run It

```bash
cd ~/Documents/cyber-attack-leads
python3 app.py
```

## Deploy on Render

This repo includes a `render.yaml` Blueprint for a Render web service. During Blueprint creation, Render prompts for these secret environment variables:

- `SERPAPI_KEY`
- `OPENAI_API_KEY`

The service uses `pip install -r requirements.txt` to build and starts the Flask app with Gunicorn.

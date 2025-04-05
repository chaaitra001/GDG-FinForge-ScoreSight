from newspaper import Article
from transformers import pipeline
import requests

API_KEY = "AIzaSyD_KxObUQ3nOkTdOzZhrt-dtB-FklMxxmE"
SEARCH_ENGINE_ID = "3007eed1251e043d9"
NUM_RESULTS = 5

# Load zero-shot classifier once
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# ESG category sentiment-based pairs
esg_labels = {
    "Environmental": [f"{industry} promotes sustainability", "causes environmental harm"],
    "Social": [f"{industry} improves social equity", "harms social welfare"],
    "Governance": [f"{industry} supports ethical governance", "promotes corruption"]
}

# Google Search Article Fetcher
def fetch_articles(query, max_results=NUM_RESULTS):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "num": max_results
    }

    response = requests.get(url, params=params)
    items = response.json().get("items", [])
    articles = []

    for item in items:
        title = item.get("title")
        link = item.get("link")
        snippet = item.get("snippet", "")
        try:
            a = Article(link)
            a.download()
            a.parse()
            text = a.text
        except:
            text = snippet
        articles.append({"title": title, "url": link, "text": text})

    return articles

# Score article batch on ESG dimension
def score_esg_articles(articles, label_pair):
    if not articles:
        return 0.0
    scores = []
    for article in articles:
        result = classifier(article["text"][:1000], candidate_labels=label_pair)
        score = (result["scores"][0] - result["scores"][1]) * 10
        scores.append(score)
    return round(sum(scores) / len(scores), 3)

# Score freeform user decision
def score_decision(text):
    enriched = f"The company plans to {text.lower()}"
    scores = {}
    for category, label_pair in esg_labels.items():
        result = classifier(enriched, candidate_labels=label_pair)
        score = (result["scores"][0] - result["scores"][1]) * 10
        scores[category] = round(score, 3)
    return scores

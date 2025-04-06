from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import pipeline
from newspaper import Article
import requests
import os
import random

ALPHA_API_KEY = "6OO3MTTFEK1ASVCJ"
GOOGLE_API_KEY = "AIzaSyD_KxObUQ3nOkTdOzZhrt-dtB-FklMxxmE"
SEARCH_ENGINE_ID = "3007eed1251e043d9"
NUM_RESULTS = 5

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

class DecisionComparisonRequest(BaseModel):
    industry: str
    option_a: str
    option_b: str

class DecisionRequest(BaseModel):
    industry: str
    decision: str

class ProfitabilityRequest(BaseModel):
    description: str

profitability_labels = ["very profitable", "moderately profitable", "neutral", "not profitable", "causes losses"]


def get_esg_label_pairs(industry: str):
    return {
        "Environmental": [f"{industry} promotes sustainability", "causes environmental harm"],
        "Social": [f"{industry} improves social equity", "harms social welfare"],
        "Governance": [f"{industry} supports ethical governance", "promotes corruption"]
    }


def score_esg_category(text: str, label_pair: list) -> float:
    result = classifier(text, candidate_labels=label_pair)
    scores = dict(zip(result["labels"], result["scores"]))
    pos_label, neg_label = label_pair
    final_score = (scores.get(pos_label, 0) - scores.get(neg_label, 0)) * 10
    return max(-10, min(10, round(final_score, 3)))


def get_esg_scores(text: str, industry: str) -> dict:
    enriched_text = f"In the {industry} industry, the company plans to {text.lower()}."
    label_pairs = get_esg_label_pairs(industry)
    scores = {}
    for category, pair in label_pairs.items():
        scores[category] = score_esg_category(enriched_text, pair)
    return scores


def compute_overall_score(scores: dict) -> float:
    return round(sum(scores.values()) / len(scores), 3)


@app.post("/compare-decisions")
def compare_decisions(data: DecisionComparisonRequest):
    score_a = get_esg_scores(data.option_a, data.industry)
    score_b = get_esg_scores(data.option_b, data.industry)
    return {
        "industry": data.industry,
        "option_a": {
            "description": data.option_a,
            "predicted_esg_score": score_a,
            "overall_score": compute_overall_score(score_a)
        },
        "option_b": {
            "description": data.option_b,
            "predicted_esg_score": score_b,
            "overall_score": compute_overall_score(score_b)
        }
    }


@app.post("/simulate")
def simulate_esg_impact(data: DecisionRequest):
    return {
        "industry": data.industry,
        "decision": data.decision,
        "predicted_esg_score": get_esg_scores(data.decision, data.industry)
    }

def predict_esg_from_decision(decision: str, industry: str):
    enriched_text = f"In the {industry} industry, the company plans to {decision.lower()}."
    label_pairs = get_esg_label_pairs(industry)
    scores = {}
    for category, pair in label_pairs.items():
        result = classifier(enriched_text, candidate_labels=pair)
        pos_label, neg_label = pair
        pos_index = result["labels"].index(pos_label)
        neg_index = result["labels"].index(neg_label)
        final_score = (result["scores"][pos_index] - result["scores"][neg_index]) * 10
        scores[category] = round(final_score, 3)
    return scores

API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyD_KxObUQ3nOkTdOzZhrt-dtB-FklMxxmE")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID", "3007eed1251e043d9")
NUM_RESULTS = 5


def fetch_articles(query: str, max_results=NUM_RESULTS):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": SEARCH_ENGINE_ID,
        "q": query,
        "num": max_results
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    items = response.json().get("items", [])
    articles = []
    for item in items:
        title = item.get("title")
        link = item.get("link")
        snippet = item.get("snippet", "")
        try:
            article = Article(link)
            article.download()
            article.parse()
            text = article.text
        except Exception:
            text = snippet
        articles.append({"title": title, "url": link, "text": text})
    return articles


def score_esg_article(text: str, industry: str) -> dict:
    label_pairs = get_esg_label_pairs(industry)
    scores = {}
    for category, pair in label_pairs.items():
        result = classifier(text[:1000], candidate_labels=pair)
        pos_label, neg_label = pair
        pos_index = result["labels"].index(pos_label)
        neg_index = result["labels"].index(neg_label)
        final_score = (result["scores"][pos_index] - result["scores"][neg_index]) * 10
        scores[category] = round(final_score, 3)
    return scores


@app.get("/score-live")
def score_live(industry: str = Query(...)):
    query = f"{industry} ESG news"
    articles = fetch_articles(query, max_results=NUM_RESULTS)
    scored_articles = []
    for article in articles:
        esg_scores = score_esg_article(article["text"], industry)
        scored_articles.append({
            "title": article["title"],
            "url": article["url"],
            "esg_scores": esg_scores,
            "snippet": article["text"][:200]
        })
    return {"industry": industry, "articles": scored_articles}

@app.get("/stock-price")
def get_stock_price(symbol: str = Query(...)):
    try:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": ALPHA_API_KEY
        }
        res = requests.get(url, params=params)
        data = res.json()
        quote = data.get("Global Quote", {})
        return {
            "symbol": symbol,
            "price": float(quote.get("05. price", 0)),
            "change": float(quote.get("10. change percent", "0%" ).strip('%'))
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stock price fetch error: {str(e)}")


@app.get("/stock-history")
def get_stock_history(symbol: str = Query(...)):
    try:
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "compact",
            "apikey": ALPHA_API_KEY
        }
        r = requests.get(url, params=params)
        data = r.json()
        time_series = data.get("Time Series (Daily)", {})
        dates = list(time_series.keys())[:30][::-1]
        prices = [float(time_series[d]["4. close"]) for d in dates]
        return {
            "symbol": symbol,
            "dates": dates,
            "prices": prices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stock history error: {str(e)}")


@app.get("/company-info")
def company_info(name: str = Query(...)):
    try:
        price_data = get_stock_price(name)
        articles = fetch_articles(f"{name} ESG news", max_results=3)
        combined_text = " ".join(article["text"] for article in articles)
        esg_score = score_esg_article(combined_text, name)
        return {"stock_info": price_data, "esg_score": esg_score}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Company info error: {str(e)}")


@app.post("/profitability-sentiment")
def detect_profitability_sentiment(data: ProfitabilityRequest):
    sentiment_result = classifier(data.description, candidate_labels=profitability_labels)
    top_label = sentiment_result["labels"][0]

    # Generate dynamic profit curve where profit > investment (simulate ROI)
    base = random.uniform(20, 30)
    growth = random.uniform(1.2, 1.8)
    peak = random.randint(3, 5)
    profit_curve = []
    for i in range(1, 8):
        invest = i * 10
        if i <= peak:
            profit = invest + base + growth * i
        else:
            profit = invest + base + growth * peak - growth * (i - peak)
        profit_curve.append({"investment": invest, "profit": round(profit, 2)})

    return {
        "description": data.description,
        "sentiment": top_label,
        "profit_data": profit_curve
    }


@app.get("/")
def root():
    return {"message": "Zero-shot ESG AI API is running"}

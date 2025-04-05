import pandas as pd
from transformers import pipeline

# Load the dataset of articles
df = pd.read_csv("articles.csv")

# Load zero-shot classification model once
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Function to generate ESG label pairs for a given industry
def get_esg_label_pairs(industry: str):
    return {
        "Environmental": [f"{industry} promotes sustainability", "causes environmental harm"],
        "Social": [f"{industry} improves social equity", "harms social welfare"],
        "Governance": [f"{industry} supports ethical governance", "promotes corruption"]
    }

# Use a default industry if not available in the CSV
default_industry = "General"

# Ensure ESG score columns exist
for label in ["Environmental", "Social", "Governance"]:
    df[label] = 0.0

# Score each article using the classifier
for idx, row in df.iterrows():
    industry = row.get("industry", default_industry)
    label_pairs = get_esg_label_pairs(industry)
    text = row["text"]
    for category, pair in label_pairs.items():
        result = classifier(text, candidate_labels=pair)
        pos_label, neg_label = pair
        pos_index = result["labels"].index(pos_label)
        neg_index = result["labels"].index(neg_label)
        final_score = (result["scores"][pos_index] - result["scores"][neg_index]) * 10
        df.loc[idx, category] = round(final_score, 3)

# Save the scored articles to a new CSV
df.to_csv("esg_scored_articles.csv", index=False)
print("✅ ESG scores saved to esg_scored_articles.csv")


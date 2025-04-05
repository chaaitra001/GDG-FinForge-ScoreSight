def predict_esg_from_decision(text: str):
    result = classifier(text, labels)
    return dict(zip(result["labels"], result["scores"]))

from pydantic import BaseModel

class DecisionRequest(BaseModel):
    industry: str
    decision: str

@app.post("/simulate")
def simulate_esg_impact(data: DecisionRequest):
    projected_scores = predict_esg_from_decision(data.decision)
    return {
        "industry": data.industry,
        "decision": data.decision,
        "predicted_esg_score": projected_scores
    }

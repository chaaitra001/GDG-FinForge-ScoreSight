import React, { useState } from "react";

function App() {
  const [industry, setIndustry] = useState("");
  const [optionA, setOptionA] = useState("");
  const [optionB, setOptionB] = useState("");
  const [comparison, setComparison] = useState(null);
  const [error, setError] = useState(null);
  const [articleData, setArticleData] = useState([]);
  const [showArticles, setShowArticles] = useState(false);

  const handleCompare = async () => {
    try {
      const response = await fetch("http://localhost:8002/compare-decisions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          industry,
          option_a: optionA,
          option_b: optionB,
        }),
      });

      if (!response.ok) throw new Error("Failed to fetch ESG scores");

      const data = await response.json();
      setComparison(data);
      setError(null);
      setShowArticles(false);
    } catch (err) {
      console.error(err);
      setError("Something went wrong. Please try again.");
    }
  };

  const fetchArticles = async () => {
    try {
      const res = await fetch(`http://localhost:8002/score-live?industry=${encodeURIComponent(industry)}`);
      const data = await res.json();
      setArticleData(data.articles || []);
      setShowArticles(true);
    } catch (err) {
      console.error("Failed to fetch articles", err);
      setError("Failed to fetch articles.");
    }
  };

  const getHighlightStyle = (overallA, overallB, isA) => {
    // If the scores are exactly equal, no option is recommended.
    if (overallA === overallB) {
      return {
        style: {
          backgroundColor: "#ffffff",
          border: "1px solid #ccc"
        },
        isWinner: false
      };
    }
  
    // Determine the winner:
    // - If this is Option A, it wins if overallA > overallB
    // - If this is Option B, it wins if overallB > overallA
    const isWinner = (isA && overallA > overallB) || (!isA && overallB < overallA);
    return {
      style: isWinner
        ? {
            backgroundColor: "#e6ffed",
            border: "2px solid #28a745",
            boxShadow: "0 0 10px rgba(40, 167, 69, 0.3)"
          }
        : {
            backgroundColor: "#ffffff",
            border: "1px solid #ccc"
          },
      isWinner
    };
  };  
  

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Compare Financial Decisions</h1>
      <input
        type="text"
        placeholder="Industry"
        value={industry}
        onChange={(e) => setIndustry(e.target.value)}
        style={{ display: "block", marginBottom: "1rem", width: "300px" }}
      />
      <textarea
        rows="3"
        placeholder="Option A (e.g., invest in renewables)"
        value={optionA}
        onChange={(e) => setOptionA(e.target.value)}
        style={{ display: "block", marginBottom: "1rem", width: "300px" }}
      />
      <textarea
        rows="3"
        placeholder="Option B (e.g., expand oil exploration)"
        value={optionB}
        onChange={(e) => setOptionB(e.target.value)}
        style={{ display: "block", marginBottom: "1rem", width: "300px" }}
      />
      <button onClick={handleCompare}>Compare ESG Impact</button>
      {error && <p style={{ color: "red", marginTop: "1rem" }}>⚠️ {error}</p>}
      {comparison && (
        <div style={{ marginTop: "2rem" }}>
          <h2>ESG Score Comparison for {comparison.industry}</h2>
          <div style={{ display: "flex", gap: "2rem", marginTop: "1rem" }}>
          {[comparison.option_a, comparison.option_b].map((opt, index) => {
  const isA = index === 0;
  const other = isA ? comparison.option_b : comparison.option_a;
  const { style: highlightStyle, isWinner } = getHighlightStyle(opt.overall_score, other.overall_score, isA);

  return (
    <div
      key={index}
      style={{
        padding: "1rem",
        borderRadius: "8px",
        width: "280px",
        ...highlightStyle,
      }}
    >
      <h3>
        {isA ? "Option A" : "Option B"} {isWinner && <span style={{ color: "green" }}>✅ Recommended</span>}
      </h3>
      <p><i>{opt.description}</i></p>
      <h4>ESG Breakdown</h4>
      <ul>
        {Object.entries(opt.predicted_esg_score).map(([label, val]) => (
          <li key={label}>{label}: {val.toFixed(3)}</li>
        ))}
      </ul>
      <strong>Overall ESG Score: {opt.overall_score.toFixed(3)}</strong>
    </div>
  );
})}
          </div>
          <button style={{ marginTop: "2rem" }} onClick={fetchArticles}>
            View ESG Articles for {comparison.industry}
          </button>
          {showArticles && (
            <div style={{ marginTop: "1.5rem" }}>
              <h3>📰 ESG Article Snippets</h3>
              {Array.isArray(articleData) && articleData.length > 0 ? (
                articleData.map((article, idx) => (
                  <div key={idx} style={{ marginBottom: "1rem" }}>
                    <a href={article.url} target="_blank" rel="noopener noreferrer">
                      {article.title}
                    </a>
                    <p>{article.snippet}...</p>
                  </div>
                ))
              ) : (
                <p>No articles found.</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;

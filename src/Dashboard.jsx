import React, { useState } from "react";

function Dashboard() {
  const [company, setCompany] = useState("");
  const [stockInfo, setStockInfo] = useState(null);
  const [esgScore, setEsgScore] = useState(null);
  const [error, setError] = useState(null);

  const fetchCompanyData = async () => {
    try {
      const res = await fetch(`http://localhost:8002/company-info?name=${encodeURIComponent(company)}`);
      const data = await res.json();
      setStockInfo(data.stock_info);
      setEsgScore(data.esg_score);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("❌ Failed to fetch company data.");
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>📊 Company Dashboard</h1>
      <input
        type="text"
        placeholder="Enter Company Name (e.g. Tesla)"
        value={company}
        onChange={(e) => setCompany(e.target.value)}
        style={{ marginRight: "1rem", width: "300px" }}
      />
      <button onClick={fetchCompanyData}>Fetch Info</button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {stockInfo && (
        <div style={{ marginTop: "2rem" }}>
          <h2>📈 Stock Info</h2>
          <p><strong>Price:</strong> {stockInfo.price}</p>
          <p><strong>Symbol:</strong> {stockInfo.symbol}</p>
        </div>
      )}

      {esgScore && (
        <div style={{ marginTop: "2rem" }}>
          <h2>🌱 ESG Score (from news)</h2>
          <ul>
            {Object.entries(esgScore).map(([category, score]) => (
              <li key={category}>{category}: {score.toFixed(3)}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default Dashboard;

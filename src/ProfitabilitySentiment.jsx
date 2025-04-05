import React, { useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

function ProfitabilitySentiment() {
  const [description, setDescription] = useState("");
  const [sentiment, setSentiment] = useState(null);
  const [profitData, setProfitData] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async () => {
    try {
      const res = await fetch("http://localhost:8002/profitability-sentiment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description }),
      });
      const data = await res.json();
      setSentiment(data.sentiment);
      setProfitData(data.profit_data);
      setError(null);
    } catch (err) {
      console.error(err);
      setError("❌ Failed to fetch sentiment analysis.");
    }
  };

  const chartData = {
    labels: profitData.map((pt) => `$${pt.investment}`),
    datasets: [
      {
        label: "Expected Profit",
        data: profitData.map((pt) => pt.profit),
        fill: false,
        borderColor: "#36a2eb",
        backgroundColor: "#36a2eb",
        tension: 0.3,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { display: true },
      title: { display: true, text: "Investment vs Profit Forecast" },
    },
    scales: {
      x: {
        title: { display: true, text: "Investment ($)" },
      },
      y: {
        title: { display: true, text: "Profit ($)" },
        beginAtZero: true,
      },
    },
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>💡 Profitability Predictor</h1>
      <textarea
        rows="4"
        value={description}
        placeholder="Describe the business decision..."
        onChange={(e) => setDescription(e.target.value)}
        style={{ width: "100%", maxWidth: "600px", marginBottom: "1rem" }}
      />
      <br />
      <button onClick={handleSubmit}>Run Profitability Analysis</button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {sentiment && (
        <div style={{ marginTop: "2rem" }}>
          <h2>🔍 Sentiment: <span style={{ color: "#28a745" }}>{sentiment}</span></h2>
          <div style={{ maxWidth: "700px", marginTop: "2rem" }}>
            <Line data={chartData} options={chartOptions} />
          </div>
        </div>
      )}
    </div>
  );
}

export default ProfitabilitySentiment;

import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./Dashboard";
import ESGCompare from "./ESGCompare";
import ProfitabilitySentiment from "./ProfitabilitySentiment"; // new component

function App() {
  return (
    <Router>
      <nav style={{ padding: "1rem", borderBottom: "1px solid #ccc" }}>
        <Link to="/dashboard" style={{ marginRight: "1rem" }}>📊 Dashboard</Link>
        <Link to="/" style={{ marginRight: "1rem" }}>🏠 ESG Compare</Link>
        <Link to="/profitability">💰 Profitability Predictor</Link>
      </nav>

      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/" element={<ESGCompare />} />
        <Route path="/profitability" element={<ProfitabilitySentiment />} />
      </Routes>
    </Router>
  );
}

export default App;


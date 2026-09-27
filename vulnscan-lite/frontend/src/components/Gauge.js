import React from "react";

function scoreToColor(score) {
  if (score >= 80) return "#2ecc71";
  if (score >= 60) return "#f1c40f";
  return "#e74c3c";
}

export default function Gauge({ score, grade }) {
  const radius = 80;
  const circumference = Math.PI * radius;
  const filled = (score / 100) * circumference;
  const color = scoreToColor(score);

  return (
    <div style={{ textAlign: "center" }}>
      <svg width="200" height="120" viewBox="0 0 200 120">
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="#ddd"
          strokeWidth="16"
        />
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke={color}
          strokeWidth="16"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - filled}
        />
        <text x="100" y="90" textAnchor="middle" fontSize="28" fontWeight="bold">
          {score}
        </text>
      </svg>
      <div style={{ fontSize: "20px", fontWeight: "bold" }}>Grade: {grade}</div>
    </div>
  );
}

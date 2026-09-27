import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getScanStatus, getPdfUrl } from "../api";
import Gauge from "../components/Gauge";
import CheckTable from "../components/CheckTable";

export default function Results() {
  const { scanId } = useParams();
  const [status, setStatus] = useState("pending");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      const data = await getScanStatus(scanId);
      if (cancelled) return;

      setStatus(data.status);
      if (data.status === "done") {
        setResult(data.result);
      } else if (data.status === "failed") {
        setError(data.error);
      } else {
        // still pending, check again in 2 seconds
        setTimeout(poll, 2000);
      }
    }

    poll();
    return () => { cancelled = true; };
  }, [scanId]);

  if (status === "pending") {
    return <div style={{ textAlign: "center", marginTop: "60px" }}>Scanning, this takes 10-30 seconds...</div>;
  }

  if (status === "failed") {
    return <div style={{ textAlign: "center", marginTop: "60px" }}>Scan failed: {error}</div>;
  }

  return (
    <div style={{ maxWidth: "700px", margin: "40px auto" }}>
      <h2>Results for {result.url}</h2>
      <Gauge score={result.score} grade={result.grade} />
      <CheckTable passed={result.passed_checks} failed={result.failed_checks} />
      <div style={{ marginTop: "20px" }}>
        <a href={getPdfUrl(scanId)}>Download PDF report</a>
      </div>
      <p style={{ fontSize: "12px", color: "#666", marginTop: "30px" }}>{result.disclaimer}</p>
    </div>
  );
}

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { startScan } from "../api";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    const res = await startScan(url);
    setLoading(false);

    if (res.scan_id) {
      navigate("/results/" + res.scan_id);
    } else {
      alert(res.error || "something went wrong");
    }
  }

  return (
    <div style={{ maxWidth: "500px", margin: "40px auto", textAlign: "center" }}>
      <div style={{ background: "#fff3cd", padding: "10px", marginBottom: "20px", border: "1px solid #ffeeba" }}>
        Only scan websites you own. This tool performs passive analysis only.
      </div>

      <h1>VulnScan Lite</h1>
      <p>Enter a website to get a quick security health report.</p>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="e.g. myblog.com"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          style={{ padding: "8px", width: "70%" }}
        />
        <button type="submit" disabled={loading} style={{ padding: "8px 16px", marginLeft: "8px" }}>
          {loading ? "Starting..." : "Scan"}
        </button>
      </form>
    </div>
  );
}

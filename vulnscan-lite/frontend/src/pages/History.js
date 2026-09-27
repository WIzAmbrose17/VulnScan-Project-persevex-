import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getHistory } from "../api";

export default function History() {
  const [scans, setScans] = useState([]);
  const [loggedOut, setLoggedOut] = useState(false);

  useEffect(() => {
    getHistory().then((data) => {
      if (data.error) {
        setLoggedOut(true);
      } else {
        setScans(data);
      }
    });
  }, []);

  if (loggedOut) {
    return <div style={{ textAlign: "center", marginTop: "60px" }}>You need to login to see your scan history.</div>;
  }

  return (
    <div style={{ maxWidth: "700px", margin: "40px auto" }}>
      <h2>Scan History</h2>
      {scans.length === 0 && <p>no scans yet</p>}
      <table border="1" cellPadding="8" style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th>URL</th>
            <th>Score</th>
            <th>Grade</th>
            <th>Date</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {scans.map((s) => (
            <tr key={s.id}>
              <td>{s.url}</td>
              <td>{s.score}</td>
              <td>{s.grade}</td>
              <td>{s.created_at}</td>
              <td><Link to={"/results/" + s.id}>view</Link></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

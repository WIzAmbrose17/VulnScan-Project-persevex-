import React from "react";

export default function CheckTable({ passed, failed }) {
  return (
    <div>
      <h3>Passed Checks</h3>
      {passed.length === 0 && <p>none, ouch</p>}
      <ul>
        {passed.map((p, i) => (
          <li key={i} style={{ color: "green" }}>{p}</li>
        ))}
      </ul>

      <h3>Failed Checks</h3>
      {failed.length === 0 && <p>none, nice</p>}
      <table border="1" cellPadding="8" style={{ borderCollapse: "collapse", width: "100%" }}>
        <thead>
          <tr>
            <th>Check</th>
            <th>Why it matters</th>
            <th>Nginx fix</th>
            <th>Apache fix</th>
          </tr>
        </thead>
        <tbody>
          {failed.map((f, i) => (
            <tr key={i}>
              <td>{f.check}</td>
              <td>{f.why}</td>
              <td><code>{f.nginx}</code></td>
              <td><code>{f.apache}</code></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

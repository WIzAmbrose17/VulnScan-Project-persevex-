import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    const res = await login(email, password);
    if (res.message) {
      navigate("/history");
    } else {
      alert(res.error);
    }
  }

  return (
    <div style={{ maxWidth: "300px", margin: "60px auto" }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <input type="email" placeholder="email" value={email}
          onChange={(e) => setEmail(e.target.value)} style={{ width: "100%", padding: "8px", marginBottom: "10px" }} />
        <input type="password" placeholder="password" value={password}
          onChange={(e) => setPassword(e.target.value)} style={{ width: "100%", padding: "8px", marginBottom: "10px" }} />
        <button type="submit" style={{ width: "100%", padding: "8px" }}>Login</button>
      </form>
    </div>
  );
}

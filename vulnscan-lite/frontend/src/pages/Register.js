import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { register } from "../api";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    const res = await register(email, password);
    if (res.message) {
      navigate("/history");
    } else {
      alert(res.error);
    }
  }

  return (
    <div style={{ maxWidth: "300px", margin: "60px auto" }}>
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <input type="email" placeholder="email" value={email}
          onChange={(e) => setEmail(e.target.value)} style={{ width: "100%", padding: "8px", marginBottom: "10px" }} />
        <input type="password" placeholder="password" value={password}
          onChange={(e) => setPassword(e.target.value)} style={{ width: "100%", padding: "8px", marginBottom: "10px" }} />
        <button type="submit" style={{ width: "100%", padding: "8px" }}>Register</button>
      </form>
    </div>
  );
}

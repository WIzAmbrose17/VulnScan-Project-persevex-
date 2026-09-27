const BASE_URL = "http://localhost:5000";

export async function startScan(url) {
  const res = await fetch(BASE_URL + "/api/scan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ url: url }),
  });
  return res.json();
}

export async function getScanStatus(scanId) {
  const res = await fetch(BASE_URL + "/api/scan/" + scanId + "/status", {
    credentials: "include",
  });
  return res.json();
}

export async function login(email, password) {
  const res = await fetch(BASE_URL + "/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

export async function register(email, password) {
  const res = await fetch(BASE_URL + "/api/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ email, password }),
  });
  return res.json();
}

export async function getHistory() {
  const res = await fetch(BASE_URL + "/api/history", {
    credentials: "include",
  });
  return res.json();
}

export function getPdfUrl(scanId) {
  return BASE_URL + "/api/scan/" + scanId + "/pdf";
}

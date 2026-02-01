const API_BASE = "http://localhost:8000";

async function apiRequest(endpoint, method="GET", body=null) {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      "Authorization": token ? `Bearer ${token}` : ""
    },
    body: body ? JSON.stringify(body) : null
  });
  return await res.json();
}

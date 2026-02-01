async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const res = await apiRequest("/auth/login", "POST", { email, password });
  if (res.access_token) {
    localStorage.setItem("token", res.access_token);
    window.location.href = "dashboard.html";
  } else {
    alert("Login failed");
  }
}

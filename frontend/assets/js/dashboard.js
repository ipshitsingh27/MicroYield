document.addEventListener("DOMContentLoaded", async () => {
  const data = await apiRequest("/vault/summary");
  const container = document.getElementById("dashboardContent");
  container.innerHTML = `
    <div class="card">Vault Balance: ${data.total}</div>
    <div class="card">USDC Principal: ${data.principal}</div>
    <div class="card">Yield Earned: ${data.yield}</div>
  `;
});

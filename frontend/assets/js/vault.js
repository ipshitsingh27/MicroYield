document.addEventListener("DOMContentLoaded", async () => {
  const data = await apiRequest("/vault/summary");
  const container = document.getElementById("vaultContent");
  container.innerHTML = `
    <div class="card">XLM Saved: ${data.xlm}</div>
    <div class="card">USDC Principal: ${data.principal}</div>
    <div class="card">Yield: ${data.yield}</div>
  `;
});

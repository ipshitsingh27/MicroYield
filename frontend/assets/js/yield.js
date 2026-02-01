document.addEventListener("DOMContentLoaded", async () => {
  const data = await apiRequest("/vault/apy");
  const container = document.getElementById("yieldContent");
  container.innerHTML = `
    <div class="card">Current APY: ${data.apy}%</div>
    <div class="card">Total Yield Distributed: ${data.total_distributed}</div>
  `;
});

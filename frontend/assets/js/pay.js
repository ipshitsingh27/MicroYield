async function makePayment() {
  const invest = document.getElementById("investToggle").checked;
  if (invest) {
    await apiRequest("/wallet/pay", "POST", { invest: true });
    alert("Payment done + invested");
  } else {
    await apiRequest("/wallet/pay", "POST", { invest: false });
    alert("Payment done");
  }
}

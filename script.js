let yieldBalance = 500;
const app = document.getElementById("app");

// Update balance display
const yieldAmount = document.querySelector(".yield-fixed .amount");
if (yieldAmount) {
  yieldAmount.innerText = `₹${yieldBalance}`;
}

const data = {
  travel: [
    {
      name: "Travala",
      img: "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=600&h=400&fit=crop",
      desc: "Book flights & hotels directly using cryptocurrency.",
      link: "https://www.travala.com",
    },
    {
      name: "Alternative Airlines",
      img: "https://images.unsplash.com/photo-1526772662000-3f88f10405ff?w=600&h=400&fit=crop",
      desc: "Book airline tickets using BTC, ETH & stablecoins.",
      link: "https://www.alternativeairlines.com",
    },
  ],

  giftcards: [
    {
      name: "Bitrefill",
      img: "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&h=400&fit=crop",
      desc: "Use crypto-backed gift cards for restaurants, food brands, and more.",
      link: "https://www.bitrefill.com",
    },
    {
      name: "CoinGate Gift Cards",
      img: "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=600&h=400&fit=crop",
      desc: "Purchase global brand gift cards with crypto.",
      link: "https://coingate.com/gift-cards",
    },
  ],

  services: [
    {
      name: "Namecheap",
      img: "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&h=400&fit=crop",
      desc: "Buy domains & hosting using crypto payments.",
      link: "https://www.namecheap.com",
    },
  ],

  cards: [
    {
      name: "Crypto.com Card",
      img: "https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=600&h=400&fit=crop",
      desc: "Spend crypto anywhere Visa is accepted.",
      link: "https://crypto.com/cards",
    },
  ],
};

function showCategories() {
  app.innerHTML = `
    <div class="category-container">
      <div class="category-card" onclick="showPlaces('travel')">✈️ Travel</div>
      <div class="category-card" onclick="showPlaces('giftcards')">🎁 Gift Cards</div>
      <div class="category-card" onclick="showPlaces('services')">🎮 Digital Services</div>
      <div class="category-card" onclick="showPlaces('cards')">💳 Crypto Cards</div>
    </div>
  `;
  
  // Add ripple effect to category cards
  addRippleEffect();
}

function showPlaces(category) {
  let html = `
    <div class="nav-buttons">
      <button onclick="showCategories()">⬅ Back</button>
    </div>
    <div class="place-container">
  `;

  data[category].forEach((item) => {
    html += `
      <div class="place-card">
        <img src="${item.img}" alt="${item.name}">
        <h3>${item.name}</h3>
        <p>${item.desc}</p>
        <button onclick="window.open('${item.link}', '_blank')">
          Visit Website →
        </button>
      </div>
    `;
  });

  html += `</div>`;
  app.innerHTML = html;
}

// Ripple effect for interactive elements
function addRippleEffect() {
  const cards = document.querySelectorAll('.category-card');
  
  cards.forEach(card => {
    card.addEventListener('click', function(e) {
      const ripple = document.createElement('span');
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;
      
      ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        border-radius: 50%;
        background: rgba(0, 229, 255, 0.4);
        top: ${y}px;
        left: ${x}px;
        pointer-events: none;
        animation: ripple-animation 0.6s ease-out;
      `;
      
      this.appendChild(ripple);
      
      setTimeout(() => ripple.remove(), 600);
    });
  });
}

// Mouse parallax effect for floating coins
document.addEventListener('mousemove', (e) => {
  const coins = document.querySelectorAll('.crypto-coin');
  const mouseX = e.clientX / window.innerWidth;
  const mouseY = e.clientY / window.innerHeight;
  
  coins.forEach((coin, index) => {
    const speed = (index + 1) * 0.5;
    const x = (mouseX - 0.5) * speed * 20;
    const y = (mouseY - 0.5) * speed * 20;
    
    coin.style.transform = `translate(${x}px, ${y}px)`;
  });
});

// Smooth scroll behavior
document.addEventListener('click', (e) => {
  if (e.target.tagName === 'BUTTON' && e.target.onclick) {
    app.style.opacity = '0';
    app.style.transform = 'translateY(20px)';
    
    setTimeout(() => {
      app.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      app.style.opacity = '1';
      app.style.transform = 'translateY(0)';
    }, 100);
  }
});

// Initialize
showCategories();

// Balance card pulse effect on hover
const balanceCard = document.querySelector('.yield-fixed');
if (balanceCard) {
  balanceCard.addEventListener('mouseenter', () => {
    yieldAmount.style.transform = 'scale(1.1)';
    yieldAmount.style.transition = 'transform 0.3s ease';
  });
  
  balanceCard.addEventListener('mouseleave', () => {
    yieldAmount.style.transform = 'scale(1)';
  });
}

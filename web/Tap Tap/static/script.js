const pointsEl = document.getElementById('points');
const buyBtn = document.getElementById('buyBtn');
const coin = document.getElementById('coin');
const flagBox = document.getElementById('flagBox');

async function getStatus() {
  try {
    const res = await fetch('/api/status');
    if (!res.ok) return;
    const data = await res.json();
    pointsEl.textContent = data.points;
    if (!data.has_flag) {
      buyBtn.disabled = data.points < data.cost;
    } else {
      showFlag('RCSC{Tap_Tap_is_fun}');
    }
  } catch (e) {}
}

function showFlag(flag) {
  if (!flagBox) return;
  flagBox.style.display = 'block';
  flagBox.querySelector('.flag').textContent = flag;
}

async function clickCoin() {
  try {
    const res = await fetch('/api/click', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ gain: 1 })
    });
    const data = await res.json();
    if (data.ok) {
      pointsEl.textContent = data.points;
      // Try enabling buy button if threshold reached
      const cost = Number(document.getElementById('cost')?.textContent || '586');
      if (data.points >= cost) {
        buyBtn.disabled = false;
      }
    }
  } catch (e) {}
}

async function buyFlag() {
  try {
    const res = await fetch('/api/buy', { method: 'POST' });
    const data = await res.json();
    if (data.ok && data.flag) {
      showFlag(data.flag);
      buyBtn.disabled = true;
    }
  } catch (e) {}
}

if (coin) coin.addEventListener('click', clickCoin);
if (buyBtn) buyBtn.addEventListener('click', buyFlag);

// Initial status refresh
getStatus();

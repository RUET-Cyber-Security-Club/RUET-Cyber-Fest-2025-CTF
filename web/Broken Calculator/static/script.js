
'use strict';

const display = document.getElementById('display');
const keys = document.querySelector('.keys');
const equals = document.getElementById('equals');
const clearOne = document.getElementById('clear-one');
const clearAll = document.getElementById('clear-all');

let justEvaluated = false;

function setDisplay(text, type) {
  display.value = text || '';
  display.className = 'display' + (type ? ' ' + type : '');
}

// Append key from button clicks
keys.addEventListener('click', (e) => {
  const btn = e.target;
  if (!(btn instanceof HTMLButtonElement)) return;
  const val = btn.getAttribute('data-key');
  if (!val) return;
  if (justEvaluated) {
    // Clear first after an evaluation when new input starts
    setDisplay('', '');
    justEvaluated = false;
  }
  insertAtCursor(val);
});

// AC clears everything
clearAll.addEventListener('click', () => {
  setDisplay('', '');
  justEvaluated = false;
});

// C clears one character
clearOne.addEventListener('click', () => {
  const s = display.selectionStart ?? display.value.length;
  const e = display.selectionEnd ?? display.value.length;
  if (s !== e) {
    display.setRangeText('', s, e, 'end');
  } else if (s > 0) {
    display.setRangeText('', s - 1, s, 'end');
  }
  justEvaluated = false;
});

// Evaluate on equals via backend
equals.addEventListener('click', async () => {
  const expr = display.value.trim();
  try {
    const resp = await fetch('/eval', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ expr })
    });
    const data = await resp.json();
    if (data.status === 'error') {
      setDisplay('ERROR', 'error');
    } else if (data.status === 'flag') {
      setDisplay(data.message, 'flag');
    } else {
      setDisplay(String(data.message), '');
    }
    // Mark that we just evaluated; next input clears first
    justEvaluated = true;
  } catch (err) {
    setDisplay('ERROR', 'error');
  }
});

// Helper: insert at caret
function insertAtCursor(text) {
  const s = display.selectionStart ?? display.value.length;
  const e = display.selectionEnd ?? display.value.length;
  display.setRangeText(text, s, e, 'end');
  display.focus();
}

// If user types directly after evaluation, clear first
display.addEventListener('beforeinput', (e) => {
  if (justEvaluated) {
    setDisplay('', '');
    justEvaluated = false;
  }
});
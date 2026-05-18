/**
 * script.js
 * UI controller for the subnet calculator.
 * Depends on subnet.js being loaded first.
 */
 
const HISTORY_KEY = 'subnetHistory';
const HISTORY_LIMIT = 20;
 
// ── DOM references ────────────────────────────────────────────────────────────
 
const form        = document.getElementById('subnetForm');
const input       = document.getElementById('cidr');
const resultBox   = document.getElementById('result');
const resultList  = document.getElementById('resultList');
const historyBox  = document.getElementById('history');
const historyList = document.getElementById('historyList');
const clearBtn    = document.getElementById('clearHistory');
const errorMsg    = document.getElementById('errorMsg');
 
// ── History helpers ───────────────────────────────────────────────────────────
 
function loadHistory() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY)) || [];
  } catch {
    return [];
  }
}
 
function saveToHistory(cidr, result) {
  const history = loadHistory();
  // Avoid duplicates at the top
  if (history.length > 0 && history[0].cidr === cidr) return;
  history.unshift({ cidr, network: result.network, prefixLen: result.prefixLen });
  if (history.length > HISTORY_LIMIT) history.pop();
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
}
 
function renderHistory() {
  const history = loadHistory();
 
  if (history.length === 0) {
    historyBox.classList.add('hidden');
    return;
  }
 
  historyBox.classList.remove('hidden');
  historyList.innerHTML = '';
 
  history.forEach(entry => {
    const li = document.createElement('li');
 
    const label = document.createElement('span');
    label.className = 'history-input';
    label.textContent = entry.cidr;
 
    const arrow = document.createElement('span');
    arrow.className = 'history-arrow';
    arrow.textContent = '→';
 
    const value = document.createElement('span');
    value.className = 'history-network';
    value.textContent = `${entry.network}/${entry.prefixLen}`;
 
    // Click a history entry to re-run it
    li.addEventListener('click', () => {
      input.value = entry.cidr;
      form.requestSubmit();
    });
 
    li.append(label, arrow, value);
    historyList.appendChild(li);
  });
}
 
// ── Result rendering ──────────────────────────────────────────────────────────
 
function renderResult(result) {
  resultList.innerHTML = '';
 
  const rows = [
    ['Network Address', `${result.network}/${result.prefixLen}`],
    ['Subnet Mask',     result.netmask],
    ['Wildcard Mask',   result.wildcardMask],
    ['Broadcast',       result.broadcast],
    ['Host Range',      result.hostMin ? `${result.hostMin} – ${result.hostMax}` : 'N/A'],
    ['Usable Hosts',    result.numHosts.toLocaleString()],
    ['Total Addresses', result.totalAddresses.toLocaleString()],
    ['IP Class',        result.ipClass],
    ['Scope',           result.isPrivate ? 'Private (RFC 1918)' : 'Public'],
  ];
 
  rows.forEach(([label, value]) => {
    const li = document.createElement('li');
 
    const labelEl = document.createElement('span');
    labelEl.className = 'result-label';
    labelEl.textContent = label;
 
    const valueEl = document.createElement('span');
    valueEl.className = 'result-value';
    valueEl.textContent = value;
 
    li.append(labelEl, valueEl);
    resultList.appendChild(li);
  });
 
  resultBox.classList.remove('hidden');
}
 
// ── Event handlers ────────────────────────────────────────────────────────────
 
form.addEventListener('submit', function (e) {
  e.preventDefault();
 
  const cidr = input.value.trim();
  errorMsg.textContent = '';
  errorMsg.classList.add('hidden');
  resultBox.classList.add('hidden');
 
  try {
    const result = calculateSubnet(cidr);
    renderResult(result);
    saveToHistory(cidr, result);
    renderHistory();
  } catch (err) {
    errorMsg.textContent = err.message;
    errorMsg.classList.remove('hidden');
  }
});
 
clearBtn.addEventListener('click', () => {
  localStorage.removeItem(HISTORY_KEY);
  renderHistory();
});
 
// ── Init ──────────────────────────────────────────────────────────────────────
 
renderHistory();

document.getElementById('subnetForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const cidr = document.getElementById('ip').value;
  // Example: split into IP and mask, compute network and broadcast
  const [ip, prefix] = cidr.split('/');
  // Convert IP to binary, apply mask, etc.
  // (Alternatively, use a library or custom functions)
  document.getElementById('results').innerHTML = `
    <p>Network: ${networkAddr}</p>
    <p>Broadcast: ${broadcastAddr}</p>
    <p>Host Range: ${hostMin} - ${hostMax}</p>
  `;
  // Save to localStorage for history:contentReference[oaicite:9]{index=9}
  let history = JSON.parse(localStorage.getItem('history')||'[]');
  history.push(cidr);
  localStorage.setItem('history', JSON.stringify(history));
});
function ipToInt(ip) {
  return ip.split('.').reduce((acc, octet) => (acc << 8) + parseInt(octet, 10), 0);
}

function intToIp(int) {
  return [24, 16, 8, 0].map(shift => (int >>> shift) & 255).join('.');
}

function calculateSubnet(cidr) {
  const [ipStr, prefixStr] = cidr.split('/');
  const prefixLen = parseInt(prefixStr, 10);

  if (!ipStr || isNaN(prefixLen) || prefixLen < 0 || prefixLen > 32) {
    throw new Error('Invalid CIDR format');
  }

  const ipInt = ipToInt(ipStr);
  const maskInt = prefixLen === 0 ? 0 : 0xFFFFFFFF << (32 - prefixLen);
  const networkInt = ipInt & maskInt;
  const broadcastInt = networkInt | (~maskInt >>> 0);
  const total = broadcastInt - networkInt + 1;

  let hostMin = "N/A", hostMax = "N/A", numHosts = 0;
  if (total > 2) {
    hostMin = intToIp(networkInt + 1);
    hostMax = intToIp(broadcastInt - 1);
    numHosts = total - 2;
  }

  return {
    network: intToIp(networkInt),
    broadcast: intToIp(broadcastInt),
    netmask: intToIp(maskInt),
    prefixLen,
    hostMin,
    hostMax,
    numHosts
  };
}

document.getElementById('subnetForm').addEventListener('submit', function (e) {
  e.preventDefault();
  const input = document.getElementById('cidr').value.trim();
  const resultBox = document.getElementById('result');
  const resultList = document.getElementById('resultList');
  resultList.innerHTML = '';

  try {
    const result = calculateSubnet(input);

    const entries = [
      ['Network', `${result.network}/${result.prefixLen}`],
      ['Netmask', result.netmask],
      ['Broadcast', result.broadcast],
      ['Host Range', `${result.hostMin} – ${result.hostMax}`],
      ['Usable Hosts', result.numHosts],
    ];

    entries.forEach(([label, value]) => {
      const li = document.createElement('li');
      li.textContent = `${label}: ${value}`;
      resultList.appendChild(li);
    });

    resultBox.classList.remove('hidden');
  } catch (err) {
    alert("Invalid CIDR input. Please try again.");
    resultBox.classList.add('hidden');
  }
});

// Key under which we'll store the history array
const STORAGE_KEY = 'subnetHistory';

function loadHistory() {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored ? JSON.parse(stored) : [];
}

function saveHistoryEntry(entry) {
  const history = loadHistory();
  history.unshift(entry);          // newest first
  if (history.length > 20) history.pop();  // cap size
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
}

function renderHistory() {
  const history = loadHistory();
  const historyDiv = document.getElementById('history');
  const list = document.getElementById('historyList');
  list.innerHTML = '';

  if (history.length === 0) {
    historyDiv.classList.add('hidden');
    return;
  }
  historyDiv.classList.remove('hidden');

  history.forEach(item => {
    const li = document.createElement('li');
    li.textContent = `${item.input} → ${item.network}/${item.prefixLen}`;
    list.appendChild(li);
  });
}

// On page load
renderHistory();

// In your submit handler, after computing and displaying `result`:
const entry = {
  input:   input,                   // the CIDR string
  network: result.network,
  prefixLen: result.prefixLen
};
saveHistoryEntry(entry);
renderHistory();

// Clear history button
document.getElementById('clearHistory').addEventListener('click', () => {
  localStorage.removeItem(STORAGE_KEY);
  renderHistory();
});

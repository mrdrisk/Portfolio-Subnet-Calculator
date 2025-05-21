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

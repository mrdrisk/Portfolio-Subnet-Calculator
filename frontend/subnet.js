/**
 * Convert a dotted-quad IPv4 string into a 32-bit integer.
 */
function ipToInt(ip) {
  return ip.split('.')
    .map(octet => parseInt(octet, 10))
    .reduce((acc, octet) => (acc << 8) + octet);
}

/**
 * Convert a 32-bit integer back to dotted-quad IPv4.
 */
function intToIp(int) {
  return [24, 16, 8, 0]
    .map(shift => (int >>> shift) & 0xFF)
    .join('.');
}

/**
 * Given an IPv4/CIDR string, compute subnet info.
 * Returns an object: network, broadcast, netmask, prefixLen, hostMin, hostMax, numHosts.
 */
function calculateSubnet(cidr) {
  const [ipStr, prefixStr] = cidr.split('/');
  const prefixLen = parseInt(prefixStr, 10);

  // Convert IP to a 32-bit number
  const ipInt = ipToInt(ipStr);

  // Build mask as 32-bit integer: leading prefixLen ones
  const maskInt = prefixLen === 0
    ? 0
    : 0xFFFFFFFF << (32 - prefixLen);

  // Compute network and broadcast
  const networkInt   = ipInt & maskInt;
  const broadcastInt = networkInt | (~maskInt >>> 0);

  // Usable host range (if possible)
  const total = broadcastInt - networkInt + 1;
  let hostMin = null, hostMax = null, numHosts = 0;
  if (total > 2) {
    hostMin  = intToIp(networkInt + 1);
    hostMax  = intToIp(broadcastInt - 1);
    numHosts = total - 2;
  }

  return {
    network:     intToIp(networkInt),
    broadcast:   intToIp(broadcastInt),
    netmask:     intToIp(maskInt),
    prefixLen:   prefixLen,
    hostMin,
    hostMax,
    numHosts
  };
}

// Example usage:
const result = calculateSubnet("192.168.1.10/24");
console.log(result);
// {
//   network: "192.168.1.0",
//   broadcast: "192.168.1.255",
//   netmask: "255.255.255.0",
//   prefixLen: 24,
//   hostMin: "192.168.1.1",
//   hostMax: "192.168.1.254",
//   numHosts: 254
// }

/**
 * subnet.js
 * Core IPv4 subnet calculation logic.
 * Pure functions only — no DOM interaction, no side effects.
 */
 
/**
 * Converts a dotted-quad IPv4 string to a 32-bit unsigned integer.
 * @param {string} ip - e.g. "192.168.1.10"
 * @returns {number}
 */
function ipToInt(ip) {
  return ip.split('.')
    .map(octet => parseInt(octet, 10))
    .reduce((acc, octet) => (acc * 256) + octet, 0);
}
 
/**
 * Converts a 32-bit integer to a dotted-quad IPv4 string.
 * Uses unsigned right shift to handle sign bit correctly.
 * @param {number} int
 * @returns {string}
 */
function intToIp(int) {
  return [24, 16, 8, 0]
    .map(shift => (int >>> shift) & 0xFF)
    .join('.');
}
 
/**
 * Validates an IPv4 address string.
 * @param {string} ip
 * @returns {boolean}
 */
function isValidIp(ip) {
  const octets = ip.split('.');
  if (octets.length !== 4) return false;
  return octets.every(o => {
    const n = parseInt(o, 10);
    return String(n) === o && n >= 0 && n <= 255;
  });
}
 
/**
 * Validates a CIDR prefix length.
 * @param {number} prefix
 * @returns {boolean}
 */
function isValidPrefix(prefix) {
  return Number.isInteger(prefix) && prefix >= 0 && prefix <= 32;
}
 
/**
 * Calculates full subnet information from a CIDR string.
 * @param {string} cidr - e.g. "192.168.1.10/24"
 * @returns {{
 *   network: string,
 *   broadcast: string,
 *   netmask: string,
 *   wildcardMask: string,
 *   prefixLen: number,
 *   hostMin: string|null,
 *   hostMax: string|null,
 *   numHosts: number,
 *   totalAddresses: number,
 *   ipClass: string,
 *   isPrivate: boolean
 * }}
 * @throws {Error} on invalid input
 */
function calculateSubnet(cidr) {
  const parts = cidr.trim().split('/');
  if (parts.length !== 2) throw new Error('Input must be in CIDR format: x.x.x.x/n');
 
  const [ipStr, prefixStr] = parts;
  const prefixLen = parseInt(prefixStr, 10);
 
  if (!isValidIp(ipStr))       throw new Error(`Invalid IP address: "${ipStr}"`);
  if (!isValidPrefix(prefixLen)) throw new Error(`Prefix must be 0–32, got: "${prefixStr}"`);
 
  const ipInt = ipToInt(ipStr);
 
  // Build subnet mask: prefixLen leading 1s, rest 0s
  // Special-case /0 to avoid undefined shift behaviour
  const maskInt = prefixLen === 0
    ? 0
    : (0xFFFFFFFF << (32 - prefixLen)) >>> 0;
 
  const networkInt   = (ipInt & maskInt) >>> 0;
  const broadcastInt = (networkInt | (~maskInt >>> 0)) >>> 0;
  const totalAddresses = broadcastInt - networkInt + 1;
 
  // Usable hosts: /31 and /32 are special cases (point-to-point / host routes)
  let hostMin = null, hostMax = null, numHosts = 0;
  if (prefixLen <= 30) {
    hostMin  = intToIp(networkInt + 1);
    hostMax  = intToIp(broadcastInt - 1);
    numHosts = totalAddresses - 2;
  } else if (prefixLen === 31) {
    // RFC 3021: /31 point-to-point, both addresses usable
    hostMin  = intToIp(networkInt);
    hostMax  = intToIp(broadcastInt);
    numHosts = 2;
  } else {
    // /32 single host route
    hostMin  = intToIp(networkInt);
    hostMax  = intToIp(networkInt);
    numHosts = 1;
  }
 
  return {
    network:        intToIp(networkInt),
    broadcast:      intToIp(broadcastInt),
    netmask:        intToIp(maskInt),
    wildcardMask:   intToIp(~maskInt >>> 0),
    prefixLen,
    hostMin,
    hostMax,
    numHosts,
    totalAddresses,
    ipClass:        getIpClass(ipStr),
    isPrivate:      isPrivateIp(ipInt),
  };
}
 
/**
 * Returns the classful class of an IPv4 address (A/B/C/D/E).
 * @param {string} ip
 * @returns {string}
 */
function getIpClass(ip) {
  const first = parseInt(ip.split('.')[0], 10);
  if (first < 128)  return 'A';
  if (first < 192)  return 'B';
  if (first < 224)  return 'C';
  if (first < 240)  return 'D (Multicast)';
  return 'E (Reserved)';
}
 
/**
 * Returns true if the IP falls within RFC 1918 private ranges.
 * @param {number} ipInt
 * @returns {boolean}
 */
function isPrivateIp(ipInt) {
  const ranges = [
    [ipToInt('10.0.0.0'),    ipToInt('10.255.255.255')],
    [ipToInt('172.16.0.0'),  ipToInt('172.31.255.255')],
    [ipToInt('192.168.0.0'), ipToInt('192.168.255.255')],
  ];
  return ranges.some(([start, end]) => ipInt >= start && ipInt <= end);
}

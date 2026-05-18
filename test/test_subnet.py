#!/usr/bin/env python3
"""
test_subnet.py
Unit tests for subnet_utils.py.
 
Run from the repo root:
    python3 -m pytest test/test_subnet.py -v
Or directly:
    python3 test/test_subnet.py
"""
 
import sys
import os
import unittest
 
# Allow imports from cli/ regardless of where the test is run from
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "cli"))
 
from subnet_utils import calculate_subnet, get_ip_class, get_scope
 
 
class TestIpClass(unittest.TestCase):
    """Tests for get_ip_class()."""
 
    def test_class_a(self):
        self.assertEqual(get_ip_class("10.0.0.1"), "A")
 
    def test_class_b(self):
        self.assertEqual(get_ip_class("172.16.0.1"), "B")
 
    def test_class_c(self):
        self.assertEqual(get_ip_class("192.168.1.1"), "C")
 
    def test_class_d_multicast(self):
        self.assertIn("D", get_ip_class("224.0.0.1"))
 
    def test_class_e_reserved(self):
        self.assertIn("E", get_ip_class("240.0.0.1"))
 
    def test_class_a_boundary(self):
        self.assertEqual(get_ip_class("127.0.0.1"), "A")
 
    def test_class_b_boundary(self):
        self.assertEqual(get_ip_class("191.255.0.1"), "B")
 
 
class TestCalculateSubnet(unittest.TestCase):
    """Tests for calculate_subnet()."""
 
    # ── Standard /24 ──────────────────────────────────────────────────────────
 
    def test_network_address_24(self):
        result = calculate_subnet("192.168.1.10/24")
        self.assertEqual(result["network"], "192.168.1.0")
 
    def test_broadcast_24(self):
        result = calculate_subnet("192.168.1.10/24")
        self.assertEqual(result["broadcast"], "192.168.1.255")
 
    def test_netmask_24(self):
        result = calculate_subnet("192.168.1.10/24")
        self.assertEqual(result["netmask"], "255.255.255.0")
 
    def test_wildcard_mask_24(self):
        result = calculate_subnet("192.168.1.10/24")
        self.assertEqual(result["wildcard_mask"], "0.0.0.255")
 
    def test_host_min_24(self):
        result = calculate_subnet("192.168.1.10/24")
        self.assertEqual(result["host_min"], "192.168.1.1")
 
    def test_host_max_24(self):
        result = calculate_subnet("192.168.1.10/24")
        self.assertEqual(result["host_max"], "192.168.1.254")
 
    def test_num_hosts_24(self):
        result = calculate_subnet("192.168.1.10/24")
        self.assertEqual(result["num_hosts"], "254")
 
    def test_total_addresses_24(self):
        result = calculate_subnet("192.168.1.10/24")
        self.assertEqual(result["total_addresses"], "256")
 
    def test_prefix_len_24(self):
        result = calculate_subnet("192.168.1.10/24")
        self.assertEqual(result["prefix_len"], "24")
 
    # ── Class A /8 ────────────────────────────────────────────────────────────
 
    def test_network_8(self):
        result = calculate_subnet("10.0.0.0/8")
        self.assertEqual(result["network"], "10.0.0.0")
 
    def test_broadcast_8(self):
        result = calculate_subnet("10.0.0.0/8")
        self.assertEqual(result["broadcast"], "10.255.255.255")
 
    def test_num_hosts_8(self):
        result = calculate_subnet("10.0.0.0/8")
        self.assertEqual(result["num_hosts"], "16777214")
 
    def test_netmask_8(self):
        result = calculate_subnet("10.0.0.0/8")
        self.assertEqual(result["netmask"], "255.0.0.0")
 
    def test_wildcard_8(self):
        result = calculate_subnet("10.0.0.0/8")
        self.assertEqual(result["wildcard_mask"], "0.255.255.255")
 
    # ── /16 ───────────────────────────────────────────────────────────────────
 
    def test_network_16(self):
        result = calculate_subnet("172.16.5.99/16")
        self.assertEqual(result["network"], "172.16.0.0")
 
    def test_broadcast_16(self):
        result = calculate_subnet("172.16.5.99/16")
        self.assertEqual(result["broadcast"], "172.16.255.255")
 
    def test_num_hosts_16(self):
        result = calculate_subnet("172.16.5.99/16")
        self.assertEqual(result["num_hosts"], "65534")
 
    # ── Edge: /30 (smallest normal subnet) ───────────────────────────────────
 
    def test_num_hosts_30(self):
        result = calculate_subnet("192.168.1.0/30")
        self.assertEqual(result["num_hosts"], "2")
 
    def test_host_range_30(self):
        result = calculate_subnet("192.168.1.0/30")
        self.assertEqual(result["host_min"], "192.168.1.1")
        self.assertEqual(result["host_max"], "192.168.1.2")
 
    def test_broadcast_30(self):
        result = calculate_subnet("192.168.1.0/30")
        self.assertEqual(result["broadcast"], "192.168.1.3")
 
    # ── Edge: /31 (RFC 3021 point-to-point) ──────────────────────────────────
 
    def test_num_hosts_31(self):
        result = calculate_subnet("192.168.1.0/31")
        self.assertEqual(result["num_hosts"], "2")
 
    def test_host_range_31(self):
        # Both addresses usable per RFC 3021
        result = calculate_subnet("192.168.1.0/31")
        self.assertEqual(result["host_min"], "192.168.1.0")
        self.assertEqual(result["host_max"], "192.168.1.1")
 
    # ── Edge: /32 (host route) ────────────────────────────────────────────────
 
    def test_num_hosts_32(self):
        result = calculate_subnet("192.168.1.1/32")
        self.assertEqual(result["num_hosts"], "1")
 
    def test_host_range_32(self):
        result = calculate_subnet("192.168.1.1/32")
        self.assertEqual(result["host_min"], "192.168.1.1")
        self.assertEqual(result["host_max"], "192.168.1.1")
 
    def test_network_broadcast_32(self):
        result = calculate_subnet("192.168.1.1/32")
        self.assertEqual(result["network"], "192.168.1.1")
        self.assertEqual(result["broadcast"], "192.168.1.1")
 
    # ── Edge: /0 (entire internet) ────────────────────────────────────────────
 
    def test_network_0(self):
        result = calculate_subnet("0.0.0.0/0")
        self.assertEqual(result["network"], "0.0.0.0")
 
    def test_broadcast_0(self):
        result = calculate_subnet("0.0.0.0/0")
        self.assertEqual(result["broadcast"], "255.255.255.255")
 
    def test_netmask_0(self):
        result = calculate_subnet("0.0.0.0/0")
        self.assertEqual(result["netmask"], "0.0.0.0")
 
    # ── Scope (private / public) ──────────────────────────────────────────────
 
    def test_private_10(self):
        result = calculate_subnet("10.0.0.0/8")
        self.assertIn("Private", result["scope"])
 
    def test_private_172(self):
        result = calculate_subnet("172.16.0.0/12")
        self.assertIn("Private", result["scope"])
 
    def test_private_192(self):
        result = calculate_subnet("192.168.0.0/16")
        self.assertIn("Private", result["scope"])
 
    def test_public(self):
        result = calculate_subnet("8.8.8.0/24")
        self.assertEqual(result["scope"], "Public")
 
    # ── Host bits set (strict=False behaviour) ────────────────────────────────
 
    def test_host_bits_set(self):
        # 192.168.1.10/24 — host bits set, should still give .0 network
        result = calculate_subnet("192.168.1.10/24")
        self.assertEqual(result["network"], "192.168.1.0")
 
    # ── IP class in result ────────────────────────────────────────────────────
 
    def test_ip_class_in_result_a(self):
        result = calculate_subnet("10.0.0.0/8")
        self.assertEqual(result["ip_class"], "A")
 
    def test_ip_class_in_result_c(self):
        result = calculate_subnet("192.168.1.0/24")
        self.assertEqual(result["ip_class"], "C")
 
    # ── Invalid inputs ────────────────────────────────────────────────────────
 
    def test_invalid_no_prefix(self):
        with self.assertRaises(ValueError):
            calculate_subnet("192.168.1.0")
 
    def test_invalid_bad_ip(self):
        with self.assertRaises(ValueError):
            calculate_subnet("999.999.999.999/24")
 
    def test_invalid_prefix_too_large(self):
        with self.assertRaises(ValueError):
            calculate_subnet("192.168.1.0/33")
 
    def test_invalid_empty_string(self):
        with self.assertRaises(ValueError):
            calculate_subnet("")
 
    def test_invalid_garbage(self):
        with self.assertRaises(ValueError):
            calculate_subnet("not-an-ip")
 
 
if __name__ == "__main__":
    unittest.main(verbosity=2)

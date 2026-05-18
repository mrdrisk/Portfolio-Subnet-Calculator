"""
conftest.py
Pytest configuration — loaded automatically before any tests run.
Adds the cli/ directory to sys.path so test files can import
subnet_utils, history, etc. without any extra setup.
"""
 
import sys
import os
 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "cli"))
 
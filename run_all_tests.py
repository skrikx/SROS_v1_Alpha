#!/usr/bin/env python3
"""
Master Test Runner for SROS v1 Alpha.
Runs all tests in the 'tests' directory using pytest.
"""
import sys
import pytest
import os

def main():
    """Run all tests."""
    print("==================================================")
    print("SROS v1 Alpha - Master Test Runner")
    print("==================================================")
    
    # Ensure the current directory is in sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    print(f"Running tests in: {os.path.join(current_dir, 'tests')}")
    print("--------------------------------------------------")
    
    # Run pytest
    # -v: verbose
    # -s: show stdout/stderr
    exit_code = pytest.main(["-v", "tests"])
    
    print("--------------------------------------------------")
    if exit_code == 0:
        print("SUCCESS: All tests passed.")
    else:
        print(f"FAILURE: Tests failed with exit code {exit_code}.")
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

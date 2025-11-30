#!/usr/bin/env python3
"""
Run all tests and generate test report

This script runs all tests and provides a summary report.
"""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run all tests and generate report"""
    print("="*70)
    print("Running Test Suite")
    print("="*70)
    
    # Run pytest with coverage
    result = subprocess.run(
        [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "-x",  # Stop on first failure
        ],
        cwd=Path(__file__).parent.parent,
    )
    
    if result.returncode == 0:
        print("\n" + "="*70)
        print("✅ All tests passed!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ Some tests failed")
        print("="*70)
        sys.exit(1)


if __name__ == "__main__":
    run_tests()


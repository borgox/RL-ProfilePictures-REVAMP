#!/usr/bin/env python3
"""
Test Runner Script for RLProfilePictures Backend

This script provides an easy way to run different test suites.
"""

import sys
import subprocess
import argparse


def run_command(cmd):
    """Run a command and return the exit code."""
    print(f"\n{'='*80}")
    print(f"Running: {' '.join(cmd)}")
    print(f"{'='*80}\n")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description='Run tests for RLProfilePictures Backend')
    parser.add_argument('suite', nargs='?', default='all', 
                       choices=['all', 'platform', 'epic', 'bulk', 'admin', 'performance', 'quick'],
                       help='Test suite to run (default: all)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-s', '--show', action='store_true', help='Show print statements')
    parser.add_argument('--cov', action='store_true', help='Run with coverage')
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ['pytest']
    
    # Add flags
    if args.verbose:
        base_cmd.append('-v')
    if args.show:
        base_cmd.append('-s')
    if args.cov:
        base_cmd.extend(['--cov=.', '--cov-report=html', '--cov-report=term-missing'])
    
    # Determine which tests to run
    test_suites = {
        'all': ['tests/'],
        'platform': ['tests/test_platform_routes.py'],
        'epic': ['tests/test_epic_routes.py'],
        'bulk': ['tests/test_bulk_routes.py'],
        'admin': ['tests/test_admin_stats_routes.py'],
        'performance': ['tests/test_performance_benchmark.py', '-v', '-s'],
        'quick': ['tests/', '-x', '--tb=short']  # Stop on first failure
    }
    
    cmd = base_cmd + test_suites[args.suite]
    
    # Run tests
    exit_code = run_command(cmd)
    
    # Print summary
    print(f"\n{'='*80}")
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print(f"{'='*80}\n")
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Simple Framework Runner

A simplified version for running a few combinations quickly.
"""

import subprocess
import sys
from pathlib import Path
import argparse


def run_combination(tool, software, cve):
    """Run a single combination and return success status."""
    root_dir = Path(__file__).parent.absolute()
    vul4c_script = root_dir / "Framework" / "vul4c.py"
    
    cmd = [
        sys.executable,
        str(vul4c_script),
        "--tool", tool,
        "--software", software, 
        "--CVEID", cve
    ]
    
    print(f"Running: {tool} -> {software} -> {cve}")
    result = subprocess.run(cmd, cwd=root_dir)
    
    success = result.returncode == 0
    status = "✓" if success else "✗"
    print(f"{status} {tool} -> {software} -> {cve}")
    
    return success


def main():
    parser = argparse.ArgumentParser(description="Simple framework runner")
    parser.add_argument('tool', help='Tool name (e.g., VulnFix)')
    parser.add_argument('software', help='Software name (e.g., audiofile)')
    parser.add_argument('cve', help='CVE ID (e.g., CVE-2017-6838)')
    
    args = parser.parse_args()
    
    success = run_combination(args.tool, args.software, args.cve)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

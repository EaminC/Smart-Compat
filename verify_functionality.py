#!/usr/bin/env python3
"""
Quick functionality verification script
"""

import subprocess
import sys
import os

def run_test(cmd, description):
    """Run a test command and report results"""
    print(f"\n🧪 Testing: {description}")
    print(f"Command: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ SUCCESS")
        elif result.returncode == 2:
            print("⚠️ CONFLICTS DETECTED (as expected)")
        else:
            print(f"❌ FAILED (exit code: {result.returncode})")
        
        # Show first few lines of output
        if result.stdout:
            lines = result.stdout.split('\n')[:5]
            for line in lines:
                if line.strip():
                    print(f"  {line}")
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def main():
    print("🚀 Package Conflict Detection Tool - Functionality Verification")
    print("=" * 70)
    
    # Test basic package detection
    run_test(
        'python compat-cli.py "requests==2.25.0" "urllib3==2.0.0"',
        "Basic package conflict detection"
    )
    
    # Test enhanced mode
    run_test(
        'python compat-cli.py enhanced "requests==2.25.0" "urllib3==1.26.0"',
        "Enhanced mode compatibility check"
    )
    
    # Test requirements.txt analysis - compatible
    run_test(
        'python compat-cli.py requirements data/examples/test_requirements1.txt data/examples/test_requirements3.txt',
        "Requirements.txt compatibility analysis (compatible)"
    )
    
    # Test requirements.txt analysis - conflicting
    run_test(
        'python compat-cli.py requirements data/examples/web_app_requirements.txt data/examples/conflicting_requirements.txt',
        "Requirements.txt compatibility analysis (conflicts)"
    )
    
    print("\n" + "=" * 70)
    print("🎉 Verification complete! Check results above.")

if __name__ == "__main__":
    main() 
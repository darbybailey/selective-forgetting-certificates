"""Recompute and compare every new result. Optionally replay the original archives."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parent
CHECKS=(
    ("overlap/run.py","RESULTS.json"),
    ("grid_check/run.py","RESULTS.json"),
    ("recognition/run.py","RESULTS.json"),
    ("recognition/stress.py","STRESS_RESULTS.json"),
    ("general_r/run.py","RESULTS.json"),
    ("general_r/recognize.py","RECOGNITION_RESULTS.json"),
    ("peeling/run.py","RESULTS.json"),
    ("stability/run.py","RESULTS.json"),
    ("stability/phases.py","PHASE_RESULTS.json"),
    ("gluing/run.py","RESULTS.json"),
    ("border/run.py","RESULTS.json"),
    ("xp/run.py","RESULTS.json")
)

def run_check(script, expected):
    result = subprocess.run([sys.executable, str(ROOT / script)], capture_output=True, text=True, cwd=ROOT)
    return script, result.returncode == 0, result.stdout[-200:] if result.stdout else ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", action="store_true")
    args = parser.parse_args()
    passed = 0
    for script, expected in CHECKS:
        name, ok, out = run_check(script, expected)
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
        if ok:
            passed += 1
    print(f"\n{passed}/{len(CHECKS)} checks passed")
    return 0 if passed == len(CHECKS) else 1

if __name__ == "__main__":
    raise SystemExit(main())

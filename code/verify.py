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
    ("xp/run.py","RESULTS.json"),
)
PRIOR=(
    ("Three_Actors_Proofs_and_Experiments.zip","22600b1fe9aafa484b895cc87c3fb2d4c059650be377a1fe84d698c62c12baa0",["--full","--jobs","2"]),
    ("Weighted_Colorings_Proofs_and_Tests.zip","c75887e56a2618f144b583eba85ea35fea053a683f608e741a86a41f5fba4d25",[]),
)


def verify(item):
    script,record=item
    path=ROOT/script
    output=subprocess.run([sys.executable,"-B",str(path)],cwd=path.parent,text=True,capture_output=True)
    if output.returncode!=0:
        raise RuntimeError(f"{script} failed\n{output.stderr}")
    actual=json.loads(output.stdout)
    expected=json.loads((path.parent/record).read_text())
    if actual!=expected:
        raise RuntimeError(f"{script} differed from {record}")
    return script


def replay_prior():
    for name,digest,args in PRIOR:
        archive=ROOT/'prior'/name
        if hashlib.sha256(archive.read_bytes()).hexdigest()!=digest:
            raise ValueError(f"Digest mismatch for {name}")
        with tempfile.TemporaryDirectory() as tmp, ZipFile(archive) as bundle:
            bundle.extractall(tmp)
            entry=Path(tmp)/"verify.py"
            if not entry.exists():
                matching=[p for p in Path(tmp).rglob("verify.py") if p.parent.parent==Path(tmp)]
                if len(matching)!=1:
                    raise ValueError(f"No unique top-level runner in {name}")
                entry=matching[0]
            run=subprocess.run([sys.executable,"-B",str(entry),*args],cwd=entry.parent,
                               capture_output=True,text=True)
            if run.returncode:
                raise RuntimeError(f"{name} failed\n{run.stderr}\n{run.stdout[-3000:]}")
        print(f"PASS  {name}",flush=True)


if __name__=="__main__":
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--prior",action="store_true",help="also extract and replay both earlier releases")
    args=cli.parse_args()
    with ThreadPoolExecutor(max_workers=3) as workers:
        for name in workers.map(verify,CHECKS):
            print(f"PASS  {name}",flush=True)
    if args.prior:
        replay_prior()

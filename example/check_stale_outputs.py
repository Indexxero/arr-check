#!/usr/bin/env python3
"""Checks that a receipt lists only files the run wrote, run fresh into a work folder.

    python3 example/check_stale_outputs.py <empty work folder>

Stated before the fix existed, from main 1e967be: a file put in the out folder before a run
was hashed into receipt.json as an output and receipt.py verify printed RECEIPT OK. Exit 0
only when:
  * a run into a new folder, and into an existing empty one, works as before;
  * a second run into a folder holding the first run's files is refused, exit 1, nothing
    in the folder changed;
  * the same second run with --replace (Larkspur with --deferred-gl, then without) works:
    its folder holds exactly the files a fresh run without --deferred-gl writes, its
    receipt names no ledger input and verifies;
  * with a file the previous receipt does not list planted beside it, --replace is
    refused and removes nothing;
  * a folder holding a file and no receipt.json is refused with and without --replace;
  * the stray file case from main: a hand made arr_adjusted.csv in the folder is never
    certified, because the run is refused.
  * a full run, then --profile --replace into the same folder: only manifest.json and
    profile.md remain, so --replace really removes the previous run's files.
"""
import hashlib, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
work = os.path.abspath(sys.argv[1])
os.makedirs(work, exist_ok=True)
B = ["--schedule", "example/inputs/schedule.csv", "--invoices", "example/inputs/invoices.csv", "--map", "example/inputs/mapping.json"]
GL = ["--deferred-gl", "example/inputs/deferred_gl.csv"]
bad = 0


def report(label, ok, detail=""):
    global bad
    bad += not ok
    print(f"  {'ok  ' if ok else 'FAIL'} {label:66s} {str(detail)[:80]}")


def run(out, *extra):
    return subprocess.run([sys.executable, "-W", "ignore", "pilot.py", *B, "--asof", "2025-10", "--out", out, *extra],
                          cwd=ROOT, capture_output=True, text=True)


def state(out):
    """Every file in the folder with its sha256; what 'nothing changed' is measured against."""
    return {f: hashlib.sha256(open(os.path.join(out, f), "rb").read()).hexdigest() for f in sorted(os.listdir(out))}


fresh = os.path.join(work, "fresh")
r = run(fresh)
report("a new folder: works as before", r.returncode == 0 and os.path.isfile(os.path.join(fresh, "receipt.json")), r.stderr[-80:])
empty = os.path.join(work, "empty")
os.makedirs(empty)
r = run(empty)
report("an existing empty folder: works as before", r.returncode == 0 and set(os.listdir(empty)) == set(os.listdir(fresh)), r.stderr[-80:])

x = os.path.join(work, "x")
r1 = run(x, *GL)
before = state(x)
r2 = run(x)
report("second run into the first run's folder, no --replace: refused, unchanged",
       r1.returncode == 0 and r2.returncode == 1 and "STOPPED, nothing written" in r2.stderr and state(x) == before, r2.stderr.strip()[-80:])
r3 = run(x, "--replace")
rec = json.load(open(os.path.join(x, "receipt.json"))) if r3.returncode == 0 else {}
report("with --replace: the folder holds exactly a fresh run's files", r3.returncode == 0 and set(os.listdir(x)) == set(os.listdir(fresh)),
       sorted(set(os.listdir(x)) ^ set(os.listdir(fresh))) or r3.stderr[-80:])
v = subprocess.run([sys.executable, "-W", "ignore", "receipt.py", "verify", "--out", x, *B], cwd=ROOT, capture_output=True, text=True)
report("with --replace: the receipt names no ledger input and verifies",
       "deferred_gl" not in rec.get("inputs", {}) and v.returncode == 0, (sorted(rec.get("inputs", {})), v.stdout.strip()[-20:]))

z = os.path.join(work, "z")
r7, r8 = run(z), run(z, "--profile", "--replace")
report("a full run, then --profile --replace: only the profile's two files remain",
       r7.returncode == 0 and r8.returncode == 0 and sorted(os.listdir(z)) == ["manifest.json", "profile.md"], sorted(os.listdir(z))[:6])

open(os.path.join(x, "arr_adjusted.csv"), "w").write("customer,arr\nPlanted Co,999999\n")
before = state(x)
r4 = run(x, "--replace")
report("a file the old receipt does not list: --replace refused, nothing removed",
       r4.returncode == 1 and "does not list" in r4.stderr and "arr_adjusted.csv" in r4.stderr and state(x) == before, r4.stderr.strip()[-80:])

y = os.path.join(work, "y")
os.makedirs(y)
open(os.path.join(y, "arr_adjusted.csv"), "w").write("customer,arr\nPlanted Co,999999\n")
before = state(y)
r5, r6 = run(y), run(y, "--replace")
report("a hand made file and no receipt: refused, with and without --replace",
       r5.returncode == 1 and r6.returncode == 1 and "no receipt.json" in r6.stderr and state(y) == before, (r5.returncode, r6.returncode))
report("the stray file is never certified: no receipt.json was written", not os.path.exists(os.path.join(y, "receipt.json")), sorted(os.listdir(y)))
print("RESULT:", "ALL AS STATED" if not bad else f"{bad} NOT AS STATED")
sys.exit(1 if bad else 0)

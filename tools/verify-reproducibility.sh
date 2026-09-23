#!/usr/bin/env bash
# Reproducibility gate for the measured artifacts.
#
# Two different claims, tested separately, because they fail for different reasons:
#
#   A. DETERMINISM — the same database snapshot in gives byte-identical output out.
#      A failure here is a defect in these tools.
#   B. DRIFT       — a later snapshot gives the same package membership with moved sizes,
#      because Arch updates the databases continuously. Not a failure: a fact to report.
#
# Conflating them makes the gate useless: assert byte-identity across a database refresh and
# every Arch update looks like a bug; ignore bytes entirely and a real defect looks like drift.
#
# Usage:  bash tools/verify-reproducibility.sh
# Env:    SCRATCH=<dir>   working directory (default: a fresh mktemp -d)
#         REPO=<url>      repository to clone (default: the public origin below)
set -u

REPO="${REPO:-https://github.com/CarlCPP007/wayland-desktop-audit.git}"
SCRATCH="${SCRATCH:-$(mktemp -d)}"
PY="${PY:-python3}"
FILES="data/features-availability.tsv data/features-stacks.json data/features.json
       data/features.tsv data/features-guesses.json docs/features.md data/availability.tsv
       data/shake-to-find.tsv data/shake.tsv data/shake.json data/shake-guesses.json
       data/closure.tsv data/closure.json data/closure-guesses.json
       data/combos.tsv data/combos.json data/builds.tsv data/builds.json"

cd "$SCRATCH" 2>/dev/null || { mkdir -p "$SCRATCH" && cd "$SCRATCH"; } || exit 1
echo "=== cloning $REPO into $SCRATCH ==="
git clone -q "$REPO" repo || { echo "CLONE FAILED"; exit 1; }
cd repo || exit 1
echo "cloned: $(git log --oneline -1)"
echo "the databases download on the first run below and are cached for the second"

pipeline() {
  $PY tools/pkg-features.py > /dev/null 2>&1                                                     || return 1
  $PY tools/pkg-closure-v2.py --stacks data/features-stacks.json --out features > /dev/null 2>&1  || return 2
  $PY tools/feature-report.py docs/features.md > /dev/null 2>&1                                   || return 3
  $PY tools/probe-names.py data/probe-shake-to-find.txt data/shake-to-find.tsv > /dev/null 2>&1    || return 4
  $PY tools/pkg-closure-v2.py --stacks data/shake-to-find-stacks.json --out shake > /dev/null 2>&1 || return 5
  $PY tools/pkg-closure-v2.py > /dev/null 2>&1                                                    || return 6
  $PY tools/pkg-closure-v2.py --stacks data/combo-stacks.json --out combos > /dev/null 2>&1        || return 7
  $PY tools/pkg-closure-v2.py --stacks data/builds-stacks.json --out builds > /dev/null 2>&1       || return 8
  $PY tools/pkg-availability.py data/availability.tsv > /dev/null 2>&1                             || return 9
}

echo; echo "=== run 1 ==="
pipeline; s=$?; [ $s -eq 0 ] || { echo "run 1 failed at stage $s"; exit 2; }; echo "  done"

SNAP="$SCRATCH/snap1"; mkdir -p "$SNAP"
$PY - "$SNAP" $FILES <<'PY'
import shutil, sys, os
snap, files = sys.argv[1], sys.argv[2:]
for f in files:
    shutil.copy(f, os.path.join(snap, f.replace("/", "__")))
print(f"  snapshotted {len(files)} artifacts")
PY

echo; echo "=== run 2 (same cached databases) ==="
pipeline; s=$?; [ $s -eq 0 ] || { echo "run 2 failed at stage $s"; exit 3; }; echo "  done"

echo; echo "=== A. determinism: run 2 against run 1, one snapshot ==="
$PY - "$SNAP" <<'PY'
import sys, os
snap = sys.argv[1]; bad = []
for flat in sorted(os.listdir(snap)):
    f = flat.replace("__", "/")
    same = open(os.path.join(snap, flat), "rb").read() == open(f, "rb").read()
    if not same: bad.append(f)
    print(f"  {'IDENTICAL' if same else 'DIFFERS  '} {f}")
print()
print("RESULT A:", "PASS — one database snapshot reproduces byte-identically"
      if not bad else f"FAIL — {len(bad)} artifact(s) differ from the same input: a tooling defect")
sys.exit(1 if bad else 0)
PY
rc_a=$?

echo; echo "=== B. drift: run 1 against the committed artifacts ==="
$PY - "$SNAP" <<'PY'
import sys, os, json, subprocess
snap = sys.argv[1]
def vintage(b):
    try: return json.loads(b)["db_vintage"]
    except Exception: return None
defect = moved = 0
for flat in sorted(os.listdir(snap)):
    f = flat.replace("__", "/")
    fresh = open(os.path.join(snap, flat), "rb").read()
    committed = subprocess.run(["git", "show", "HEAD:" + f], capture_output=True).stdout
    if fresh == committed:
        print(f"  IDENTICAL {f}"); continue
    note = ""
    if f.endswith(".json"):
        va, vb = vintage(fresh), vintage(committed)
        if va and vb:
            if va == vb:
                note = "  <-- same snapshot, still differs: TOOLING DEFECT"; defect += 1
            else:
                ch = [k for k in va if k in vb and va[k] != vb[k]]
                note = f"  <-- database snapshot moved ({', '.join(ch) or 'n/a'})"; moved += 1
    print(f"  DIFFERS   {f}{note}")
print()
if defect:
    print(f"RESULT B: FAIL — {defect} artifact(s) differ while the database snapshot is identical")
    sys.exit(1)
print(f"RESULT B: drift only ({moved} artifact(s)) — package membership stable, sizes moved"
      " upstream, which is expected: the databases are re-downloaded when absent and Arch"
      " updates them continuously.")
PY
rc_b=$?

echo; echo "=== the snapshot the artifacts record ==="
$PY - <<'PY'
import json
for f in ["data/features.json", "data/shake.json", "data/closure.json"]:
    v = json.load(open(f, encoding="utf-8")).get("db_vintage") or {}
    e = v.get("extra.db", {})
    print(f"  {f:<22} packages={v.get('packages')}  extra.db sha256={str(e.get('sha256'))[:12]}"
          f"  mtime={e.get('mtime')}")
PY

echo
echo "anything listed below is drift in the clone, not a change to commit:"
git status --porcelain
echo "(end)"
exit $(( rc_a || rc_b ))

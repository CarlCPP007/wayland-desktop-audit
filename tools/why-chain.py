#!/usr/bin/env python3
"""why-chain.py <stack> [<pkg> ...] — prove WHY a package is in a closure.

Walks the parent edges recorded by pkg-closure-v2.py from the package back to its stack
root and prints the chain with the exact dependency token at each hop. No chain, no claim:
if a package cannot be traced to a root, that is a resolver defect and says so.

Bare invocation (no package names) prints the tracer for the heaviest 10 members, which is
the verification step for the number the table reports.
"""
import json, os, sys

BASE = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + "/../data")
_a = sys.argv[1:]
FILE = "closure.json"
if "--file" in _a:
    i = _a.index("--file")
    FILE = _a[i + 1]
    del _a[i:i + 2]
sys.argv = [sys.argv[0]] + _a
doc = json.load(open(os.path.join(BASE, FILE), encoding="utf-8"))
PARENTS = doc["parents"]
DETAIL = doc["detail"]

stack = sys.argv[1]
if stack not in PARENTS:
    print("unknown stack. known:", "\n  " + "\n  ".join(PARENTS))
    sys.exit(2)
PARENTS = PARENTS[stack]
DETAIL = DETAIL[stack]
print(f"stack {stack}: {len(PARENTS)} traced members, {len(DETAIL)} in closure")

targets = sys.argv[2:]
if not targets:
    row = next(r for r in doc["rows"] if r["stack"] == stack)
    targets = [h["pkg"] for h in row["heaviest_marginal"]]

for t in targets:
    chain, node, guard = [], t, 0
    while node in PARENTS and guard < 60:
        parent, token = PARENTS[node]
        chain.append(f"{parent}  --[{token}]-->  {node}")
        node, guard = parent, guard + 1
    print(f"\n=== {t} ===")
    if not chain:
        print(f"  ROOT of the stack (nothing depends on it) OR UNTRACEABLE — investigate")
    else:
        print(f"  hops: {len(chain)}   root: {node}")
        for c in reversed(chain):
            print("   ", c)

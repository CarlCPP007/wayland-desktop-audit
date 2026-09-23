#!/usr/bin/env python3
"""why <pkg> [<pkg> ...] — show the raw DEPENDS lines from the cached Arch db.
Ground truth for a suspicious closure member: what declares it, and how.
"""
import os, sys, tarfile
from collections import defaultdict

DB = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + "/../data/db")


def parse_desc(text):
    out, key = {}, None
    for line in text.splitlines():
        if not line.strip():
            key = None
            continue
        if line.startswith("%") and line.endswith("%"):
            key = line.strip("%")
            out.setdefault(key, [])
        elif key:
            out[key].append(line)
    return out


pkgs = {}
for name in ("core.db", "extra.db", "multilib.db"):
    p = os.path.join(DB, name)
    if not os.path.exists(p):
        continue
    with tarfile.open(p, "r:gz") as tf:
        for m in tf.getmembers():
            if not m.name.endswith("/desc"):
                continue
            d = parse_desc(tf.extractfile(m).read().decode("utf-8", "replace"))
            pkgs[d["NAME"][0]] = {"repo": name.split(".")[0], "depends": d.get("DEPENDS", []),
                                  "provides": d.get("PROVIDES", []), "optd": d.get("OPTDEPENDS", [])}

# who declares each name as a hard dep?
rev = defaultdict(list)
for n, p in pkgs.items():
    for d in p["depends"]:
        rev[d.split("=")[0]].append(n)
    for d in p["optd"]:
        rev[d.split(":")[0].split("=")[0]].append(n + "  [OPT]")
    for x in p["provides"]:
        rev[x.split("=")[0]].append(n + "  [PROVIDES]")

for target in sys.argv[1:]:
    print(f"\n=== {target} ===")
    if target in pkgs:
        p = pkgs[target]
        print(f"  repo={p['repo']}  hard deps ({len(p['depends'])}):")
        for d in p["depends"]:
            print("    ", d)
    else:
        print("  (not a package name in the db)")
    print(f"  declared as a dep/provide of ({len(rev[target])}):")
    for n in sorted(rev[target])[:30]:
        print("    ", n)

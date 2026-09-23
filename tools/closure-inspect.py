#!/usr/bin/env python3
"""Diagnose the closure result — find what a stack pulls that it should not.
Reuses data/db/*.db and data/closure.json. Read-only.
"""
import json, os, tarfile, sys
from collections import defaultdict

BASE = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + "/../data")
DB = os.path.join(BASE, "db")


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
    repo = name.split(".")[0]
    with tarfile.open(p, "r:gz") as tf:
        for m in tf.getmembers():
            if not m.name.endswith("/desc"):
                continue
            d = parse_desc(tf.extractfile(m).read().decode("utf-8", "replace"))
            n = d["NAME"][0]
            pkgs[n] = {"repo": repo, "isize": int(d.get("ISIZE", ["0"])[0] or 0),
                       "depends": d.get("DEPENDS", []), "provides": d.get("PROVIDES", []),
                       "desc": (d.get("DESC", [""])[0])[:60]}

doc = json.load(open(os.path.join(BASE, "closure.json"), encoding="utf-8"))
detail = doc["detail"]
stacks = sys.argv[1:] or list(detail)

MB = 1048576
for s in stacks:
    names = detail[s]
    sizes = sorted(((pkgs[n]["isize"], n) for n in names if n in pkgs), reverse=True)
    print(f"\n=== {s}  ({len(names)} pkgs, {sum(x for x,_ in sizes)/MB:.0f} MB) ===")
    print("  top 12 by installed size:")
    for sz, n in sizes[:12]:
        print(f"    {sz/MB:8.1f} MB  {n:<28} {pkgs[n]['repo']:<8} {pkgs[n]['desc']}")

if len(stacks) == 2:
    a, b = (set(detail[s]) for s in stacks)
    only_a = sorted(((pkgs[n]["isize"], n) for n in a - b if n in pkgs), reverse=True)
    only_b = sorted(((pkgs[n]["isize"], n) for n in b - a if n in pkgs), reverse=True)
    print(f"\n=== ONLY in {stacks[0]} ({len(only_a)} pkgs, {sum(x for x,_ in only_a)/MB:.0f} MB) ===")
    for sz, n in only_a[:20]:
        print(f"    {sz/MB:8.1f} MB  {n:<28} {pkgs[n]['desc']}")
    print(f"\n=== ONLY in {stacks[1]} ({len(only_b)} pkgs, {sum(x for x,_ in only_b)/MB:.0f} MB) ===")
    for sz, n in only_b[:20]:
        print(f"    {sz/MB:8.1f} MB  {n:<28} {pkgs[n]['desc']}")

# how wide are the provider sets for common sonames? (the suspected bug)
print("\n=== provider fan-out for sonames that commonly appear as deps ===")
prov = defaultdict(list)
for n, p in pkgs.items():
    for x in p["provides"]:
        prov[x.split("=")[0]].append(n)
interesting = [k for k in prov if len(prov[k]) > 3 and (".so" in k or "sh" == k)]
for k in sorted(interesting, key=lambda k: -len(prov[k]))[:25]:
    print(f"  {k:<34} {len(prov[k]):>3} providers: {', '.join(sorted(prov[k])[:8])}")

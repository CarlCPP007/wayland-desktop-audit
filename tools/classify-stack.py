#!/usr/bin/env python3
"""classify-stack.py <label> <names-file> [...] --out <stacks.json>

Classify a build's package list as official-repo vs AUR (offline db + AUR RPC), then emit a
stacks JSON that pkg-closure-v2.py consumes via --stacks. Names are read literally from the
build's own package list — never retyped by hand, so a typo cannot become a finding.

names-file format: one package per line; `#` starts a comment (impasto's lists annotate every
package with its reason, so comments must be stripped, not dropped silently).
"""
import json, os, re, sys, tarfile, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.normpath(HERE + "/../data")
DB = os.path.join(EV, "db")


def official_names():
    names = set()
    for f in ("core.db", "extra.db", "multilib.db"):
        p = os.path.join(DB, f)
        if not os.path.exists(p):
            continue
        with tarfile.open(p, "r:gz") as tf:
            for m in tf.getmembers():
                if m.name.endswith("/desc"):
                    names.add(os.path.basename(os.path.dirname(m.name)).rsplit("-", 2)[0])
    return names


def parse_names(path):
    out = []
    for line in open(path, encoding="utf-8", errors="replace"):
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


def aur_info(names):
    got = {}
    for i in range(0, len(names), 100):
        chunk = names[i:i + 100]
        url = ("https://aur.archlinux.org/rpc/?v=5&type=info&"
               + "&".join("arg[]=" + urllib.parse.quote(n) for n in chunk))
        try:
            d = json.load(urllib.request.urlopen(url, timeout=30))
            for r in d.get("results", []):
                got[r["Name"]] = {"votes": r.get("NumVotes", 0), "ver": r.get("Version"),
                                  "maint": r.get("Maintainer"), "out": r.get("OutOfDate")}
        except Exception as e:
            print("  AUR RPC err:", e)
    return got


def main():
    args = sys.argv[1:]
    out_path = args[args.index("--out") + 1]
    pairs = [(args[i], args[i + 1]) for i in range(0, args.index("--out"), 2)]

    off = official_names()
    stacks, report = {}, {}
    for label, path in pairs:
        want = parse_names(path)
        roots, unknown = [], []
        need_aur = [n for n in want if n not in off]
        aur = aur_info(sorted(set(need_aur)))
        for n in want:
            if n in off:
                roots.append(["repo", n])
            elif n in aur:
                roots.append(["aur", n])
            else:
                unknown.append(n)
        stacks[label] = roots
        report[label] = {"total": len(want), "official": len(roots) - len([r for r in roots if r[0] == "aur"]),
                         "aur": {n: aur[n] for n in want if n in aur}, "unknown": unknown}

    json.dump(stacks, open(out_path, "w", encoding="utf-8", newline="\n"), indent=1)
    for label, r in report.items():
        print(f"\n=== {label} — {r['total']} declared, {r['official']} official, {len(r['aur'])} AUR, "
              f"{len(r['unknown'])} unknown ===")
        for n, v in sorted(r["aur"].items(), key=lambda kv: -kv[1]["votes"]):
            flag = "  OUT-OF-DATE" if v["out"] else ""
            print(f"  AUR {n:<30} {v['ver']:<24} votes={v['votes']:<4} maint={v['maint']}{flag}")
        if r["unknown"]:
            print("  UNKNOWN (not in repos, not in AUR — check spelling):", r["unknown"])
    print(f"\nwrote {out_path}")


main()

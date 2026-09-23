#!/usr/bin/env python3
"""Feature hunt, stage 1 — availability.

Reads a catalog of desktop features and their candidate packages
(`data/features-catalog.json`), probes every candidate against the official
repositories first and the AUR second, and writes two files:

  <prefix>-availability.tsv   feature, pkg, where, repo, version, votes,
                              depends_n, installed_bytes, desc
  <prefix>-stacks.json        resolver input for pkg-closure-v2.py:
                              {"<feature> :: <pkg>": [[repo|aur, pkg]]}

A candidate that exists nowhere is reported as NONE and left out of the
resolver input, so a typo can never become a fake row in the cost table.

No third-party dependencies: urllib + json only.
"""
import json, os, sys, time, urllib.parse, urllib.request

ARCH = "https://archlinux.org/packages/search/json/?name="
AUR = "https://aur.archlinux.org/rpc/?v=5&type=info&arg[]="
HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.normpath(HERE + "/../data")


def get(url, tries=3):
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    return {"__error__": str(last)}


def official(name):
    d = get(ARCH + urllib.parse.quote(name))
    for res in d.get("results", []):
        # accept arch-independent packages too: fonts, icon themes and tools such as
        # tlp/ranger ship as "any" and are just as installable as x86_64 ones
        if res.get("pkgname") == name and res.get("arch") in ("x86_64", "any"):
            return res
    return None


def aur(name):
    d = get(AUR + urllib.parse.quote(name))
    for res in d.get("results", []):
        if res.get("Name") == name:
            return res
    return None


def main():
    catalog = sys.argv[1] if len(sys.argv) > 1 else os.path.join(OUTDIR, "features-catalog.json")
    prefix = sys.argv[2] if len(sys.argv) > 2 else os.path.join(OUTDIR, "features")
    with open(catalog, encoding="utf-8") as f:
        cat = json.load(f)

    rows, stacks, none = [], {}, []
    for feature, candidates in cat["features"].items():
        for name in candidates:
            o = official(name)
            if o:
                rows.append((feature, name, "official", o.get("repo", "?"),
                             f"{o.get('pkgver')}-{o.get('pkgrel')}", "",
                             len(o.get("depends") or []), o.get("installed_size") or 0,
                             (o.get("pkgdesc") or "")[:60]))
                stacks[f"{feature} :: {name}"] = [["repo", name]]
                print(f"  ok  {feature:<18} {name:<24} official/{o.get('repo')} {o.get('pkgver')}")
                continue
            a = aur(name)
            if a:
                rows.append((feature, name, "AUR", "-", a.get("Version", "?"),
                             a.get("NumVotes", 0), len(a.get("Depends") or []), 0,
                             (a.get("Description") or "")[:60]))
                stacks[f"{feature} :: {name}"] = [["aur", name]]
                print(f"  ok  {feature:<18} {name:<24} AUR ({a.get('NumVotes', 0)} votes)")
                continue
            rows.append((feature, name, "NONE", "-", "-", "", 0, 0, ""))
            none.append(f"{feature}/{name}")
            print(f"  --  {feature:<18} {name:<24} NOT FOUND — excluded")

    with open(prefix + "-availability.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("feature\tpkg\twhere\trepo\tversion\tvotes\tdepends_n\tinstalled_bytes\tdesc\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")
    with open(prefix + "-stacks.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(stacks, f, indent=1, sort_keys=True)

    found = len(rows) - len(none)
    print(f"\n{found}/{len(rows)} candidates exist · {len(stacks)} queued for costing")
    if none:
        print("not found (excluded):", ", ".join(none))
    print("written:", prefix + "-availability.tsv", "and", prefix + "-stacks.json")


if __name__ == "__main__":
    main()

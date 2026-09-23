#!/usr/bin/env python3
"""Probe an ad-hoc candidate list: official repos first, then AUR.

Input: a file of `axis<TAB>name` lines (or bare `name`), `#` comments ignored.
Output: a table on stdout, and a TSV suitable for `pkg-closure-v2.py --stacks`.

This is the entry point for "I want feature X" — a name typed in chat has to be
proven to exist before it is costed, or the run reports a plausible-looking zero.
No third-party deps: urllib + json only.
"""
import json, sys, urllib.request, urllib.parse, time

ARCH = "https://archlinux.org/packages/search/json/?name="
AUR = "https://aur.archlinux.org/rpc/?v=5&type=info&arg[]="


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
    for res in get(ARCH + urllib.parse.quote(name)).get("results", []):
        # "any" matters: fonts, icon themes and plugin assets are published arch-independent
        if res.get("pkgname") == name and res.get("arch") in ("x86_64", "any"):
            return res
    return None


def aur(name):
    for res in get(AUR + urllib.parse.quote(name)).get("results", []):
        if res.get("Name") == name:
            return res
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: probe-names.py <candidates file> [out.tsv]")
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None

    cands = []
    for line in open(src, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        parts = line.split("\t") if "\t" in line else ["candidate", line.strip()]
        cands.append((parts[0].strip(), parts[1].strip()))

    rows = []
    for axis, name in cands:
        o = official(name)
        if o:
            rows.append((axis, name, "official", o.get("repo", "?"),
                         f"{o.get('pkgver')}-{o.get('pkgrel')}", "",
                         len(o.get("depends") or []), o.get("installed_size") or 0,
                         (o.get("pkgdesc") or "")[:60]))
            continue
        a = aur(name)
        if a:
            rows.append((axis, name, "AUR", "-", a.get("Version", "?"), a.get("NumVotes", 0),
                         len(a.get("Depends") or []), 0, (a.get("Description") or "")[:60]))
            continue
        rows.append((axis, name, "NONE", "-", "-", "", 0, 0, ""))

    print(f"{'axis':<22}{'pkg':<38}{'where':<9}{'repo':<7}{'version':<24}{'votes':>5}{'dep':>5}{'instMB':>9}  desc")
    print("-" * 150)
    for r in rows:
        mb = f"{r[7]/1048576:.1f}" if r[7] else "-"
        print(f"{r[0]:<22}{r[1]:<38}{r[2]:<9}{r[3]:<7}{r[4]:<24}{str(r[5]):>5}{r[6]:>5}{mb:>9}  {r[8]}")

    missing = [r[1] for r in rows if r[2] == "NONE"]
    if missing:
        # NONE is a claim about the name, not proof of absence: check the raw response
        # for one of them before treating any of these as non-existent
        print(f"\nnot found under that exact name: {', '.join(missing)}")
        print("search the AUR by keyword before dropping: "
              "curl -s 'https://aur.archlinux.org/rpc/?v=5&type=search&arg=<keyword>'")

    if out:
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write("axis\tpkg\twhere\trepo\tversion\tvotes\tdepends_n\tinstalled_bytes\tdesc\n")
            for r in rows:
                f.write("\t".join(str(x) for x in r) + "\n")
        print("\nwritten:", out)


if __name__ == "__main__":
    main()

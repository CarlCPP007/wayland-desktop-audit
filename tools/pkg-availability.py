#!/usr/bin/env python3
"""Pass 2a — package availability. Official repos first, then AUR.
Writes TSV: name, source, repo, version, votes, depends_n, installed_bytes
No third-party deps: urllib + json only.
"""
import json, sys, urllib.request, urllib.parse, time

ARCH = "https://archlinux.org/packages/search/json/?name="
AUR = "https://aur.archlinux.org/rpc/?v=5&type=info&arg[]="

CANDIDATES = [
    # compositors
    ("COMP", "hyprland"), ("COMP", "niri"), ("COMP", "sway"), ("COMP", "river"),
    ("COMP", "labwc"), ("COMP", "wayfire"), ("COMP", "dwl"), ("COMP", "mango"),
    ("COMP", "mangowm-git"), ("COMP", "hyprland-git"), ("COMP", "sway-git"),
    # shells / bars  (the RAM lever)
    ("SHELL", "noctalia"), ("SHELL", "noctalia-shell"), ("SHELL", "noctalia-git"),
    ("SHELL", "quickshell"), ("SHELL", "quickshell-git"),
    ("SHELL", "dms-shell"), ("SHELL", "dms-shell-hyprland"), ("SHELL", "dms-shell-niri"),
    ("SHELL", "waybar"), ("SHELL", "hyprpanel"), ("SHELL", "caelestia-shell"),
    ("SHELL", "aylurs-gtk-shell"), ("SHELL", "ags"), ("SHELL", "nwg-shell"),
    ("SHELL", "yambar"), ("SHELL", "sfwbar"),
    # theme engines
    ("THEME", "matugen"), ("THEME", "wallust"), ("THEME", "python-pywal"), ("THEME", "pywal"),
]


def get(url, tries=3):
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


rows = []
for axis, name in CANDIDATES:
    o = official(name)
    if o:
        rows.append((axis, name, "official", o.get("repo", "?"), f"{o.get('pkgver')}-{o.get('pkgrel')}",
                     "", len(o.get("depends") or []), o.get("installed_size") or 0,
                     (o.get("pkgdesc") or "")[:50]))
        continue
    a = aur(name)
    if a:
        rows.append((axis, name, "AUR", "-", a.get("Version", "?"), a.get("NumVotes", 0),
                     len(a.get("Depends") or []), 0, (a.get("Description") or "")[:50]))
        continue
    rows.append((axis, name, "NONE", "-", "-", "", 0, 0, ""))

print(f"{'axis':<6}{'pkg':<24}{'where':<9}{'repo':<7}{'version':<26}{'votes':>5}{'dep':>5}{'instMB':>9}  desc")
print("-" * 132)
for r in rows:
    mb = f"{r[7]/1048576:.1f}" if r[7] else "-"
    print(f"{r[0]:<6}{r[1]:<24}{r[2]:<9}{r[3]:<7}{r[4]:<26}{str(r[5]):>5}{r[6]:>5}{mb:>9}  {r[8]}")

with open(sys.argv[1] if len(sys.argv) > 1 else "availability.tsv", "w", encoding="utf-8", newline="\n") as f:
    f.write("axis\tpkg\twhere\trepo\tversion\tvotes\tdepends_n\tinstalled_bytes\tdesc\n")
    for r in rows:
        f.write("\t".join(str(x) for x in r) + "\n")
print("\nwritten:", sys.argv[1] if len(sys.argv) > 1 else "availability.tsv")

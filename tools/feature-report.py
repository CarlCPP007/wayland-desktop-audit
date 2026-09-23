#!/usr/bin/env python3
"""Feature hunt, stage 2 — the report.

Merges the two measured files into one markdown comparison, one table per
feature:

  <prefix>-availability.tsv   where each candidate lives (official / AUR),
                              its version and vote count
  <prefix>.tsv                its full closure, measured: packages + MB

Usage:  python tools/feature-report.py [outfile]

Costs are full transitive closures resolved against the Arch core/extra/
multilib databases, so a candidate's cost includes everything it drags in.
AUR candidates are a lower bound: an AUR package's own dependencies are read
from the AUR RPC and anything unreachable is reported rather than guessed, so
a low AUR figure means "not measurable offline", not "small".
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.normpath(HERE + "/../data")

INTRO = """# Feature hunt — what each desktop feature costs

Every candidate below was probed for real availability and then costed as a
full transitive dependency closure against the Arch `core`/`extra`/`multilib`
databases. Nothing in this file is estimated: a candidate that does not exist in
either repository was removed from the run, and the replacing of five such names
(`swww`, `rofi-wayland`, `hyprshot`, `rofimoji`, `pywal16`) is recorded in
`data/features-catalog.json`.

**How to read the numbers.** `packages` and `MB` are the candidate's *entire*
closure — the package plus everything it needs. They are not directly
comparable across different features (a bar and a file manager do different
jobs); compare candidates *within* a row. `marginal` in
`data/features.tsv` equals the total here, because the intersection across 145
measured stacks is empty.

**AUR rows are a lower bound.** An official package resolves exactly, offline,
from the database dump. An AUR package has its own dependencies read from the
AUR RPC, but a dependency that cannot be reached that way is reported as
unresolved instead of guessed — so a suspiciously low AUR figure means
"not measurable offline", not "small". Where an AUR candidate resolved to a
single package or none at all it is marked **(unmeasurable)** and excluded from
the cheapest-option summary.

**Closures overlap heavily between features.** Each figure is a candidate's
whole closure, so `pavucontrol` reads 1,094 MB and `swayosd` 1,006 MB mostly
because both pay for the same GTK3 stack. The useful signal is the ordering
within a row and the outliers, not the absolute figure: once a toolkit is
already installed for something else, the next candidate on that toolkit is
almost free. The three whole builds measured in `data/builds.tsv` show what the
parts cost when combined — `hyprland` + `wayle` + `rust-dock` comes to
1,113.7 MB in total, less than any single bar candidate above listed alone.

A dagger (†) marks an AUR candidate: it needs `git`/`makepkg` at install time
and is not covered by the binary-repository trust chain.
"""


def read_tsv(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        head = f.readline().rstrip("\n").split("\t")
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            rows.append(dict(zip(head, line.split("\t"))))
    return rows


def measurable(r):
    """A closure of 0-1 packages means the AUR RPC never reached that package's
    dependencies, so the figure is a measurement gap, not a small install."""
    return not (r[2] <= 1 and r[1].get("where") == "AUR")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else None

    avail = {}
    for r in read_tsv(os.path.join(OUTDIR, "features-availability.tsv")):
        avail[(r["feature"], r["pkg"])] = r

    cost = {}
    for r in read_tsv(os.path.join(OUTDIR, "features.tsv")):
        if " :: " not in r["stack"]:
            continue                     # skip the built-in compositor stacks
        feature, pkg = r["stack"].split(" :: ", 1)
        cost[(feature, pkg)] = (int(r["pkgs"]), float(r["installed_MB"]),
                                r["aur_roots"], r["aur_unresolved"])

    features = {}
    for (feature, pkg), (pkgs, mb, aur_roots, unresolved) in cost.items():
        a = avail.get((feature, pkg), {})
        features.setdefault(feature, []).append((pkg, a, pkgs, mb, aur_roots, unresolved))

    lines = [INTRO]
    summary = []
    for feature in sorted(features):
        rows = sorted(features[feature], key=lambda r: r[3])
        mrows = [r for r in rows if measurable(r)]
        cheapest = mrows[0][3] if mrows else None
        lines.append(f"\n## {feature}\n")
        lines.append("| candidate | where | version | votes | packages | MB | vs cheapest measured |")
        lines.append("|---|---|---|---|---|---|---|")
        for pkg, a, pkgs, mb, aur_roots, unresolved in rows:
            where = a.get("where", "?")
            mark = "†" if where == "AUR" else ""
            version = a.get("version", "?")
            votes = a.get("votes", "") or ""
            note = ""
            if not measurable((pkg, a, pkgs, mb, aur_roots, unresolved)):
                note = " **(unmeasurable)**"
                delta_s = "—"
            elif mb == cheapest:
                delta_s = "cheapest measured"
            else:
                delta_s = f"+{mb - cheapest:,.1f} MB"
            lines.append(f"| `{pkg}`{mark} | {where} | {version} | {votes} | "
                         f"{pkgs}{note} | {mb:,.1f} | {delta_s} |")
        worst = mrows[-1] if mrows else None
        offrows = [r for r in mrows if r[1].get("where") == "official"]
        off = offrows[0] if offrows else None
        # a slot can have no official candidate at all (emoji picker): say so
        # rather than printing an empty cell that reads like a zero
        if off is None:
            off_cell = "none — AUR-only slot"
        else:
            off_cell = f"`{off[0]}` at {off[3]:,.1f} MB"
        if mrows:
            lines.append(f"\nCheapest measured: **`{mrows[0][0]}`** at {mrows[0][3]:,.1f} MB. "
                         f"Dearest measured: `{worst[0]}` at {worst[3]:,.1f} MB "
                         f"(swing {worst[3] - mrows[0][3]:,.1f} MB). "
                         f"Cheapest official: {off_cell}.")
        else:
            lines.append("\nNo candidate in this slot could be measured offline.")
        summary.append((feature,
                        mrows[0][0] if mrows else "-", mrows[0][3] if mrows else None,
                        mrows[0][1].get("where", "?") if mrows else "-",
                        off[0] if off else "—", off[3] if off else None,
                        worst[0] if worst else "—", worst[3] if worst else None))

    lines.append("\n## Summary — cheapest measured option per feature\n")
    lines.append("Candidates marked unmeasurable are excluded here; \"cheapest official\" is the "
                 "best option needing no build step.\n")
    lines.append("| feature | cheapest measured | where | MB | cheapest official | MB | dearest measured | MB | swing |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for feature, bpkg, bmb, where, opkg, omb, wpkg, wmb in summary:
        bs = "" if bmb is None else f"{bmb:,.1f}"
        os_ = "" if omb is None else f"{omb:,.1f}"
        ws = "" if wmb is None else f"{wmb:,.1f}"
        sw = "" if (bmb is None or wmb is None) else f"{wmb - bmb:,.1f}"
        lines.append(f"| {feature} | `{bpkg}`{'†' if where == 'AUR' else ''} | {where} | "
                     f"{bs} | {opkg if opkg == '—' else '`' + opkg + '`'} | {os_} | `{wpkg}` | {ws} | {sw} |")

    lines.append("\n† AUR: not in the binary repositories; requires building from "
                 "source at install time.\n")
    doc = "\n".join(lines) + "\n"

    if out:
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            f.write(doc)
        print(f"written: {out}")
    else:
        print(doc)
    print(f"{len(summary)} features, "
          f"{sum(len(v) for v in features.values())} candidates costed")


if __name__ == "__main__":
    main()

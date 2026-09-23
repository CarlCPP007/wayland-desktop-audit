#!/usr/bin/env python3
"""Pass 2b (v2) — real install cost per candidate STACK.  Supersedes pkg-closure.py (v1).

Downloads the Arch repo databases once, resolves transitive dependency closures OFFLINE.

v2 fixes a MEASURED defect in v1: `libglvnd` hard-depends on the VIRTUAL `opengl-driver`,
which is provided by both `mesa` (18 deps) and `nvidia-utils` (5 deps). v1's "fewest deps"
tie-break therefore picked the 948 MB NVIDIA driver as the GL provider in every stack, and
asymmetrically (sway also pulled lib32-nvidia-utils, +562 MB). Those virtuals are satisfied
by the HARDWARE, never by the desktop choice, so v2 refuses to resolve them and records the
skipped names instead. Every remaining multi-provider choice is logged to
data/provider-guesses.json so a bad guess is visible, not silently inflating a number.

Writes data/closure.json, data/closure.tsv, data/provider-guesses.json.
"""
import json, os, re, sys, tarfile, urllib.parse, urllib.request
import datetime, hashlib
from collections import defaultdict

OUTDIR = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + "/../data")
CACHE = os.path.join(OUTDIR, "db")
OUT_NAME = "closure"
os.makedirs(CACHE, exist_ok=True)

MIRRORS = ["https://geo.mirror.pkgbuild.com",
           "https://fastly.mirror.pkgbuild.com",
           "https://mirrors.kernel.org/archlinux"]
REPOS = [("core", "core/os/x86_64/core.db"),
         ("extra", "extra/os/x86_64/extra.db"),
         ("multilib", "multilib/os/x86_64/multilib.db")]

# Virtuals satisfied by the MACHINE, not by the stack choice. Resolving these by guess is
# what produced the v1 defect. Recorded and skipped, never guessed.
EXTERNAL_VIRTUALS = {
    "opengl-driver", "vulkan-driver", "lib32-opengl-driver", "lib32-vulkan-driver",
    "ttf-font", "ttf-font-nerd",            # font choice, not stack choice
    "sh", "awk",                            # base system already satisfies these
    "wayland-compositor",                   # the stack root itself provides it
}

# Hardware drivers / alternative GPU stacks must never satisfy a generic soname.
DRIVER_RE = re.compile(
    r"^(lib32-)?(nvidia-utils|nvidia-open.*|rocm-.*|opencl-(nvidia|rocm).*"
    r"|vulkan-(nouveau|radeon|intel|swrast|virtio|dozen|microsoft|broadcom).*)$")

# `xdg-desktop-portal-impl` is a virtual with four real providers. Picking by "fewest deps"
# pulled a Qt/KDE portal into stacks that have no Qt (measured: qt6-base +66 MB appeared in
# the niri+noctalia closure). The portal follows the COMPOSITOR, so it is chosen by name.
PORTAL_PREF = {
    "hyprland": "xdg-desktop-portal-hyprland",
    "niri": "xdg-desktop-portal-gtk",
    "sway": "xdg-desktop-portal-gtk",
    "labwc": "xdg-desktop-portal-gtk",
    "river": "xdg-desktop-portal-wlr",
    "mangowm": "xdg-desktop-portal-gtk",
}

STACKS = {
    "hyprland+noctalia+matugen":  [("repo", "hyprland"), ("repo", "noctalia"), ("repo", "matugen")],
    "hyprland+dms+matugen":       [("repo", "hyprland"), ("repo", "dms-shell-hyprland"), ("repo", "matugen")],
    "niri+noctalia+matugen":      [("repo", "niri"), ("repo", "noctalia"), ("repo", "matugen")],
    "niri+dms+matugen":           [("repo", "niri"), ("repo", "dms-shell-niri"), ("repo", "matugen")],
    "sway+waybar+wallust":        [("repo", "sway"), ("repo", "waybar"), ("aur", "wallust")],
    "labwc+waybar+wallust":       [("repo", "labwc"), ("repo", "waybar"), ("aur", "wallust")],
    "river+yambar+wallust":       [("repo", "river"), ("aur", "yambar"), ("aur", "wallust")],
    "hyprland+caelestia+matugen": [("repo", "hyprland"), ("aur", "caelestia-shell"), ("repo", "matugen")],
    "mangowm+quickshell+matugen": [("aur", "mangowm-git"), ("repo", "quickshell"), ("repo", "matugen")],
}


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 100000:
        return dest
    tmp = dest + ".part"
    print(f"  GET {url}")
    with urllib.request.urlopen(url, timeout=240) as r, open(tmp, "wb") as f:
        while True:
            c = r.read(1 << 20)
            if not c:
                break
            f.write(c)
    os.replace(tmp, dest)
    return dest


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


def load_db(path, repo):
    pkgs = {}
    with tarfile.open(path, "r:gz") as tf:
        for m in tf.getmembers():
            if not m.name.endswith("/desc"):
                continue
            d = parse_desc(tf.extractfile(m).read().decode("utf-8", "replace"))
            n = d["NAME"][0]
            pkgs[n] = {"name": n, "repo": repo,
                       "version": d.get("VERSION", [""])[0],
                       "isize": int(d.get("ISIZE", ["0"])[0] or 0),
                       "depends": d.get("DEPENDS", []),
                       "provides": d.get("PROVIDES", []),
                       "desc": (d.get("DESC", [""])[0])[:70]}
    return pkgs


def db_vintage(paths):
    """Every number here measures one snapshot of the Arch databases, so the snapshot
    travels with the output. Without it, a size that moved between two runs is
    indistinguishable from a defect in the resolver: the databases are re-downloaded
    only when absent, and Arch updates them continuously, so a second run against a
    fresh copy legitimately reports different megabytes for the same package set."""
    out = {}
    for p in paths:
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        st = os.stat(p)
        out[os.path.basename(p)] = {
            "sha256": h.hexdigest(),
            "mtime": datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "bytes": st.st_size,
        }
    return out


def aur_rpc(names):
    if not names:
        return {}
    url = ("https://aur.archlinux.org/rpc/?v=5&type=info&"
           + "&".join("arg[]=" + urllib.parse.quote(n) for n in names))
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            d = json.loads(r.read().decode())
    except Exception as e:
        print("  AUR RPC failed:", e)
        return {}
    return {x["Name"]: {"version": x.get("Version"), "depends": x.get("Depends") or [],
                        "votes": x.get("NumVotes", 0)}
            for x in d.get("results", [])}


def main():
    global OUT_NAME
    a = sys.argv[1:]
    while a:
        flag, val = a[0], (a[1] if len(a) > 1 else "")
        if flag == "--stacks":
            for label, roots in json.load(open(val, encoding="utf-8")).items():
                STACKS[label] = [tuple(r) for r in roots]
            a = a[2:]
        elif flag == "--out":
            OUT_NAME = val
            a = a[2:]
        else:
            a = a[1:]

    pkgs = {}
    db_paths = []
    for repo, rel in REPOS:
        dest = os.path.join(CACHE, os.path.basename(rel))
        if not os.path.exists(dest):
            fetch(f"{MIRRORS[0]}/{rel}", dest)
        db_paths.append(dest)
        p = load_db(dest, repo)
        print(f"  {repo}: {len(p)} packages")
        pkgs.update(p)

    providers = defaultdict(list)
    for name, p in pkgs.items():
        providers[name].append(name)
        for prov in p["provides"]:
            providers[prov.split("=")[0]].append(name)

    guesses = []
    ext_hits = defaultdict(set)
    parents = {}          # child -> (parent, dep token), per stack, cleared each stack

    def add_dep(base, seen, unresolved, stack, parent):
        """Resolve ONE dependency token to a package name and return it for the queue.
        Must NOT add to `seen` — the queue's own `if n in seen: continue` guard would then
        skip expanding this package's dependencies and truncate the closure at depth 1."""
        def note(chosen):
            parents.setdefault(chosen, (parent, base))
            return [] if chosen in seen else [chosen]

        if base in EXTERNAL_VIRTUALS:
            ext_hits[base].add(stack)
            return []
        if base in pkgs:
            return note(base)
        if base == "xdg-desktop-portal-impl":
            owner = next((c for c in PORTAL_PREF if c in stack), None)
            pick = PORTAL_PREF.get(owner)
            if pick and pick in pkgs:
                guesses.append({"stack": stack, "dep": base, "chose": pick,
                                "candidates": sorted(set(providers.get(base, []))),
                                "rule": "portal follows compositor"})
                return note(pick)
        cands = sorted(set(providers.get(base, [])))
        # a hardware driver package must never satisfy a generic soname/virtual
        cands = [c for c in cands if not DRIVER_RE.match(c)]
        # arch sanity: a 64-bit package's soname dep is never satisfied by a lib32-* package.
        # Measured: waybar's `libgtk-3.so` resolved to lib32-gtk3 -> lib32-mesa ->
        # lib32-llvm-libs (+168 MB of 32-bit llvm in a 64-bit bar's closure).
        if not parent.startswith("lib32-"):
            arch_ok = [c for c in cands if not c.startswith("lib32-")]
            if arch_ok:
                cands = arch_ok
        if not cands:
            unresolved.add(base)
            return []
        in_closure = [c for c in cands if c in seen]
        pick = in_closure[0] if in_closure else min(cands, key=lambda c: (len(pkgs[c]["depends"]), c))
        if len(cands) > 1:
            guesses.append({"stack": stack, "dep": base, "chose": pick, "candidates": cands})
        return note(pick)

    def resolve(root, seen, unresolved, stack):
        q = [root]
        while q:
            n = q.pop()
            if n in seen:
                continue
            p = pkgs.get(n)
            if p is None:
                unresolved.add(n)
                continue
            seen.add(n)
            for d in p["depends"]:
                q.extend(add_dep(re.split(r"[<>=]", d)[0].strip(), seen, unresolved, stack, n))

    result = {}
    for label, roots in STACKS.items():
        seen, unresolved = set(), set()
        parents.clear()
        for k, n in roots:
            if k == "repo":
                resolve(n, seen, unresolved, label)
        result[label] = {"seen": seen, "unresolved": unresolved,
                         "aur_roots": [n for k, n in roots if k == "aur"],
                         "parents": dict(parents)}

    info = aur_rpc(sorted({a for r in result.values() for a in r["aur_roots"]}))
    for label, r in result.items():
        for a in r["aur_roots"]:
            for d in info.get(a, {}).get("depends", []):
                for x in add_dep(re.split(r"[<>=]", d)[0].strip(), r["seen"], r["unresolved"], label, a):
                    resolve(x, r["seen"], r["unresolved"], label)

    inter = None
    for r in result.values():
        inter = set(r["seen"]) if inter is None else (inter & r["seen"])
    inter = inter or set()

    rows = []
    for label in STACKS:
        r = result[label]
        seen = r["seen"]
        marg_set = seen - inter
        heaviest = sorted(((pkgs[n]["isize"], n, pkgs[n]["desc"]) for n in marg_set), reverse=True)[:8]
        rows.append({
            "stack": label, "pkgs": len(seen),
            "installed_MB": round(sum(pkgs[n]["isize"] for n in seen) / 1048576, 1),
            "marginal_pkgs": len(marg_set),
            "marginal_MB": round(sum(pkgs[n]["isize"] for n in marg_set) / 1048576, 1),
            "aur_roots": r["aur_roots"],
            "aur_versions": {a: info.get(a, {}).get("version") for a in r["aur_roots"]},
            "aur_unresolved": sorted(r["unresolved"]),
            "heaviest_marginal": [{"MB": round(s / 1048576, 1), "pkg": n, "desc": d}
                                  for s, n, d in heaviest],
        })
    rows.sort(key=lambda x: x["marginal_MB"])

    vintage = db_vintage(db_paths)
    vintage["packages"] = len(pkgs)
    vintage["repos"] = {repo: len(load_db(os.path.join(CACHE, os.path.basename(rel)), repo))
                        for repo, rel in REPOS}

    json.dump({"rows": rows, "shared_floor_pkgs": len(inter),
               "shared_floor_MB": round(sum(pkgs[n]["isize"] for n in inter) / 1048576, 1),
               "external_virtuals_hit": {k: sorted(v) for k, v in ext_hits.items()},
               "parents": {k: v["parents"] for k, v in result.items()},
               "db_vintage": vintage,
               "detail": {k: sorted(v["seen"]) for k, v in result.items()}},
              open(os.path.join(OUTDIR, OUT_NAME + ".json"), "w", encoding="utf-8", newline="\n"), indent=1)
    json.dump(guesses, open(os.path.join(OUTDIR, OUT_NAME + "-guesses.json"), "w", encoding="utf-8", newline="\n"), indent=1)

    with open(os.path.join(OUTDIR, OUT_NAME + ".tsv"), "w", encoding="utf-8", newline="\n") as f:
        f.write("stack\tpkgs\tinstalled_MB\tmarginal_pkgs\tmarginal_MB\taur_roots\taur_unresolved\n")
        for r in rows:
            f.write(f"{r['stack']}\t{r['pkgs']}\t{r['installed_MB']}\t{r['marginal_pkgs']}\t"
                    f"{r['marginal_MB']}\t{';'.join(r['aur_roots'])}\t{';'.join(r['aur_unresolved'])}\n")

    print(f"\nshared floor (all stacks): {len(inter)} pkgs, "
          f"{sum(pkgs[n]['isize'] for n in inter)/1048576:.0f} MB")
    print("external virtuals skipped:", {k: len(v) for k, v in ext_hits.items()})
    print(f"provider guesses logged: {len(guesses)}\n")
    print(f"{'stack':<29}{'pkgs':>5}{'instMB':>8}{'margPkgs':>10}{'margMB':>8}  aur / unresolved")
    print("-" * 114)
    for r in rows:
        extra = ",".join(r["aur_roots"])
        if r["aur_unresolved"]:
            extra += "  UNRESOLVED:" + ",".join(r["aur_unresolved"])
        print(f"{r['stack']:<29}{r['pkgs']:>5}{r['installed_MB']:>8}{r['marginal_pkgs']:>10}"
              f"{r['marginal_MB']:>8}  {extra}")
    print("\nheaviest marginal packages per stack:")
    for r in rows:
        print(f"  {r['stack']}: " + ", ".join(f"{h['pkg']}({h['MB']})" for h in r["heaviest_marginal"][:6]))
    print(f"\nwritten: {OUT_NAME}.json, {OUT_NAME}.tsv, {OUT_NAME}-guesses.json")


main()

# Method

The goal is a number you can argue with: for a given desktop stack, how many packages does it
add to a bare Arch system, how many megabytes do they occupy installed, and which package is
responsible for each one that surprises you.

## Sources

| what | where | used for |
|---|---|---|
| Arch `core`, `extra`, `multilib` databases | official mirrors, `*.db` tarballs | names, versions, `DEPENDS`, `PROVIDES`, installed size |
| AUR RPC | `https://aur.archlinux.org/rpc/` | version, votes and declared dependencies for AUR packages |
| GitHub REST API | via `gh` CLI | stars, license, language, last push, commit counts, contributors, open issues, releases |
| the audited projects' own files | their repositories | declared package lists, manifests, install scripts |

The Arch databases are downloaded once into `data/db/` (gitignored — third-party data that goes
stale) and all resolution then happens offline and deterministically.

## What the numbers mean

**Installed size** is the sum of the `ISIZE` field of every package in the closure, as declared
by the repository database. It is uncompressed on-disk size of the package payload. It excludes
the pacman cache, configuration, and anything the software generates at runtime (shell caches,
font caches, wallpapers you download later).

**Closure** is the transitive set: the stack's roots, everything they declare, and everything
those declare, resolved to exhaustion. A package's own declared size is a poor guide to its
cost — `waybar` is 2.2 MB and pulls a gigabyte of closure, `gtk4` is 52.1 MB and does the same.

**Shared floor** is the intersection of every stack measured. In the nine-stack race it is
127 packages / 592 MB: `glibc`, `systemd`, `python`, `perl`, `git` and other things a working
Arch system has regardless of desktop. The **marginal** column is the closure minus that floor,
i.e. what the desktop choice itself adds. Both numbers are reported because both are true and
they answer different questions: *how much will this add to my system* (marginal) versus *what
does a from-scratch build of this stack require* (total).

**Point in time.** Every figure is tied to the database snapshot it was measured against.

## Resolver rules

Implemented in [`tools/pkg-closure-v2.py`](../tools/pkg-closure-v2.py).

1. **Resolve to exhaustion, breadth-first.** Declared dependencies are not the cost; the closure
   is. See defect 2 for what happens when this is done wrong.
2. **Never guess a virtual that the machine satisfies.** `opengl-driver`, `vulkan-driver`,
   `lib32-opengl-driver`, `lib32-vulkan-driver`, `ttf-font`, `ttf-font-nerd`, `sh`, `awk` and
   `wayland-compositor` are recorded as skipped and left out. GPU drivers are a property of the
   hardware, not of the desktop, and resolving them by guess is what produced defect 1.
3. **A hardware driver must never satisfy a generic soname.** `nvidia-utils`, `nvidia-open*`,
   `rocm-*`, `opencl-*` and vendor Vulkan drivers are filtered out of candidate sets for
   generic dependencies, so a 948 MB proprietary driver cannot be chosen to satisfy
   `libEGL.so` when `mesa` will do.
4. **Architecture sanity: no 32-bit packages for 64-bit dependencies.** If a dependency is a
   soname of a 64-bit package, a `lib32-*` provider is not a valid answer, whatever its
   dependency count. See defect 3.
5. **`xdg-desktop-portal-impl` is chosen by compositor, not by size.** The virtual has four real
   providers; picking the smallest pulls a Qt/KDE portal into stacks that contain no Qt
   (measured: `qt6-base` appearing in a `niri` + `noctalia` closure). The portal follows the
   compositor, so it is selected by name.
6. **Every multi-provider choice is logged** to `data/*-guesses.json` with its candidates and
   the rule used. A wrong guess is then visible in a file rather than hidden inside a total.
7. **Every closure member reached through the official repositories must be traceable to a root.**
   The resolver records a parent edge — `(child, parent, exact dependency token)` — for each
   package it adds, and `tools/why-chain.py` walks those edges back to the stack root. Roots
   themselves have no parent edge, so a stack with two official roots reports two untraced
   members. **Known gap:** dependencies reached through an **AUR** package's declared dependencies
   are counted but no parent edge is recorded for them, so AUR-rooted stacks show a large untraced
   set (208 of 393 members for `hyprland` + `caelestia-shell`, 37 of 203 for `mangowm-git`, 21 of
   172 for `river` + `yambar` + `wallust`). A package that cannot be traced in a stack whose roots
   are all official *is* a resolver defect; `tools/why-chain.py` prints the traced/total counts per
   stack so the two cases are distinguishable.

## Resolver defects found by measurement

These are documented rather than quietly fixed, because they are the reason to trust the current
output. Each was caught by a result that was implausible, not by reasoning.

### 1. A virtual resolved by "fewest dependencies" picked the 948 MB GPU driver

`libglvnd` declares `libxext`, `mesa` and the virtual `opengl-driver`. That virtual is provided
by both `mesa` (18 dependencies) and `nvidia-utils` (5). The tie-break chose the NVIDIA driver
for **every** stack, and asymmetrically — `sway` also pulled `lib32-nvidia-utils`, +562 MB, so
the "lightest" compositor appeared heaviest.

Symptom: `sway` + `waybar` + `wallust` (378 packages, 3.0 GB) measuring *heavier* than
`hyprland` + `noctalia` + `matugen` (270 packages, 2.1 GB). Fix: rules 2 and 3.

### 2. A closure silently truncated at depth one

`add_dep` added a resolved package to the `seen` set *and* queued it. When the queue popped it,
the `if n in seen: continue` guard skipped it — so no package was ever expanded, and every
closure was exactly one level deep.

Symptom: `niri` + `dankmaterialshell` resolving to 18 packages with no Qt6 anywhere in it,
which is impossible for a QML shell. Fix: a resolved dependency must be queued, never marked
seen; the queue marks it when it is expanded.

### 3. 168 MB of 32-bit LLVM in a 64-bit bar

`waybar` declares the soname `libgtk-3.so=0-64`. The candidate set included `lib32-gtk3`, which
provides that soname name; the size tie-break picked it, and the closure then grew
`lib32-gtk3` → `lib32-mesa` → `lib32-llvm-libs` (+168 MB) for a bar that will never load a
32-bit library.

Symptom: 32-bit packages appearing in stacks that contain no 32-bit anything. Fix: rule 4.

A fourth, smaller class of defect is worth naming: **unresolved names were silently dropped** in
early versions. They are now reported per stack in the `aur_unresolved` column of the TSVs, so a
gap in the data is visible in the table rather than reducing a total quietly.

## Limits

Stated plainly, because these numbers are easy to over-read.

* **No runtime measurement.** Nothing here says how many megabytes of RAM a shell uses, how it
  behaves under load, or how it feels. Install cost is one axis; it is not the interesting one
  for everyone.
* **Not a security audit.** No source was read for vulnerabilities, no package signature policy
  was evaluated, no AUR PKGBUILD was audited beyond the metadata cited.
* **Figures are for a bare base system.** They answer "what does this add to a minimal Arch
  install". On a system that already has GTK4, a GTK4 shell is far cheaper than the table
  implies — which is exactly why the two-component case in the README is measured separately.
* **GPU and hardware drivers are excluded** by rule 2. A from-scratch install of any of these
  stacks also needs a graphics driver, and its size depends entirely on the hardware.
* **AUR closures are approximate.** Official packages are resolved from the full database,
  offline and exactly. AUR packages have no local database: their declared dependencies come
  from the RPC and are resolved the same way, but an AUR package's *own* size is unknown (no
  installed size is published), AUR packages that depend on other AUR packages beyond the RPC's
  answer are listed as unresolved rather than guessed, and **no parent chain is recorded for
  dependencies reached through an AUR package** — so a stack with AUR roots is larger than the
  table shows and less auditable than an official-only stack. Where a stack has AUR components,
  its true total is *higher* than the table shows, and the unresolved names are printed.
* **`xdg-desktop-portal-impl` is a rule, not a measurement** (rule 5). A user who deliberately
  installs a different portal provider will move their own numbers slightly.
* **Provider guesses happen** for multi-provider sonames. They are logged (rule 6) so they can
  be audited; they are not each hand-checked.
* **Star counts and commit velocity are point-in-time** and move quickly. They are reported as
  signals with the query that produced them, not as verdicts on their own.

## Reproducing

```bash
# provenance facts (needs gh, authenticated)
./tools/recon-repos.sh data/repos.tsv

# the nine-stack race — downloads data/db/*.db on first run, then works offline
python3 tools/pkg-closure-v2.py

# cost a build found in the wild from its own package list
python3 tools/classify-stack.py "build-name" path/to/packages.txt --out data/my-stacks.json
python3 tools/pkg-closure-v2.py --stacks data/my-stacks.json --out my-build

# prove any single claim
python3 tools/why-chain.py "sway+waybar+wallust" gpsd python    # chain with exact tokens
python3 tools/why.py python gpsd                                # raw DEPENDS lines from the db
python3 tools/closure-inspect.py                                # what a stack pulls that it shouldn't
```

`--stacks <file.json>` merges stack definitions into the built-in nine; `--out <name>` names the
output set (`<name>.json`, `<name>.tsv`, `<name>-guesses.json`). Stack file format:

```json
{
  "my stack": [["repo", "hyprland"], ["aur", "wallust"]]
}
```

`repo` roots are resolved from the official databases; `aur` roots are resolved from the AUR RPC
and their declared dependencies.

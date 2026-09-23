# Plugins — the feature class that has no package

Everything in [`features.md`](features.md) is costed as a package. Shake-to-find is not a
package, and neither is the build's other plugin. Both are compiled by `hyprpm` from a GitHub
repository on first run, so no amount of pacman archaeology will find them.

This file exists so the omission is documented rather than invisible: a reader who searches the
42 slots for "shake to find" finds nothing, and needs to be told why.

## What impasto actually does

From its own setup script, verbatim:

```
say 'building shake to find and glass: your password, once'
act hyprpm update
plugin dynamic-cursors https://github.com/virtcode/hypr-dynamic-cursors
plugin hyprglass       https://github.com/hyprnux/hyprglass
act hyprpm reload
```

| name in the build | repository | what it is | status |
|---|---|---|---|
| shake to find | [`VirtCode/hypr-dynamic-cursors`](https://github.com/VirtCode/hypr-dynamic-cursors) | cursor effects for Hyprland; **shake to find** magnifies the pointer when you shake it | 739★, MIT, last push 2026-09-04 |
| glass | [`hyprnux/hyprglass`](https://github.com/hyprnux/hyprglass) | blur, lens, diffraction and refraction on windows | 286★, BSD-3-Clause, last push 2026-09-18 |

Neither is packaged — the AUR has nothing under `hypr-dynamic-cursors`, `hyprglass`, or
`*-git`, and a keyword search returns nothing for either name. They are build-from-source only.

## What it costs

The plugin contributes **no packages**. `hyprpm` does: it is an official package
(`extra` 0.56.2-3, 0.5 MB) and it needs a compiler toolchain before it can build anything.

| stack | packages | total | marginal |
|---|---|---|---|
| bare Hyprland + hyprpm + toolchain + `hyprcursor` | 212 | 1,080.7 MB | 79 pkgs / 489.4 MB |
| hyprpm + `base-devel` + cmake + meson + cpio + git | 273 | 1,675.5 MB | 140 pkgs / 1,084.2 MB |

The second stack looks heavier because it starts from nothing: `gcc` (220.9 MB) and `cmake`
(101.4 MB) dominate it.

**Against a build that already carries the toolchain, the feature is free.** `hyprpm` declares
seven dependencies — `cmake`, `cpio`, `glaze`, `hyprland`, `hyprland-protocols`,
`hyprwayland-scanner`, `meson` — and all seven are already inside impasto's own closure, as is
`hyprpm` itself. Adding shake-to-find to that build adds **zero packages**.

That is the general rule for plugins and it cuts both ways: they cost nothing to add to a build
that already compiles its own software, and they cost a full toolchain on a build that does not.

## The vector cursor it needs

Shake-to-find magnifies the pointer, so the cursor has to be a vector — a bitmap cursor cannot
scale up cleanly. The build fetches one:

```
git clone --depth=1 https://github.com/javigomezo/bibata-modern-classic-hyprcursor
```

That repository has **2 stars and was last pushed 2024-09-14** — the stalest link in this
feature by roughly two years. A packaged alternative exists and is healthier:
`bibata-cursor-git` in the AUR ("Bibata Cursor Themes, **including hyprcursor** and Xcursor",
9 Bibata variants listed).

Cursor themes add **no dependency tree** — measured: adding the packaged cursor to the build
chain above changed the closure by 0 packages. A theme is files, not dependencies, which is also
why a single-package AUR closure should not be read as an unmeasurable one when the package is a
theme.

## Fragility worth knowing before adopting

`hyprpm` keys its compiled headers on Hyprland's commit hash. When Hyprland is rebuilt — even to
the same version against new libraries — the old headers stay, and every plugin is refused while
`hyprpm reload` still reports success; only `hyprctl plugin list` shows the failure. The build
handles this by forcing an update when the list comes back empty.

Both plugins are **Hyprland-only** by construction: choosing shake-to-find fixes the compositor
slot to Hyprland, which is otherwise the cheapest decision in the audit. This is the one place
where a preference in the aesthetic layer propagates into the compositor choice.

## Reproduce

```bash
# 1. probe the names — a plugin that has no package must be proven absent, not assumed
python tools/probe-names.py data/probe-shake-to-find.txt data/shake-to-find.tsv

# 2. cost what the feature does pull in
python tools/pkg-closure-v2.py --stacks data/shake-to-find-stacks.json --out shake
```

`probe-names.py` reports `NONE` for both plugin names. That is a statement about the names, not
proof of absence — search the AUR by keyword and check the repository before concluding
anything, which is how the two upstream repositories above were confirmed.

## Attribution

`hypr-dynamic-cursors` is MIT, `hyprglass` is BSD-3-Clause, and `bibata-modern-classic-hyprcursor`
is GPL-3.0 — all upstream, none reviewed or endorsed by their authors here. Measured facts about
impasto's behaviour come from its own published setup script; see [`CREDITS.md`](../CREDITS.md).

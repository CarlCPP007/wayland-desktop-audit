# Ricelin — audit

**Source:** [github.com/Gakuseei/Ricelin](https://github.com/Gakuseei/Ricelin) · **owner:** Gakuseei · **licence:** MIT (repo `LICENSE`) · **HEAD read:** `f00e041`, pushed 2026-09-18 · 312★, 23 forks, 201 files, 59 MB

Ricelin is a **personal Hyprland rice built on CachyOS**: the whole shell is hand-written [Quickshell](https://quickshell.org) QML (110 files), themed "warm vermilion" with [matugen](https://github.com/InioX/matugen), on Hyprland, Ghostty, fish and JetBrains Mono Nerd. A companion repo by the same owner, [rishot](https://github.com/Gakuseei/rishot), provides its screenshot tool.

It is the closest thing in this repository to a like-for-like competitor to [impasto](audit-impasto.md): both are **whole desktops**, and both target a Hyprland session. Ricelin is the smaller and more opinionated of the two — no package manager, no AUR bootstrap of its own, and a shell written from scratch rather than assembled from existing bars.

| | Ricelin | impasto |
|---|---|---|
| type | whole desktop | whole desktop |
| compositor | Hyprland, **configured in Lua** | Hyprland, configured in Hyprland's own syntax |
| shell | hand-written Quickshell, 110 QML files | Quickshell + a wide app set |
| theming | matugen from the wallpaper | matugen from the wallpaper |
| native packages | 38 (core) / 44 (core + full) | 85 mandatory |
| AUR packages | 4 (core) | 0 |
| declared licence | MIT | GPL-3.0 |

## What its installer actually does

`install.sh` is a bootstrap: it prints the plan, fetches the repositories' own keyrings, then hands over to a Python wizard in `installer/` (`distro.py`, `pkg.py`, `fallbacks.py`, `aur.py`, `state.py`, `ui.py`, `grub_theme.py`, `sddm_theme.py`, `tui.py`, `bin/ricelin.py`). It supports five package families, an `aur_choice` of `helper`/`manual`/`none`, and flags `--quickstart`, `--full`, `--sddm`, `--no-deps`, `--dry-run`, `--uninstall`. Replaced configs are backed up, and an in-app updater (`ricelin`) re-pulls the repo.

Two design decisions are worth crediting because they are what make the thing auditable at all:

* **The package manifest is data, not shell.** `installer/packages.json` declares every dependency once, with per-distro native names, AUR flags and fallback ladders. That is the only reason the cost below can be measured rather than guessed.
* **Hardware specifics are neutralised upstream.** Monitor layout ships as `monitors.lua.example` rather than a live config, so a third party can install it without inheriting someone else's screens.

## Verified by running it

Nothing here is inferred from the README.

| check | result |
|---|---|
| `distro.py` own selftest | **pass** — family detection, native name mapping, resolve, plan |
| `fallbacks.py` own selftest | **pass** — 7 handlers, every one returns steps |
| `pkg.py` own selftest | **fails on a non-Arch host** — three asserts hard-require `pacman`. Fine on the target, but the module's "cheap to unit-test anywhere" claim holds only on Arch. |
| CachyOS detection | `ID=cachyos`, `ID_LIKE=arch` → family **`arch`** |
| plan for `arch`, core group | 38 native + 4 AUR + 1 `curl` fallback |
| plan for `arch`, core + full | 44 native + 4 AUR + 1 fallback |

The 4 AUR roots are `bibata-cursor-theme-bin`, `dotool`, `gpu-screen-recorder`, `mpvpaper`; the fallback is `rishot`, fetched by the repo's own script because no distribution packages it. Every one of the 44 native names was probed against the official repositories and confirmed resident (see `data/ricelin-availability.tsv`).

## What it costs

Measured as a full dependency closure against the Arch databases the rest of this repository uses — 15,463 packages, `core.db` sha256 `c76bc4cc4311`, `extra.db` `f3b7154ebfee`, `multilib.db` `54298ee0d6bd`, all fetched 2026-09-23 07:55:50. Closures include dependencies, so they are comparable with every other number here.

| stack | packages | installed | what it is |
|---|---|---|---|
| **Ricelin core** | **527** | **2,878.5 MB** | the 38-package core plus its closure |
| Ricelin core + full profile | 593 | 3,282.3 MB | the six daily apps (Dolphin, KeePassXC, Zathura, imv, rnote, mupdf backend) add **66 pkgs / 403.8 MB** |
| Ricelin AUR set | 259 | 1,040.5 MB | the four AUR roots' closures, before build time |
| Ricelin extras (Brave theme) | 177 | 777.6 MB | `brave-bin` alone |

For scale, on the same databases and the same measurement: `hyprland+noctalia+matugen` is **234 pkgs / 1,053.6 MB**, `hyprland+dms+matugen` **233 / 1,168.2**, `hyprland+caelestia+matugen` **393 / 1,839.5**.

**Ricelin's core is 2.7× the lightest full shell stack in the stack race.** That is not a flaw in the shell — it is what the rice chooses to ship alongside it, and the heaviest single rows say exactly what:

| marginal size | package | what it is |
|---|---|---|
| 298.8 MB | `noto-fonts-cjk` | Google Noto CJK fonts |
| 231.9 MB | `ttf-jetbrains-mono-nerd` | patched JetBrains Mono, the rice's icon font |
| 121.4 MB | `qt6-declarative` | QML runtime — required by the shell itself |
| 111.5 MB | `papirus-icon-theme` | Papirus icons |
| 106.8 MB | `noto-fonts` | Google Noto TTF |
| 82.8 MB | `breeze-icons` | pulled in by `kde-cli-tools` |
| 73.6 MB | `python` | the installer's own runtime |
| 66.5 MB | `qt6-base` | Qt6 base |

Two clusters account for roughly **1.0 GB of the 2.88 GB**: fonts (749 MB across the four font rows) and KDE/Qt command-line tooling (`kde-cli-tools` + `kdialog` + `breeze-icons` + Qt). Neither is the shell's visual identity. `noto-fonts-cjk` alone is 10% of the install and only matters if CJK text is on screen; `kde-cli-tools`/`kdialog` exist so shell QML can open a file dialog, which is a whole KDE icon stack and a Qt5 dress for a file picker.

## Findings

**1. `gpu-screen-recorder` is no longer an AUR package, and the manifest still says it is.** `installer/packages.json` carries `"aur": true` for it with an AUR-then-Flatpak fallback ladder, but it now ships in official `extra` (**6.1.2-1**). Two independent checks agree: the AUR RPC returns no version for the name (it is not there any more), and the official probe finds it. The practical effect is mild — the AUR helper installs it from the official repository anyway — but it makes the manifest's own claims wrong, and it keeps a package on the AUR path that does not need a helper.

**2. The `swww` note is half-stale: the mechanism holds, the wording no longer does.** The README says that on CachyOS `pacman -S swww` resolves to `awww` because *"awww … declares provides: swww and replaces: swww, while vanilla Arch installs native swww."* Verified from the databases: **no package named `swww` exists**, and `awww` does declare both `PROVIDES` and `REPLACES` for it — so the command works. But "vanilla Arch installs native `swww`" is no longer true anywhere; the Provides route is now the only route, on every Arch derivative. Anyone debugging a fresh CachyOS install from that sentence will look for the wrong package name.

**3. The 4 AUR roots make an AUR helper mandatory.** There is no core-only install path that avoids building from the AUR, because `dotool` (input synthesis for the shell's keybindings), `bibata-cursor-theme-bin` (cursors), `mpvpaper` (video wallpaper) and `gpu-screen-recorder` are all AUR roots in the core group. The installer handles this correctly with `aur_choice`, including a `none` mode that reroutes to fallbacks — but "core" here still means "an AUR helper gets bootstrapped".

**4. A resolver defect in this repository, found by costing Ricelin.** A stack root that is not a package name but *is* provided by exactly one package (`swww` → `awww`) was being reported as unresolved, which understates a closure. `tools/pkg-closure-v2.py` now resolves such roots to their single provider and records the substitution in `provider_substitutions` rather than silently picking one. Ambiguous providers are still left unresolved, on purpose: that is a choice for a human, not a tool. The fix moved Ricelin's core from 526/2,867.9 to **527/2,878.5** and changed no other stack's numbers.

## Credit

Ricelin is **Gakuseei's** work under MIT — the shell, the installer, the theme system and the rice as a whole. It is not redistributed here and nothing in this repository modifies it. Its own `CREDITS.md` attributes the SDDM theme, the wallpapers and the upstream projects it builds on; those credits are the ones that matter and should be read there. This page is an independent measurement of something the author published, not a contribution to it.

## Reproduce

```bash
git clone --depth=1 https://github.com/Gakuseei/Ricelin.git
cd Ricelin
# 1. would it detect your distribution, and what would it install?
python3 installer/distro.py            # own selftest
python3 -c "import sys; sys.path.insert(0,'installer'); import distro as D; \
  print(D.plan(D.load_manifest(), 'arch', groups=('core',), aur_choice='helper'))"

# 2. the cost and the name check, using this repository's tools
cd <this repo>
python tools/pkg-closure-v2.py --stacks data/ricelin-stacks.json --out ricelin
python tools/probe-names.py data/probe-ricelin.txt data/ricelin-availability.tsv
```

`tools/pkg-closure-v2.py` re-downloads the Arch databases unless `data/db/` is populated, so the numbers above are only reproducible while Arch's mirrors still serve that snapshot — every generated artifact carries the `db_vintage` it was measured against for exactly this reason.

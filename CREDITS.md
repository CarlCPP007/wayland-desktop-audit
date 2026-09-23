# Credits and attribution

This repository analyses other people's work. None of it is mine, and none of the projects
below reviewed, approved or endorsed this audit. They are credited here because the audit is
built on facts read from their public repositories, and because a measurement is only useful
if you can go and check it.

No upstream source code is vendored in this repository. Where an upstream file informed a
number, it is referenced by URL (and line number where it matters) rather than copied.

## Audited builds

### impasto

* **Owner:** [andreumassanet](https://github.com/andreumassanet)
* **Repository:** https://github.com/andreumassanet/impasto
* **License:** GPL-3.0
* **What was used:** the declared package lists (`packages/pacman.txt`, `packages/aur.txt`) were
  fetched and parsed programmatically — never retyped — and the install script (`setup`) was
  read to document its stages, its flags and its `/etc` payload. The `impasto` row in
  `data/builds.tsv` is the closure of the packages that list names.
* **Where:** [docs/audit-impasto.md](docs/audit-impasto.md),
  [docs/install-impasto-on-arch.md](docs/install-impasto-on-arch.md)

### wayle

* **Owner:** [wayle-rs](https://github.com/wayle-rs) and its 25 contributors
* **Repository:** https://github.com/wayle-rs/wayle
* **License:** MIT
* **What was used:** `Cargo.toml` (to establish the system-level dependency set) and the AUR
  package metadata for `wayle-bin` (version, votes). Closure measured from the Arch databases.
* **Where:** [docs/audit-wayle.md](docs/audit-wayle.md)

### rust-dock

* **Owner:** [rhythmcreative](https://github.com/rhythmcreative)
* **Repository:** https://github.com/rhythmcreative/rust-dock
* **License:** the repository's `LICENSE` file is GPL-3.0 while `Cargo.toml` declares
  `license = "MIT"`. This conflict is noted as a finding, not resolved here — the author is the
  only one who can settle it.
* **What was used:** `Cargo.toml`, the installer script, and the README's stated runtime
  dependencies. Closure measured from the Arch databases.
* **Where:** [docs/audit-rust-dock.md](docs/audit-rust-dock.md)

## Components measured in the stack race

The audit costs other people's packages, so they belong here too. Compositors, shells, bars and
theme engines referenced by name in the tables. Licenses below were read from each project's
repository metadata on 2026-09-23; where a project publishes no machine-readable license the
entry says so rather than guessing.

* **Compositors:** [Hyprland](https://github.com/hyprwm/Hyprland) (BSD-3-Clause) ·
  [niri](https://github.com/niri-wm/niri) (GPL-3.0) · [Sway](https://github.com/swaywm/sway) (MIT) ·
  [labwc](https://github.com/labwc/labwc) (GPL-2.0) · [River](https://github.com/riverwm/river) (no
  detected license file) · [mango](https://github.com/mangowm/mango) (license not machine-readable) ·
  [Wayfire](https://github.com/WayfireWM/wayfire) (MIT)
* **Shells, bars and toolkits:** [Quickshell](https://github.com/quickshell-mirror/quickshell) (LGPL-3.0) ·
  [Noctalia](https://github.com/noctalia-dev/noctalia) (MIT) ·
  [DankMaterialShell](https://github.com/AvengeMedia/DankMaterialShell) (MIT) ·
  [Waybar](https://github.com/Alexays/Waybar) (MIT) ·
  [yambar](https://codeberg.org/dnkl/yambar) (see upstream) ·
  [Caelestia shell](https://github.com/caelestia-dots/shell) (GPL-3.0) ·
  [AGS / Astal](https://github.com/Aylur/ags) (GPL-3.0)
* **Theme engines:** [matugen](https://github.com/InioX/matugen) (GPL-2.0) ·
  [wallust](https://codeberg.org/explosion-mental/wallust) (see upstream) ·
  [pywal](https://github.com/dylanaraps/pywal) (MIT, archived)

If a license above is wrong it is wrong on this page only, and correcting it is welcome.

## Data sources

* **Arch Linux package databases** — `core`, `extra`, `multilib`, fetched from the official
  mirrors (`geo.mirror.pkgbuild.com`). Package names, versions, declared dependencies,
  provided sonames and installed sizes all come from here.
* **Arch User Repository RPC** (https://aur.archlinux.org/rpc/) — for packages that live in the
  AUR, used for version, vote count and dependencies.
* **GitHub REST API** — stars, license, language, last push, commit counts, contributors,
  open issues and releases, queried via the `gh` CLI. Point-in-time by nature.

## Tools this audit depends on

Standard library only, plus `gh` for the provenance pass. No vendored third-party code.

## A note on fairness

This audit measures install cost and reads maintenance signals from public APIs. It does not
read the audited projects' source for bugs, does not test them at runtime, and makes no claim
about how they feel to use — which is, for a desktop, most of what matters. A small project with
two commits in ninety days may simply be finished rather than abandoned; the tier rubric says
what the numbers say and no more.

Corrections from authors and users are genuinely welcome — see the README.

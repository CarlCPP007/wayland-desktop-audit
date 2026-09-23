# Audit: wayle

**Repository:** https://github.com/wayle-rs/wayle · **Owner:** [wayle-rs](https://github.com/wayle-rs) ·
**License:** MIT · **Verdict:** **Watch**

> Figures measured 2026-09-23. See [method.md](method.md) for what the numbers mean and exclude.

## What it is

A desktop shell written in Rust on GTK4 + Relm4: bar, notifications, on-screen display, wallpaper
and device management, with a settings GUI and a CLI. It is compositor-agnostic — it targets
Hyprland, Niri and Mango rather than binding to one compositor — which is unusual in this space
and is the reason it survives a compositor change.

| | |
|---|---|
| implementation | Rust, GTK4 + Relm4 |
| stars | 934 |
| last commit | 2026-07-25 |
| commits / last 90 days | **3** |
| contributors | 25 |
| open issues | **166** |
| latest release | v0.7.0 (2026-07-25) |
| packaging | AUR `wayle-bin` 0.7.0-1 — **2 votes**; `wayle-git` is stale at `0.1.0.r0` |

## Measured install cost

| | |
|---|---|
| closure of `wayle-bin` | **226 packages** |
| installed size | **1,007.7 MB** |
| marginal over the shared floor | 99 packages / 415.3 MB |
| with a compositor (`hyprland` + `wayle`) | 269 packages / 1,113.7 MB |

The declared system dependencies are all ordinary Arch packages — `gtk4`, `gtk4-layer-shell`,
`gtksourceview5`, `libpulse`, `fftw`, `systemd-libs` — plus vendored SQLite and its own CAVA
sub-crate. Nothing exotic, nothing from the AUR except the shell itself.

**The GTK4 entry fee applies.** `wayle-bin` is a few megabytes; roughly a gigabyte of its closure
is the GTK4 stack, including the GTK3 that `gtk4` pulls in through `xdg-desktop-portal-gtk`
(see [findings.md](findings.md#1-gtk4-hard-depends-on-a-gtk3-portal-so-every-gtk4-app-drags-gtk3-in)).
On a system that already has GTK4, this collapses to the marginal figure.

## Two practical caveats

* **`wayle-bin` is an AUR binary package with two votes.** Votes are a weak proxy for anything,
  but a binary package published through the AUR is a supply chain you are choosing to trust.
  Building from source removes that trust question; it requires Rust 1.93.
* **`wayle-git` reports version `0.1.0.r0`** and does not track the project's current state.
  Do not use it to mean "the latest".

## Verdict: Watch

The engineering is sound and the choices are good: official-repository dependencies, a real CLI
and settings surface, compositor independence, MIT licensing, 25 contributors. What the numbers
do not support is *dependency* right now — 3 commits in 90 days against 166 open issues is a
maintenance signal that a user should not walk past, and the only packaged path is a two-vote AUR
binary.

This is not a claim that the project is abandoned. A shell can be feature-complete between
releases, and an issue backlog measures how many people are using something as much as it
measures neglect. The tier says what the signals say: revisit when commits resume or the package
lands in `extra`, and until then treat it as something to try rather than something to build on.

## Sources

* Repository facts: GitHub REST API (`repos/wayle-rs/wayle`, `/commits`, `/contributors`,
  `/releases`), queried 2026-09-23.
* AUR metadata for `wayle-bin` and `wayle-git`: AUR RPC, same date.
* Declared dependencies: the project's `Cargo.toml`.
* Closure: `data/builds.tsv`, `data/combos.tsv` and the corresponding JSON detail.
* Component licences and links: [CREDITS.md](../CREDITS.md).

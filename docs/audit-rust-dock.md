# Audit: rust-dock

**Repository:** https://github.com/rhythmcreative/rust-dock · **Owner:** [rhythmcreative](https://github.com/rhythmcreative) ·
**License:** conflict — see below · **Verdict:** **Adopt with conditions**

> Figures measured 2026-09-23. See [method.md](method.md) for what the numbers mean and exclude.

## What it is

A dock for Wayland compositors, written in Rust with GTK4. It is not packaged in the official
repositories and publishes no releases, so installing it means building it from source with the
project's installer.

| | |
|---|---|
| implementation | Rust, GTK4 + gtk4-layer-shell |
| stars | 13 |
| last commit | 2026-08-26 |
| commits / last 90 days | 2 |
| contributors | 1 |
| open issues | 0 |
| releases / tags | none |
| repository | 298 KB |

## Measured install cost

The dock itself is not in any repository, so what is costed here is the closure of its declared
runtime dependencies — `gtk4`, `gtk4-layer-shell`, `grim`:

| | |
|---|---|
| closure | **213 packages** |
| installed size | **979.1 MB** |
| marginal over the shared floor | 86 packages / 386.8 MB |
| **added beside an existing GTK4 shell** | **+1 package (`grim`), +0.0 MB** |

That last row is the interesting one, and it is measured rather than assumed: diffing the
package sets of `hyprland + wayle` and `hyprland + wayle + rust-dock` shows exactly one
additional package. GTK4 and `gtk4-layer-shell` are already paid for by the bar, so the dock's
marginal cost is `grim` (needed for live window previews) and nothing else.

From a bare base it costs the full GTK4 entry fee on its own — see
[findings.md](findings.md#1-gtk4-hard-depends-on-a-gtk3-portal-so-every-gtk4-app-drags-gtk3-in).

## Conditions

* **It is not in any repository.** Installing means a git clone and a source build, and keeping it
  updated means doing that again. There is no `pacman -Syu` path, and no release archive to
  verify against.
* **Its installer services several distributions, and bootstraps a tool from a third-party
  repository.** The install script is a `gum`-based wizard; on Debian and Fedora it adds Charm's
  third-party apt/yum repository to obtain `gum`. That is a durable change to your system's
  package sources, made by an installer for a dock. Audit the script or install the prerequisites
  yourself.
* **Its colour sync depends on pywal.** The README describes syncing with
  [pywal](https://github.com/dylanaraps/pywal), which is **archived** and has not seen a release
  since **3.3.0 on 2019-01-21** (168 open issues, last push 2024-01-27). The successor tools in
  this ecosystem are [matugen](https://github.com/InioX/matugen) and
  [wallust](https://codeberg.org/explosion-mental/wallust). A dock whose theming feeds on an
  archived colour tool is a follow-up fix waiting to happen — and it is a contained one, since the
  dock reads a generated colour file rather than embedding an engine.
* **It is a single-maintainer project with 13 stars and 2 commits in the last 90 days.** Set
  expectations accordingly: this is the tier where you are willing to own the code if the author
  moves on.
* **The license is stated twice and differently.** The repository's `LICENSE` file is GPL-3.0
  while `Cargo.toml` declares `license = "MIT"`. Only the author can settle which applies. Until
  then, treat redistribution as ambiguous — it does not affect building it for yourself.

## Verdict: Adopt with conditions

Worth it in exactly one configuration: alongside a GTK4 shell that already exists on the system,
where it costs one package, and with its colour sync repointed at a maintained theme engine. From
a bare base — 979 MB for a dock — it is not competitive with anything, and the installer's
third-party repository bootstrap should be read before it is run.

## Sources

* Repository facts: GitHub REST API (`repos/rhythmcreative/rust-dock`), 2026-09-23. No releases
  or tags exist; the API returns 404 for a latest release.
* License conflict: the repository's `LICENSE` file (as detected by the GitHub API) versus the
  `license` field in `Cargo.toml`, both read the same day.
* Declared runtime dependencies and the installer description: the project's `README.md`,
  `Cargo.toml` and install script.
* pywal status: GitHub REST API for `dylanaraps/pywal` — archived, latest release 3.3.0
  (2019-01-21).
* Closure: `data/builds.tsv` and `data/combos.json` (the package-set diff in
  [findings.md](findings.md#6-two-components-can-be-cheaper-together-than-apart)).
* Component licences and links: [CREDITS.md](../CREDITS.md).

# Audit: impasto

**Repository:** https://github.com/andreumassanet/impasto · **Owner:** [andreumassanet](https://github.com/andreumassanet) ·
**License:** GPL-3.0 · **Verdict:** **Adopt** (with conditions)

> Figures measured 2026-09-23. See [method.md](method.md) for what the numbers mean and exclude.

## What it is

A complete desktop: Hyprland configuration, a Quickshell-based shell, terminal and editor
configuration, file-manager settings, a login screen, theming, cursors and fonts — installed by a
single script from the repository. It is a full takeover of both `$HOME` and parts of `/`, not a
component you drop into an existing setup.

| | |
|---|---|
| implementation | QML on [Quickshell](../CREDITS.md) |
| stars | 220 |
| last commit | 2026-09-22 |
| commits / last 90 days | 100 (API page cap — actual may be higher) |
| contributors | 1 |
| open issues | 1 |
| latest release | v0.3.2 (2026-09-22) |
| repository | 426 tracked files, ~176 MB (mostly assets) |
| symlinks | none |
| executable files | 85 (including `setup` and 19 Quickshell helper scripts) |

## Measured install cost

| | |
|---|---|
| declared packages (`packages/pacman.txt`) | **85** |
| of those, in official repositories | **85 — zero AUR** |
| closure | **629 packages** |
| installed size | **3,863.8 MB** |
| marginal over the shared floor | 502 packages / 3,271.4 MB |
| AUR in the mandatory path | **none** (`packages/aur.txt` is declared optional) |

Where the 3.9 GB goes:

| package | installed | why it is in the closure |
|---|---|---|
| `noto-fonts-cjk` | 298.8 MB | CJK coverage, declared directly |
| `ttf-jetbrains-mono-nerd` | 231.9 MB | terminal/editor font, declared directly |
| `gcc` | 220.9 MB | via `base-devel`, needed to build the AUR helper and the Hyprland plugins |
| `qt6-declarative` | 121.4 MB | Quickshell's QML runtime |
| `papirus-icon-theme` | 111.5 MB | icon theme |
| `noto-fonts` | 106.8 MB | base font set |

That is ~850 MB of fonts and toolchain. It is a deliberate choice rather than bloat, but it is
what makes this a desktop-sized install instead of a shell-sized one.

The only AUR traffic in the whole install is bootstrapping a helper (`yay` or `paru`) if neither
is present. Nothing in the mandatory desktop depends on the AUR.

## Quality signals

Read from the repository's own files rather than inferred:

* **Every declared package carries its reason.** `packages/pacman.txt` annotates each of the 85
  entries with why it exists — the kind of comment (`dbus — dbus-monitor, which hears logind
  about to sleep`) that lets a user audit the list instead of trusting it.
* **Optional really is optional.** `packages/aur.txt` states that everything in it is optional,
  and the mandatory set resolves entirely from official repositories.
* **The install script is reversible and inspectable.** `./setup` offers `install`, `update`,
  `uninstall`, and per-subsystem commands (`packages`, `sync`, `system`, `plugins`, `defaults`,
  `cursors`, `spotify`, `vscodium`, `thunar`, `vesktop`, `face`, `files`, `check`), plus
  `--dry-run` which prints what would change and changes nothing. `./setup files list` shows
  installed files you have edited, and `uninstall` removes what you have not. Files that were in
  the way are moved to `~/.local/state/impasto/backups`.
* **Skip flags exist for every subsystem** (`--skip-packages`, `--skip-system`, `--skip-plugins`,
  `--skip-extras`), so a partial install is a first-class path rather than an afterthought.
* **It follows the distribution rather than fighting it.** The login screen is enabled only
  where no other display manager is configured.
* **Face unlock is isolated.** It is a separate PAM service (`/etc/pam.d/impasto-face`, used only
  by the lock screen, installed only by the opt-in `./setup face`), so a failed face match does
  not consume password attempts.
* **Hyprland 0.56+ requirement is satisfied by Arch's own packaging.** The project needs
  Hyprland 0.56 or newer; `extra/hyprland` is **0.56.2-3**. No `hyprland-git` is required, and
  the configuration uses Hyprland's native Lua config path rather than a patch on top of `.conf`.

## Conditions and risks

* **One maintainer.** 100 commits in 90 days is not abandonment, but it is a bus factor of one.
  Adopting this means being willing to fork it or fix forward.
* **It writes into `/` as well as `$HOME`.** `./setup system` installs into
  `/usr/lib/impasto`, `/etc/pam.d`, `/etc/systemd/logind.conf.d`, `/etc/sddm.conf.d` and can
  switch `/etc/systemd/system/display-manager.service`. All of it is documented in the script and
  reversible via `uninstall`, but `--dry-run` first is the honest recommendation.
* **`install` runs the optional integrations by default.** `--skip-extras` on a first pass avoids
  patching applications that may not be installed yet; anything skipped is retried by a later
  `install` or `update`.
* **Package installation is part of the same step** (`sudo pacman -Syu --needed`). On a system
  where you want to control upgrade timing, use `--skip-packages`.

## Verdict: Adopt

Nothing in the measurement disqualifies it, and several things actively recommend it: the
mandatory path is 100% official repositories, the package list is self-documenting, the install
is dry-runnable and reversible, and the compositor version it requires is the one Arch ships.
The costs are its size — 3.9 GB is the price of shipping a full desktop with fonts and
toolchain — and its single-maintainer bus factor.

## Sources

* Repository facts: GitHub REST API (`repos/andreumassanet/impasto` and related endpoints), 2026-09-23.
* Package list: `packages/pacman.txt` and `packages/aur.txt`, fetched verbatim and parsed
  programmatically (`tools/classify-stack.py`), never retyped.
* Closure: `data/builds.tsv` and `data/builds.json`.
* Install behaviour: the project's `setup` script, read at the line level (1,548 lines).
* Component licences and links: [CREDITS.md](../CREDITS.md).

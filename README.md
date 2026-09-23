# Wayland Desktop Audit

Measured install cost and full dependency closures for Wayland desktop stacks on **Arch Linux**,
plus source-level audits of three community builds — [impasto], [wayle] and [rust-dock].

Everything here is measured from primary sources: the official Arch repository databases, the
AUR RPC, the GitHub API, and the audited projects' own files. Every number has a provenance
chain behind it (see [Method](#method)), and every claim about a dependency names the exact
token that pulls it in.

> **Point in time.** All figures were measured on **2026-09-23** against the Arch `core`,
> `extra` and `multilib` databases as published that day. Packages move; star counts and
> commit velocity move faster. Re-run the tools in this repo to refresh any of it.

---

## What this is, and what it is not

**It is** a reproducible measurement of what a desktop stack actually costs you in packages and
installed megabytes, and why. Package count and closure size are the part of a rice you cannot
see in a screenshot, and they are usually the part that decides whether an install is pleasant.

**It is not** a review, a benchmark of runtime speed, or a security audit. It does not measure
RAM or CPU at runtime, does not test Wayland protocol behaviour, and does not read anyone's
source code for vulnerabilities. See [Limits](docs/method.md#limits) for the full list of what
these numbers do and do not include.

**No upstream source code is vendored here.** Audited projects are referenced by URL and by
facts read from their public interfaces (package lists, manifests, install scripts). See
[CREDITS.md](CREDITS.md).

---

## Audited builds at a glance

| | [impasto] | [wayle] | [rust-dock] |
|---|---|---|---|
| **scope** | whole desktop (compositor, shell, terminal, editors, login screen) | shell (bar, notifications, OSD, wallpaper, devices) | dock only |
| **implementation** | QML on Quickshell | Rust, GTK4 + Relm4 | Rust, GTK4 |
| **license** | GPL-3.0 | MIT | conflict: `LICENSE` = GPL-3.0, `Cargo.toml` = MIT |
| **packages in closure** | **629** | **226** | **213** |
| **installed size** | **3,863.8 MB** | **1,007.7 MB** | **979.1 MB** |
| **AUR in mandatory path** | 0 of 85 declared | 1 (`wayle-bin`, 2 votes) | 0 |
| **last commit** | 2026-09-22 | 2026-07-25 | 2026-08-26 |
| **commits / last 90 days** | 100 | 3 | 2 |
| **contributors** | 1 | 25 | 1 |
| **open issues** | 1 | 166 | 0 |
| **latest release** | v0.3.2 | v0.7.0 | none |
| **verdict** | [Adopt](docs/audit-impasto.md) | [Watch](docs/audit-wayle.md) | [Adopt w/ conditions](docs/audit-rust-dock.md) |

The *installed size* column is the complete transitive closure resolved from the official
repositories — not the size of the app itself. It is the number that matters when the stack is
being installed onto a bare system, and it is consistently about an order of magnitude larger
than the headline package. `wayle-bin` itself is a few megabytes; its closure is a gigabyte.

### Two components are cheaper together than apart

Taken together, the bar and the dock cost what the bar alone costs:

| stack | packages | installed |
|---|---|---|
| `hyprland` + `wayle` | 269 | 1,113.7 MB |
| `hyprland` + `wayle` + `rust-dock` runtime deps | **270** | **1,113.7 MB** |

The delta is one package (`grim`) and effectively zero megabytes: GTK4 and `gtk4-layer-shell`
are already in the bar's closure. Measured by diffing the two package sets, not assumed — see
[data/builds.json](data/builds.json) and [data/combos.json](data/combos.json).

---

## The stack race: nine stacks, same three slots

Each stack is a compositor + a shell/bar + a theme engine, resolved from the official repos
(AUR only where a component genuinely lives there). Ordered by installed size.

| stack | packages | installed | marginal over shared floor | AUR in the path |
|---|---|---|---|---|
| `river` + `yambar` + `wallust` | 172 | 622.4 MB | 25.3 MB | yambar, wallust |
| `mangowm-git` + `quickshell` + `matugen` | 203 | 948.6 MB | 351.6 MB | mangowm-git |
| `hyprland` + `noctalia` + `matugen` | 234 | 1,053.6 MB | 456.5 MB | — |
| `labwc` + `waybar` + `wallust` | 275 | 1,120.1 MB | 523.0 MB | wallust |
| `sway` + `waybar` + `wallust` | 274 | 1,124.9 MB | 527.9 MB | wallust |
| `niri` + `noctalia` + `matugen` | 240 | 1,131.6 MB | 534.5 MB | — |
| `hyprland` + `dms-shell-hyprland` + `matugen` | 233 | 1,168.2 MB | 571.1 MB | — |
| `niri` + `dms-shell-niri` + `matugen` | 238 | 1,242.2 MB | 645.1 MB | — |
| `hyprland` + `caelestia-shell` + `matugen` | 393 | 1,839.5 MB | 1,242.5 MB | caelestia-shell (+5 unresolved) |

All nine stacks share a floor of **134 packages / 597.1 MB** — `glibc`, `systemd`, `python`,
`perl`, `git` and friends that any system has anyway. The *marginal* column is what the
desktop choice itself adds on top of that floor. The floor is the *intersection* of the stacks in
a table, so it moves with the set: 127 packages / 592.4 MB across the 14 combination stacks and
the 12 build stacks, because a larger set of stacks has a smaller intersection. Full resolution in
[data/closure.tsv](data/closure.tsv) and [docs/stack-race.md](docs/stack-race.md).

Two things this table shows that the packages' own sizes do not:

* The compositor is rarely the expensive part. `sway` is 5.6 MB, `niri` is 24.9 MB — but the
  shell's toolkit decides the closure.
* A stack can be *lighter* and still score worse on maintainability. `river` + `yambar` wins on
  megabytes and loses on AUR: both components live outside the official repos.

---

## Feature hunt: what each slot costs on its own

The stack race compares whole desktops. This compares the **parts**: [docs/features.md](docs/features.md)
costs **136 candidate packages across 41 desktop features** — bar, launcher, notification daemon,
lock screen, terminal, file manager, portal and the rest — each one probed for real availability
first and then resolved as a full closure.

Five candidate names looked plausible and did not exist. They were replaced with the real package
rather than dropped quietly: `swww` (gone from both repositories, superseded by `awww`),
`rofi-wayland` (folded into `rofi`), `hyprshot` → `hyprshot-git`, `rofimoji` → `rofimoji-git`,
`pywal16` → `python-pywal16`. One candidate, `adw-gtk3`, is packaged in neither repository and so
appears in no table.

One feature class is deliberately absent from those slots: **plugins**. Shake-to-find and glass —
impasto's two Hyprland plugins — are not packages at all. `hyprpm` compiles them from a GitHub
repository on first run, so they can be neither probed nor costed the way everything else here is.
They have their own file: **[docs/plugins.md](docs/plugins.md)**, covering what the feature pulls
in against a build that already carries a compiler toolchain (nothing — all seven of `hyprpm`'s
dependencies are already inside impasto's closure) and against one that does not (a full
toolchain, 79 packages / 489.4 MB on a bare Hyprland).

| slot | cheapest measured | MB | dearest measured | MB | swing |
|---|---|---|---|---|---|
| compositor | `river` | 600.4 | `niri` | 929.6 | 329.2 |
| bar / shell | `yambar` † | 282.8 | `caelestia-shell` † | 1,749.3 | 1,466.5 |
| launcher | `tofi` † | 238.1 | `walker` † | 1,026.4 | 788.3 |
| notifications | `fnott` | 244.3 | `swaync` | 1,111.2 | 866.9 |
| lock screen | `swaylock` | 348.7 | `gtklock` | 768.8 | 421.0 |
| on-screen display | `wob` | 129.9 | `swayosd` | 1,005.7 | 875.8 |
| wallpaper | `awww` | 76.4 | `mpvpaper` † | 1,040.5 | 964.1 |
| colour engine | `wallust` † | 63.5 | `python-pywal16` † | 379.7 | 316.2 |
| login screen | `ly` | 151.8 | `sddm` | 821.1 | 669.3 |
| terminal | `alacritty` | 170.4 | `ghostty` | 1,124.1 | 953.7 |
| file manager | `pcmanfm` | 778.0 | `dolphin` | 1,695.8 | 917.8 |
| portal | `xdg-desktop-portal-wlr` | 803.1 | `xdg-desktop-portal-kde` | 2,245.5 | 1,442.4 |

† AUR: requires building from source at install time.

Three things this shows that per-package sizes do not:

* **The splits are not GTK vs Qt; they are "is that toolkit already on the system".** Every
  candidate in a row that shares a toolkit with a candidate already installed is nearly free, and
  the absolute figures overlap so heavily that a bare-system comparison exaggerates every
  difference. Compare candidates within a row, not across rows.
* **The compositor is the cheapest slot.** `hyprland` is 763.2 MB of closure, `river` 600.4 — but
  a notification daemon or an OSD can each cost more than the compositor does.
* **Impasto's picks are aesthetic-first, and measurably so.** It takes the cheapest official bar
  (`quickshell`) and the cheapest wallpaper (`awww`), but also the dearest login screen (`sddm`,
  +669.3 MB over `ly`), the dearest polkit agent (`polkit-kde-agent`, +193.3 MB over
  `lxqt-policykit`) and the dearest terminal it ships besides `ghostty` (`kitty`, +540.3 MB over
  `alacritty`). That is a coherent trade, not an error — it is simply 1.4 GB of the install that
  a cost-first build would not have spent.

---

## Why the numbers look like that

Five chains, each traced from the stack root to the package with the exact dependency token.
Reproduce any of them with `tools/why-chain.py` (see [Reproduce](#reproduce)).

**1. A GTK4 bar drags GTK3 in, because `gtk4` hard-depends on a GTK3 portal.** This is the
single biggest surprise in the audit, and it is upstream packaging, not a resolver guess —
`gtk4`'s own `DEPENDS` line literally contains `xdg-desktop-portal-gtk`:

```
gtk4-layer-shell --[gtk4]--> gtk4
              --[xdg-desktop-portal-gtk]--> xdg-desktop-portal-gtk
              --[gtk3]--> gtk3                       (53.0 MB)
```

`gtk4` is 52.1 MB installed and pulls ~1 GB of closure. Any "lightweight Rust + GTK4"
bar or dock inherits this — it is cheap only if GTK4 is already on the system.

**2. Waybar is not the cheap bar it is assumed to be.** Its own size is 2.2 MB, but its
`DEPENDS` line names `gpsd`, `gtk3`, `gtkmm3`, `jack`, `sndio` and `playerctl` outright:

```
waybar --[gpsd]--> gpsd          (5.4 MB)
       --[python]--> python      (73.6 MB)
```

A location daemon and a Python interpreter for a status bar. (`python` may already be present
on a desktop system for unrelated reasons, in which case only the increment is attributable.)

**3. Noctalia pays for `git` at runtime.** `noctalia`'s `DEPENDS` contains `git` by name:

```
noctalia --[git]--> git       (31.3 MB)
         --[perl]--> perl     (70.3 MB)
```

**4. Niri still lands on GTK3**, via the portal virtual that its own `DEPENDS` names
(`xdg-desktop-portal-impl`), resolved by compositor:

```
niri --[xdg-desktop-portal-impl]--> xdg-desktop-portal-gtk
     --[gtk3]--> gtk3              (53.0 MB)
```

**5. Hyprland reaches `glycin` through its own graphics stack:**

```
hyprland --[hyprgraphics]--> hyprgraphics --[librsvg]--> librsvg
         --[gdk-pixbuf2]--> gdk-pixbuf2 --[glycin]--> glycin      (17.5 MB)
```

## Method

Closed-world dependency resolution against the official Arch databases, offline, with a
recorded parent chain for every package that enters a closure. The rules that matter — and the
three defects they were written to fix — are documented in **[docs/method.md](docs/method.md)**.
Short version:

* Resolve the full transitive closure (BFS to exhaustion), not declared dependencies.
* Never guess a **virtual** that hardware satisfies (`opengl-driver`, `vulkan-driver`,
  `ttf-font`, …). Record it and skip it.
* A hardware driver package must never satisfy a generic soname.
* A 64-bit package's soname must never resolve to a `lib32-*` package.
* `xdg-desktop-portal-impl` is chosen by compositor, not by smallest dependency count.
* Every multi-provider choice is **logged** to `data/*-guesses.json`, so a bad guess is
  visible rather than silently inflating a number.

The resolver itself was fixed three times while this audit was being run, each time because a
measured result contradicted the previous rule. Those failures are documented rather than
quietly corrected, because they are the reason to trust the current output: a 948 MB NVIDIA
driver appearing in every closure, a closure truncated at depth one, and 168 MB of 32-bit LLVM
arriving in a 64-bit bar's dependency list. See
[Resolver defects found by measurement](docs/method.md#resolver-defects-found-by-measurement).

## Verdicts

Tiers are assigned against a stated rubric, not by feel. Full reasoning in each audit doc.

| tier | meaning |
|---|---|
| **Adopt** | sound for its intended scope; documented provenance; reversible install |
| **Adopt with conditions** | sound, but depends on a precondition or needs a follow-up fix |
| **Watch** | technically sound, but current maintenance signals do not justify depending on it |
| **Reject** | a measured property disqualifies it (none in this audit) |

* **[impasto](docs/audit-impasto.md) — Adopt.** 85 declared packages, every one in the
  official repositories and every one annotated with the reason it is there; install script is
  dry-runnable and uninstallable; requires Hyprland 0.56+ and Arch's `extra` ships 0.56.2.
  Conditions: one maintainer, and it writes into `/` as well as `$HOME`, so read the script
  before running it.
* **[wayle](docs/audit-wayle.md) — Watch.** Correct architecture, official-repo dependencies,
  MIT, compositor-agnostic. But 3 commits in 90 days against 166 open issues, and the AUR
  `wayle-bin` binary package has 2 votes.
* **[rust-dock](docs/audit-rust-dock.md) — Adopt with conditions.** Effectively free beside any
  GTK4 shell (one package). Conditions: from a bare base it costs its own full GTK4 closure, and
  its colour sync reads **pywal**, which is archived and has not released since 2019-01-21.

## Install guide

**[docs/install-impasto-on-arch.md](docs/install-impasto-on-arch.md)** — a generic, paste-ready
walkthrough for putting impasto on a fresh Arch system: minimal `archinstall`, the project's own
`./setup` ritual, verification gates, and rollback. Includes a practical gotcha: staging the
repository on FAT32 loses the executable bit on its 85 executable files, `setup` included.

## Reproduce

Requires Python 3 (standard library only) and, for the repo-facts pass, the GitHub CLI.

```bash
# 1. repo provenance facts for the candidate projects (writes data/repos.tsv)
./tools/recon-repos.sh data/repos.tsv

# 2. resolve closures for the nine stacks (downloads the Arch databases once, ~10 MB)
python3 tools/pkg-closure-v2.py

# 3. prove why a package is in a closure
python3 tools/why-chain.py "sway+waybar+wallust" gpsd python

# 4. audit a build found in the wild: classify its own package list, then cost it
python3 tools/classify-stack.py "some-build" path/to/its-package-list.txt --out data/my-stacks.json
python3 tools/pkg-closure-v2.py --stacks data/my-stacks.json --out my-build

# 5. cost every desktop slot, not every stack (writes data/features-availability.tsv, docs/features.md)
python3 tools/pkg-features.py
python3 tools/pkg-closure-v2.py --stacks data/features-stacks.json --out features
python3 tools/feature-report.py docs/features.md

# 6. probe an ad-hoc candidate list before costing it — "does this even exist?"
python3 tools/probe-names.py data/probe-shake-to-find.txt data/shake-to-find.tsv
python3 tools/pkg-closure-v2.py --stacks data/shake-to-find-stacks.json --out shake
```

Tools accept `--stacks <file.json>` to add stack definitions and `--out <name>` to name the
output set. `tools/why.py` prints raw `DEPENDS` lines from the cached databases — the ground
truth behind any single claim. `tools/closure-inspect.py` lists what a stack pulls that it
probably should not.

## Data

| file | what it is |
|---|---|
| [`data/repos.tsv`](data/repos.tsv) | provenance facts per candidate project (GitHub API) |
| [`data/availability.tsv`](data/availability.tsv) | official-repo vs AUR availability per component |
| [`data/features.tsv`](data/features.tsv) | the feature hunt: 136 candidates across 41 slots, costed |
| [`data/features-availability.tsv`](data/features-availability.tsv) | where each feature candidate actually lives |
| [`data/shake-to-find.tsv`](data/shake-to-find.tsv) | the plugin probe: two plugins that no repository packages |
| [`data/shake.tsv`](data/shake.tsv) | what the plugin class does cost (its build toolchain) |
| [`data/closure.tsv`](data/closure.tsv) | the nine-stack race, resolved |
| [`data/combos.tsv`](data/combos.tsv) | combinations, including the two-component case |
| [`data/builds.tsv`](data/builds.tsv) | the three audited builds, costed |
| `data/*.json` | full detail: per-stack membership, recorded parent chains, and every resolver guess |
| [`data/README.md`](data/README.md) | column meanings and provenance of every file |

## Credits

All audited and referenced projects belong to their authors and keep their own licenses.
This audit is independent and unaffiliated, and no project here has reviewed or endorsed it.
See **[CREDITS.md](CREDITS.md)**.

## Corrections

Measured numbers age. If a figure here no longer matches reality, open an issue with the
command you ran and its output — a correction with a reproduction beats a correction without.

What to expect when you re-run: the same package **membership**, with sizes that moved. Across
a re-download two hours after these numbers were taken, 260 package versions and 198 installed
sizes had changed while zero packages were added or removed. Every JSON artifact records the
database snapshot it measured in `db_vintage`, so a difference can be attributed: an identical
`db_vintage` with different numbers is a defect in these tools and worth reporting as one; a
changed `sha256` means the Arch databases moved and the difference is drift.

## License

MIT for the analysis, documentation and tooling in this repository. Upstream projects keep
their own licenses. See [LICENSE](LICENSE).

[impasto]: https://github.com/andreumassanet/impasto
[wayle]: https://github.com/wayle-rs/wayle
[rust-dock]: https://github.com/rhythmcreative/rust-dock

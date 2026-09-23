# The stack race: nine compositor + shell + theme stacks

Each row is one compositor, one shell/bar, one theme engine. Everything was resolved from the
official Arch repositories; the AUR was used only where a component genuinely lives there. Ordered
by installed size, which is the from-scratch cost of the whole closure.

| stack | packages | installed | marginal over floor | AUR in the path |
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

**Shared floor: 134 packages / 597.1 MB** present in all nine — `glibc`, `systemd`, `python`,
`perl`, `git`. The *marginal* column is the desktop choice's own contribution on top of that.
(The floor is the intersection of the measured stacks, so it differs between tables — the 14
combination stacks and 12 build stacks share 127 packages / 592.4 MB instead.)

Data: [../data/closure.tsv](../data/closure.tsv), full detail in `../data/closure.json`.

## Components, as they stand in the repositories

| component | where | version | votes | installed |
|---|---|---|---|---|
| `hyprland` | extra | 0.56.2-3 | — | 64.0 MB |
| `niri` | extra | 26.04-1 | — | 24.9 MB |
| `sway` | extra | 1.12-4 | — | 5.6 MB |
| `river` | extra | 0.4.8-2 | — | 1.1 MB |
| `labwc` | extra | 0.20.2-1 | — | 0.7 MB |
| `wayfire` | extra | 0.11.0-1 | — | 8.8 MB |
| `mangowm-git` | AUR | 0.16.0.r0 | 12 | — |
| `noctalia` | extra | 5.1.0-1 | — | 32.7 MB |
| `quickshell` | extra | 0.3.1-1 | — | 6.0 MB |
| `dms-shell` | extra | 1.6.2-1 | — | **71.8 MB** |
| `waybar` | extra | 0.15.0-3 | — | 2.2 MB |
| `caelestia-shell` | AUR | 2.5.0-1 | 8 | — |
| `yambar` | AUR | 1.11.0-1 | 20 | — |
| `matugen` | extra | 4.2.0-1 | — | 11.4 MB |
| `wallust` | AUR | 3.5.2-1 | 19 | — |

Note where a component is *not*: `quickshell`, `noctalia` and `dms-shell` are all in `extra`, so
the QML-shell stacks need no AUR at all. The AUR appears in the lightest stack (`yambar`,
`wallust`) and in the heaviest (`caelestia-shell`), which is the whole tension in one line.

## How to read the table

**The compositor is rarely the expense.** `sway` is 5.6 MB and `niri` is 24.9 MB; both land
within 10 MB of each other after closure (1,124.9 vs 1,131.6 MB). What separates stacks is the
shell and the toolkit it brings, not the compositor.

**The cheapest stack is the least robust one.** `river` + `yambar` + `wallust` wins at 622.4 MB,
but two of its three components live in the AUR. `hyprland` + `noctalia` + `matugen` costs 431 MB
more and pulls from official repositories only — and is marginally lighter than several Waybar
stacks despite being a full QML shell, because it does not drag a toolkit it does not use
(see [findings.md](findings.md#3-noctalia-pulls-git-and-therefore-perl-at-runtime)).

**`dms-shell` is the heaviest shell per byte installed** (71.8 MB on its own, ahead of `noctalia`'s
32.7 MB), and both `dms` stacks land above their `noctalia` counterparts on the same compositor.
The difference is small enough (114 MB on Hyprland) to be irrelevant next to how the two shells
feel to use — which this audit does not measure.

**`caelestia-shell` is inflated in this table and understated at the same time.** It costs
1,839.5 MB through the official path, and **five of its AUR dependencies could not be resolved**
(`caelestia-cli`, `libcava`, `qt6-m3shapes-git`, `quickshell-git`, `ttf-rubik-vf`), so its true
from-scratch cost is higher than shown. An AUR-hosted shell with an AUR dependency chain is the
least reproducible configuration here.

**AUR votes, for what they are worth.** They are a weak signal, but they are not nothing:
`yambar` (20), `wallust` (19), `mangowm-git` (12) have some review behind them; `caelestia-shell`
(8) and `hyprpanel` (0) have less.

## Packaging traps found while resolving this

* **`mango` on the AUR is not the compositor.** It is `2.0.1-1`, described as "a tool for making
  backups of Arch packages", with 0 votes. The compositor is packaged as **`mangowm-git`**.
* **`ags` on the AUR is not Aylur's GTK Shell.** The name resolves to
  "Engine to run adventure/quest games" (9 votes). The shell is packaged as **`aylurs-gtk-shell`**.
* **`dwl` is still in the AUR at 0.9-1, while upstream is archived** (last commit 2023-11-25).
  An AUR package whose upstream no longer moves is a maintenance dead end, whatever its 11 votes.
* **`noctalia-shell` and `pywal` do not exist under those names** in either the repositories or the
  AUR, although both are natural guesses. `noctalia` is the package; `python-pywal` is the AUR
  name for pywal.
* **`niri` reports version `26.04-1`** in `extra`, which looks like a date rather than a release —
  worth noting so it is not mistaken for a resolver bug.

Every one of these was found by resolving names against the actual databases rather than assuming
that a project's name is its package name. `data/availability.tsv` records the full probe,
including the guesses that found nothing.

## Reproducing this table

```bash
python3 tools/pkg-closure-v2.py                    # the nine stacks, as defined in the script
python3 tools/pkg-closure-v2.py --stacks data/combo-stacks.json --out combos
python3 tools/closure-inspect.py                   # what a stack pulls that it should not
```

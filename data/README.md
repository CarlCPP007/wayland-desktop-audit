# Data files

All numbers in the README and the audit docs come from these files. Every one was produced by the
tools in `../tools/` from primary sources on **2026-09-23**; nothing here was typed by hand.

## Provenance

| source | what it supplies |
|---|---|
| Arch `core` / `extra` / `multilib` databases (official mirrors) | names, versions, `DEPENDS`, `PROVIDES`, installed size |
| AUR RPC | version, votes, declared dependencies for AUR packages |
| GitHub REST API (via `gh`) | stars, license, language, last push, commit counts, contributors, issues, releases |
| the audited projects' repositories | their own declared package lists and manifests, fetched verbatim |

The Arch databases themselves are **not committed** (`data/db/` is gitignored): they are
third-party data, several megabytes each, and stale the day after they are downloaded. The tools
fetch them on demand. Re-running any tool after the databases refresh will produce different
numbers, which is the point.

## Tables

### `repos.tsv` — provenance facts per candidate project

Produced by `tools/recon-repos.sh`. One row per project: repository, stars, language, last push
date, archived flag, license, open issues, size. Used for the maintenance signals in the audited
builds and for detecting dead projects (`dwl` and `pywal` are archived; `HyprPanel` is archived).

### `availability.tsv` — where does each component actually live?

Produced by `tools/pkg-availability.py`. Columns:

| column | meaning |
|---|---|
| `axis` | `COMP` (compositor), `SHELL`, or `THEME` |
| `pkg` | the name that was probed |
| `where` | `official`, `AUR`, or `NONE` if the name does not exist anywhere |
| `repo` | `core` / `extra` / `multilib` when official |
| `version` | version at time of measurement |
| `votes` | AUR votes, where applicable |
| `depends_n` | number of declared dependencies |
| `installed_bytes` | installed size, official packages only (the AUR does not publish one) |
| `desc` | package description, truncated |

`where = NONE` rows are deliberate: they record name guesses that found nothing, so a later reader
can see which names are *not* valid packages. Several traps were found this way — `mango` is a
backup tool and not the compositor, `ags` is a game engine and not Aylur's GTK Shell.

### `closure.tsv` / `combos.tsv` / `builds.tsv` — the measurements

Produced by `tools/pkg-closure-v2.py`. Columns:

| column | meaning |
|---|---|
| `stack` | the stack's label |
| `pkgs` | packages in the full transitive closure |
| `installed_MB` | installed size of that closure |
| `marginal_pkgs` | closure minus the shared floor |
| `marginal_MB` | installed size of the marginal set |
| `aur_roots` | AUR packages that were used as roots |
| `aur_unresolved` | names that could not be resolved — a gap in the data, shown rather than hidden |

* `closure.tsv` — the nine compositor + shell + theme stacks. Shared floor: **134 packages /
  597.1 MB**.
* `combos.tsv` — the nine plus combination cases (`wayle` + `rust-dock`, `hyprland` + `quickshell`).
  Shared floor: 127 packages / 592.4 MB.
* `builds.tsv` — the three audited builds, each costed from its own declared dependencies. Shared
  floor: 127 packages / 592.4 MB.

The floor is the **intersection** of the stacks in that dataset, so it shrinks as the dataset
grows. Marginals are always relative to their own dataset's floor.

### Traceability, and where it stops

`parents` records `child -> [parent, exact dependency token]` for every package pulled in through
the official repositories, which is what `tools/why-chain.py` walks to produce a chain. Two things
are legitimately absent:

* **Roots**, which have no parent by definition — so a stack with two official-repo roots reports
  exactly two untraced members.
* **Everything reached through an AUR package's declared dependencies.** AUR packages are resolved
  from RPC metadata rather than from a local database, and parent edges are not recorded for that
  path. AUR-rooted stacks therefore show large untraced sets — 208 of 393 members for
  `hyprland` + `caelestia-shell`, 37 of 203 for `mangowm-git`, 21 of 172 for `river` + `yambar` +
  `wallust`. Stacks with official roots only show 1–3.

An untraced package in a stack whose roots are all official is a defect. `tools/why-chain.py`
prints the traced-versus-total counts for every stack so the two cases can be told apart.

### `*.json` — the detail behind the tables

| file | contents |
|---|---|
| `<name>.json` | per-stack membership (`detail`), the recorded parent chain for every package (`parents`), the shared floor, and which hardware virtuals were skipped |
| `<name>-guesses.json` | every multi-provider resolution decision, with its candidates and the rule used |

`parents` is what makes the audit falsifiable: for any package in any closure, it records the
parent that pulled it in and the **exact dependency token** responsible.
`tools/why-chain.py` walks those edges back to the stack root, which is how every claim in
`../docs/findings.md` can be reproduced in one command.

`*-guesses.json` exists so that resolver guesswork is auditable. A package appearing in a closure
because of an unambiguous declaration and a package appearing because of a reasoned tie-break are
different kinds of claims, and the files keep them apart.

## Build inputs

`combo-stacks.json` and `builds-stacks.json` are the stack definitions fed to the resolver via
`--stacks`. They are the reproducible input for the combination and build tables: roots marked
`repo` resolve from the official databases, roots marked `aur` resolve from the AUR RPC.

## Reproducing

```bash
./tools/recon-repos.sh data/repos.tsv
python3 tools/pkg-closure-v2.py                                          # -> closure.{json,tsv}
python3 tools/pkg-closure-v2.py --stacks data/combo-stacks.json  --out combos
python3 tools/pkg-closure-v2.py --stacks data/builds-stacks.json --out builds
python3 tools/why-chain.py --file combos.json "hyprland+wayle+rust-dock" gtk3
```

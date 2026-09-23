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

Measured, so the shape of that drift is known rather than assumed: across a re-download two hours
after the numbers below were taken, **260 package versions and 198 installed sizes changed** while
the package **membership stayed exact** — 15,463 packages, none added, none removed. Same package
set, different megabytes.

That is why every JSON output records the snapshot it measured, in `db_vintage`: a `sha256`, an
`mtime` and a byte count for each of `core.db`, `extra.db` and `multilib.db`, plus the total
package count and a per-repository count.

```json
"db_vintage": {
  "extra.db": {"sha256": "f3b7154e…", "mtime": "2026-09-23 07:55:50", "bytes": 8850251},
  "packages": 15463,
  "repos": {"core": 299, "extra": 14982, "multilib": 182}
}
```

Two artifacts are only comparable when their `db_vintage` matches. **Same snapshot and different
numbers is a defect in the tooling. A moved `sha256` means Arch updated**, and the difference is
upstream drift rather than a correction — which is the distinction the reproducibility gate tests.

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

One row in this table was wrong when first published: `nwg-shell` was recorded as `NONE`, because
the probe accepted only `x86_64` packages and `nwg-shell` is architecture-independent (`any`).
It is in `extra` at 0.5.50-1 with 41 dependencies. Both probes now accept `any`, and the row is
corrected in place. The same defect would have hidden every architecture-independent candidate —
fonts, icon themes, `tlp`, `ranger`.

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

### `features.tsv` — the feature hunt

Produced by `tools/pkg-closure-v2.py --stacks data/features-stacks.json --out features`, then
rendered by `tools/feature-report.py`. Same columns as above, but each row's label is
`<feature> :: <candidate>` — one candidate for one desktop slot. 136 candidates across 41
features.

Read it for **ordering within a feature**, not for cross-feature totals: the candidates for
different slots do different jobs, and their closures overlap so heavily (a shared GTK3, Qt or
Wayland base of roughly 600 MB) that the absolute figures are not comparable across rows. Because
`--stacks` merges into the built-in nine, this file also contains those nine stacks; the report
skips any label without ` :: `.

`marginal` is degenerate here — the intersection across 145 mixed stacks is empty — so
`marginal_MB` equals `installed_MB`. This is expected for this dataset and is why the report
ignores the marginal columns.

### `features-availability.tsv` — where each feature candidate lives

Produced by `tools/pkg-features.py` from `features-catalog.json`. Columns: `feature`, `pkg`,
`where` (`official` / `AUR` / `NONE`), `repo`, `version`, `votes`, `depends_n`,
`installed_bytes`, `desc`.

Candidates that do not exist are **removed from the run** rather than costed as zero, and the
removal is recorded in `features-catalog.json`. Five names in the first draft of the catalog did
not exist and were replaced with the real package: `swww` (gone from both repositories,
superseded by `awww`), `rofi-wayland` (folded into `rofi`), `hyprshot` → `hyprshot-git`,
`rofimoji` → `rofimoji-git`, `pywal16` → `python-pywal16`.

### `shake-to-find.tsv`, `shake-to-find-stacks.json`, `shake.*` — the plugin probe

Plugins are the one feature class that is not a package: `hyprpm` compiles them from a GitHub
repository on first run, so there is nothing in either database to find. `probe-shake-to-find.txt`
is the candidate list for that class — both plugin names, `hyprpm` itself, the toolchain it needs,
and the cursor chain — and `shake-to-find.tsv` is what the probe returned.

Both plugin names come back `NONE`. That is a statement about the **names**, not proof of absence:
the upstream repositories were confirmed separately with the GitHub API, and both are active. See
`docs/plugins.md`. `shake-to-find-stacks.json` costs what the feature does pull in, and `shake.*`
is the resulting measurement — including the finding that against a build which already carries
the toolchain, the feature adds zero packages.

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

`combo-stacks.json`, `builds-stacks.json`, `features-stacks.json` and `shake-to-find-stacks.json`
are the stack definitions fed to the resolver via `--stacks`. They are the reproducible input for
the combination, build and feature tables: roots marked `repo` resolve from the official databases,
roots marked `aur`
resolve from the AUR RPC. `features-catalog.json` is the human-edited feature catalogue that
`tools/pkg-features.py` turns into `features-stacks.json`.

Because `--stacks` adds to the built-in nine rather than replacing them, a run over a 136-entry
feature file reports 145 rows. That is expected; the published tables are consistent with it.

## Reproducing

```bash
./tools/recon-repos.sh data/repos.tsv
python3 tools/pkg-closure-v2.py                                          # -> closure.{json,tsv}
python3 tools/pkg-closure-v2.py --stacks data/combo-stacks.json  --out combos
python3 tools/pkg-closure-v2.py --stacks data/builds-stacks.json --out builds
python3 tools/pkg-features.py                                            # -> features-{availability.tsv,stacks.json}
python3 tools/pkg-closure-v2.py --stacks data/features-stacks.json --out features
python3 tools/feature-report.py docs/features.md
python3 tools/why-chain.py --file combos.json "hyprland+wayle+rust-dock" gtk3
```

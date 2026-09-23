# Tools

Python 3, standard library only, except `recon-repos.sh` which uses the `gh` CLI. No third-party
packages to install. Run them from the repository root.

| tool | what it does |
|---|---|
| `pkg-closure-v2.py` | the resolver. Downloads the Arch databases into `data/db/` on first run, then works offline. Resolves every stack's full transitive closure, records the parent chain for each package, and writes `<out>.json`, `<out>.tsv` and `<out>-guesses.json`. The JSON carries `db_vintage` — a `sha256`, `mtime` and byte count per database — so a difference between two runs can be attributed to upstream drift instead of guessed at. |
| `why-chain.py` | walks the recorded parent edges to explain why a package is in a closure: `why-chain.py "sway+waybar+wallust" gpsd python`. Prints `traced/total` per stack. |
| `why.py` | prints the raw `DEPENDS` line from the cached database for a package — the ground truth behind any single claim. |
| `closure-inspect.py` | reports what a stack pulls in that it probably should not: 32-bit packages, GPU drivers, toolkits the stack does not use. |
| `classify-stack.py` | takes another project's package list and classifies every entry official-repo vs AUR, emitting a stack file the resolver can consume. This is how a build found in the wild gets costed. |
| `pkg-availability.py` | probes a candidate list against both the official databases and the AUR RPC and reports where each component actually lives, plus votes, dependency count and installed size. Records misses explicitly. |
| `pkg-features.py` | feature-hunt stage 1. Reads `data/features-catalog.json` (feature → candidate packages), probes every candidate, drops the ones that do not exist, and writes `data/features-availability.tsv` plus a resolver input file. |
| `feature-report.py` | feature-hunt stage 2. Merges measured closures with availability into `docs/features.md`: one table per feature, cheapest-to-dearest, with unmeasurable AUR candidates marked rather than ranked. |
| `probe-names.py` | probes an ad-hoc `axis<TAB>name` list — official repositories first, then the AUR — so a name typed in chat is proven to exist before it is costed. Writes a TSV the resolver can consume. Reports `NONE` for names it cannot find, and says so out loud: `NONE` is a claim about the name, not proof of absence, so search by keyword before dropping a candidate. This is the entry point for adding a feature that is not yet in the catalogue. Its first real use is the plugin class in `docs/plugins.md`, where every candidate legitimately probes `NONE` because plugins are not packages. |
| `recon-repos.sh` | repository provenance facts via `gh api`: stars, language, last push, archived flag, license, open issues. Writes a TSV. |

## Options

```bash
python3 pkg-closure-v2.py                                   # the built-in nine stacks
python3 pkg-closure-v2.py --stacks data/combo-stacks.json --out combos
python3 pkg-closure-v2.py --stacks data/builds-stacks.json --out builds
python3 why-chain.py --file combos.json "hyprland+wayle+rust-dock" gtk3
```

`--stacks <file.json>` merges stack definitions into the built-in set; `--out <name>` names the
output trio. Stack file format — `repo` roots resolve from the official databases, `aur` roots
from the AUR RPC:

```json
{
  "hyprland+wayle+rust-dock": [
    ["repo", "hyprland"], ["repo", "gtk4"], ["repo", "gtk4-layer-shell"],
    ["repo", "grim"], ["aur", "wayle-bin"]
  ]
}
```

## Costing a build found in the wild

The workflow these tools exist for:

```bash
# 1. where does it actually live?
python3 pkg-availability.py

# 2. classify its own declared package list (fetched verbatim, never retyped)
python3 classify-stack.py "some-build" path/to/packages.txt --out data/my-stacks.json

# 3. cost it
python3 pkg-closure-v2.py --stacks data/my-stacks.json --out my-build

# 4. verify anything surprising
python3 why-chain.py --file my-build.json "some-build" gtk3
```

## The resolver's rules

Documented in full in [`../docs/method.md`](../docs/method.md), including the three defects that
the rules exist to prevent: a virtual resolved to a 948 MB GPU driver, a closure truncated at
depth one, and 168 MB of 32-bit LLVM arriving in a 64-bit bar's dependency list.

## Rules for adding a tool

Load-bearing, learned the hard way:

* **Resolve the closure, never the declared list.** Both other defects follow from trusting one
  level of dependencies.
* **Never guess a hardware-satisfied virtual.** Record it and move on: GPU drivers are a property
  of the machine, not of the desktop.
* **Log every multi-provider choice** to a `*-guesses.json` file. An unambiguous declaration and a
  reasoned tie-break are different kinds of claims and should not look alike in a total.
* **Print the gaps.** Unresolved names and untraced packages go in the output table, not into a
  smaller number.
* **Every table is regenerable from the tools alone.** If a number cannot be reproduced by running
  something in this repository, it does not belong in the documentation.

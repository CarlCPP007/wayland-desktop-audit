#!/usr/bin/env bash
# Recon pass 1 — repo facts via gh api (authed, 5000/hr). Writes TSV to data/.
set -uo pipefail
OUT="$1"
: > "$OUT"

REPOS=(
  # ── compositors ─────────────────────────────────────────────
  hyprwm/Hyprland
  YaLTeR/niri
  swaywm/sway
  riverwm/river
  labwc/labwc
  mangowm/mango
  WayfireWM/wayfire
  djpohly/dwl
  # ── shells / bars / toolkits (the RAM lever) ────────────────
  noctalia-dev/noctalia
  AvengeMedia/DankMaterialShell
  quickshell-mirror/quickshell
  Aylur/astal
  Jas-SinghFSU/HyprPanel
  Alexays/Waybar
  caelestia-dots/shell
  end-4/dots-hyprland
  Aylur/ags
  nwg-piotr/nwg-shell
  TheZoq2/yambar
  # ── theme engines ───────────────────────────────────────────
  InioX/matugen
  explosion-mental/wallust
  dylanaraps/pywal
  nix-community/stylix
)

printf 'repo\tstars\tlang\tpushed\tbranch\tarchived\tkb\tlicense\topen_issues\tlatest_tag\ttag_date\n' >> "$OUT"
for r in "${REPOS[@]}"; do
  line=$(gh api "repos/$r" \
    --jq '[.full_name,.stargazers_count,.language,.pushed_at,.default_branch,.archived,.size,(.license.spdx_id//"-"),.open_issues_count] | @tsv' 2>/dev/null)
  if [ -z "$line" ]; then
    printf '%s\tMISSING\t\t\t\t\t\t\t\t\t\n' "$r" >> "$OUT"
    continue
  fi
  tag=$(gh api "repos/$r/releases/latest" --jq '[.tag_name,.published_at] | @tsv' 2>/dev/null)
  [ -z "$tag" ] && tag=$'\t'
  printf '%s\t%s\n' "$line" "$tag" >> "$OUT"
done

column -t -s$'\t' "$OUT" 2>/dev/null || cat "$OUT"
echo
echo "rows: $(( $(wc -l < "$OUT") - 1 ))"

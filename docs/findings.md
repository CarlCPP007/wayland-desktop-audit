# Findings

Six things the measurements turned up that the packages' own sizes do not reveal. Each one names
the exact dependency token that causes it and the command that reproduces it.

Reproduce any of these after running `python3 tools/pkg-closure-v2.py` once (which populates
`data/db/` and `data/closure.json`):

```bash
python3 tools/why-chain.py "sway+waybar+wallust" gpsd python
python3 tools/why-chain.py "hyprland+noctalia+matugen" git perl
python3 tools/why-chain.py "niri+noctalia+matugen" gtk3
python3 tools/why-chain.py --file combos.json "hyprland+wayle+rust-dock" gtk3
python3 tools/why.py gtk4 waybar noctalia niri        # raw DEPENDS lines, the ground truth
```

---

## 1. `gtk4` hard-depends on a GTK3 portal, so every GTK4 app drags GTK3 in

The largest single surprise. `gtk4`'s own `DEPENDS` line names `xdg-desktop-portal-gtk`
literally — this is upstream Arch packaging, not a resolver guess:

```
gtk4-layer-shell --[gtk4]--> gtk4
              --[xdg-desktop-portal-gtk]--> xdg-desktop-portal-gtk
              --[gtk3]--> gtk3                              (53.0 MB)
```

`gtk4` is 52.1 MB installed. `xdg-desktop-portal-gtk` is 0.4 MB. `gtk3` is 53.0 MB. A GTK4 bar
therefore arrives with a GTK3 stack it will not use, and the same is true of any GTK4 dock,
editor or settings app.

**Why it matters:** a "lightweight Rust + GTK4" component is light *only if GTK4 is already
installed*. From a bare base, GTK4 is roughly a gigabyte of closure regardless of what is built
on it. Any comparison that measures the application's own package size gets this exactly
backwards.

Verify: `python3 tools/why.py gtk4` and read the `DEPENDS` line.

## 2. Waybar is not the cheap bar it is assumed to be

Waybar is 2.2 MB on disk, and it is routinely recommended as the light option. Its `DEPENDS`
line names `gpsd`, `gtk3`, `gtkmm3`, `jack`, `sndio` and `playerctl` outright:

```
waybar --[gpsd]--> gpsd          (5.4 MB)
       --[python]--> python      (73.6 MB)
```

A location daemon and a Python interpreter, pulled in by a status bar's declared dependencies.
`waybar`'s closure is 274 packages / 1,124.9 MB in the `sway` + `waybar` + `wallust` stack —
the second heaviest bar configuration measured, behind only the AUR-shell stack.

**Caveat, stated because it is easy to over-claim:** `python` is very often already installed on
a desktop system for unrelated reasons. On a machine that has it, only `gpsd` is genuinely
attributable to Waybar. The finding is about the closure, not about a guaranteed 79 MB saving.

## 3. Noctalia pulls `git` and therefore Perl at runtime

```
noctalia --[git]--> git       (31.3 MB)
         --[perl]--> perl     (70.3 MB)
```

`git` is a declared dependency of the shell, not a build-time tool — `noctalia`'s `DEPENDS`
contains it by name. In the race this puts `hyprland` + `noctalia` + `matugen` at 234 packages /
1,053.6 MB, marginally *lighter* than several Waybar stacks despite being a full QML shell,
because it does not pull a toolkit it does not need.

## 4. Niri still lands on GTK3 — through the portal virtual

Niri's own `DEPENDS` names the virtual `xdg-desktop-portal-impl`, which has four real providers.
Resolved by compositor (rule 5 in [method.md](method.md)), it becomes:

```
niri --[xdg-desktop-portal-impl]--> xdg-desktop-portal-gtk
     --[gtk3]--> gtk3              (53.0 MB)
```

A Wayland-native compositor written in Rust, with a GTK3 portal in its closure. This is not a
criticism of Niri — it is what the virtual resolves to on Arch, and it is invisible unless the
closure is resolved rather than the declared dependency list read.

## 5. Hyprland reaches `glycin` through its own graphics stack

```
hyprland --[hyprgraphics]--> hyprgraphics  (0.2 MB)
         --[librsvg]--> librsvg            (10.3 MB)
         --[gdk-pixbuf2]--> gdk-pixbuf2    (3.0 MB)
         --[glycin]--> glycin              (17.5 MB)
```

Four hops from the compositor to an image loader. Note how little the intermediate packages cost
— `hyprgraphics` is 0.2 MB and `gdk-pixbuf2` is 3.0 MB — which is exactly why closure size and
"sum of obvious packages" diverge.

## 6. Two components can be cheaper together than apart

Measured, by diffing package sets rather than assuming shared dependencies:

| stack | packages | installed | delta |
|---|---|---|---|
| `hyprland` + `wayle` | 269 | 1,113.7 MB | — |
| `hyprland` + `wayle` + `rust-dock` runtime deps | 270 | 1,113.7 MB | **+1 package (`grim`)**, +0.0 MB |

The dock's needs — GTK4 and `gtk4-layer-shell` — are already in the bar's closure, so adding it
costs `grim` and nothing else. The same dock from a bare base costs 979.1 MB, because it pays the
GTK4 entry fee from finding 1 on its own.

**The general lesson:** component cost is not additive, and "which shell is lightest" cannot be
answered without saying what else is already installed. Cost stacks, not parts.

---

## Two resolver defects that looked like findings

Both were initially indistinguishable from real results, and both are documented in
[method.md](method.md#resolver-defects-found-by-measurement) in full:

* **`sway` appearing heavier than `hyprland`** — a "fewest dependencies" tie-break resolved the
  `opengl-driver` virtual to the 948 MB NVIDIA driver in every stack, and pulled
  `lib32-nvidia-utils` (+562 MB) into `sway` only.
* **168 MB of 32-bit LLVM in a 64-bit bar** — `waybar`'s 64-bit soname `libgtk-3.so=0-64`
  resolved to `lib32-gtk3`.

Every remaining multi-provider decision is logged to `data/*-guesses.json` so this class of
error is auditable rather than invisible. If you find a number here that looks wrong,
`tools/why-chain.py` will either produce the chain that justifies it or tell you it cannot trace
it — in which case it is a bug, and reporting it is appreciated.

# Feature hunt — what each desktop feature costs

Every candidate below was probed for real availability and then costed as a
full transitive dependency closure against the Arch `core`/`extra`/`multilib`
databases. Nothing in this file is estimated: a candidate that does not exist in
either repository was removed from the run, and the replacing of five such names
(`swww`, `rofi-wayland`, `hyprshot`, `rofimoji`, `pywal16`) is recorded in
`data/features-catalog.json`.

**How to read the numbers.** `packages` and `MB` are the candidate's *entire*
closure — the package plus everything it needs. They are not directly
comparable across different features (a bar and a file manager do different
jobs); compare candidates *within* a row. `marginal` in
`data/features.tsv` equals the total here, because the intersection across 145
measured stacks is empty.

**AUR rows are a lower bound.** An official package resolves exactly, offline,
from the database dump. An AUR package has its own dependencies read from the
AUR RPC, but a dependency that cannot be reached that way is reported as
unresolved instead of guessed — so a suspiciously low AUR figure means
"not measurable offline", not "small". Where an AUR candidate resolved to a
single package or none at all it is marked **(unmeasurable)** and excluded from
the cheapest-option summary.

**Closures overlap heavily between features.** Each figure is a candidate's
whole closure, so `pavucontrol` reads 1,094 MB and `swayosd` 1,006 MB mostly
because both pay for the same GTK3 stack. The useful signal is the ordering
within a row and the outliers, not the absolute figure: once a toolkit is
already installed for something else, the next candidate on that toolkit is
almost free. The three whole builds measured in `data/builds.tsv` show what the
parts cost when combined — `hyprland` + `wayle` + `rust-dock` comes to
1,113.7 MB in total, less than any single bar candidate above listed alone.

A dagger (†) marks an AUR candidate: it needs `git`/`makepkg` at install time
and is not covered by the binary-repository trust chain.


## OCR

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `tesseract` | official | 5.5.3-1 |  | 80 | 291.5 | cheapest |
| `tesseract-data-eng` | official | 4.1.0-5 |  | 80 | 306.3 | +14.8 MB |

Cheapest: **`tesseract`** at 291.5 MB. Dearest: `tesseract-data-eng` at 306.3 MB (+14.8 MB).

## Qt theme

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `qt6ct` | official | 0.11-8 |  | 142 | 684.4 | cheapest |
| `kvantum` | official | 1.1.8-1 |  | 144 | 692.9 | +8.5 MB |

Cheapest: **`qt6ct`** at 684.4 MB. Dearest: `kvantum` at 692.9 MB (+8.5 MB).

## X11 apps

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `xorg-xwayland` | official | 24.1.13-1 |  | 130 | 583.8 | cheapest |

## audio

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `playerctl` | official | 2.4.1-5 |  | 19 | 145.9 | cheapest |
| `pipewire` | official | 1.6.9-1 |  | 41 | 193.9 | +48.0 MB |
| `wireplumber` | official | 0.5.17-2 |  | 44 | 198.5 | +52.6 MB |
| `pamixer` | official | 1.6-4 |  | 68 | 217.2 | +71.3 MB |
| `pavucontrol` | official | 6.2-1 |  | 236 | 1,094.3 | +948.4 MB |

Cheapest: **`playerctl`** at 145.9 MB. Dearest: `pavucontrol` at 1,094.3 MB (+948.4 MB).

## bar / shell

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `yambar`† | AUR | 1.11.0-1 | 20 | 88 | 282.8 | cheapest |
| `sfwbar`† | AUR | 1.0_beta17-1 | 11 | 173 | 770.0 | +487.2 MB |
| `quickshell` | official | 0.3.1-1 |  | 167 | 915.5 | +632.7 MB |
| `noctalia` | official | 5.1.0-1 |  | 185 | 933.8 | +651.0 MB |
| `wayle-bin`† | AUR | 0.7.0-1 | 2 | 226 | 1,007.7 | +724.9 MB |
| `hyprpanel`† | AUR | 0.3.1-1 | 0 | 255 | 1,085.1 | +802.3 MB |
| `waybar` | official | 0.15.0-3 |  | 264 | 1,115.2 | +832.4 MB |
| `dms-shell` | official | 1.6.2-1 |  | 232 | 1,156.8 | +874.0 MB |
| `aylurs-gtk-shell`† | AUR | 3.1.2-1 | 18 | 242 | 1,242.7 | +959.9 MB |
| `caelestia-shell`† | AUR | 2.5.0-1 | 8 | 362 | 1,749.3 | +1,466.5 MB |

Cheapest: **`yambar`** at 282.8 MB. Dearest: `caelestia-shell` at 1,749.3 MB (+1,466.5 MB).

## battery

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `upower` | official | 1.91.4-1 |  | 105 | 359.6 | cheapest |

## bluetooth

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `bluez-utils` | official | 5.87-2 |  | 40 | 190.6 | cheapest |
| `bluez` | official | 5.87-2 |  | 43 | 191.4 | +0.8 MB |
| `blueman` | official | 2.4.6-2 |  | 186 | 870.4 | +679.8 MB |

Cheapest: **`bluez-utils`** at 190.6 MB. Dearest: `blueman` at 870.4 MB (+679.8 MB).

## brightness

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `light`† | AUR | 1.2.2-5 | 18 | 0 (unmeasurable) | 0.0 | cheapest |
| `brillo`† | AUR | 1.4.13-1 | 22 | 18 | 75.8 | +75.8 MB |
| `brightnessctl` | official | 0.5.1-3 |  | 15 | 78.3 | +78.3 MB |
| `ddcutil` | official | 3.0.1-1 |  | 58 | 285.7 | +285.7 MB |

Cheapest: **`light`** at 0.0 MB. Dearest: `ddcutil` at 285.7 MB (+285.7 MB).

## clipboard

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `wl-clip-persist` | official | 0.5.0-2 |  | 7 | 66.5 | cheapest |
| `wl-clipboard` | official | 2.3.0-1 |  | 18 | 129.6 | +63.1 MB |
| `cliphist` | official | 0.7.0-2 |  | 19 | 131.9 | +65.4 MB |

Cheapest: **`wl-clip-persist`** at 66.5 MB. Dearest: `cliphist` at 131.9 MB (+65.4 MB).

## colour / theme

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `wallust`† | AUR | 3.5.2-1 | 19 | 6 | 63.5 | cheapest |
| `matugen` | official | 4.2.0-1 |  | 7 | 74.9 | +11.4 MB |
| `python-pywal`† | AUR | 3.3.0-11 | 1 | 72 | 370.4 | +306.9 MB |
| `python-pywal16`† | AUR | 1:3.8.15-1 | 19 | 76 | 379.7 | +316.2 MB |

Cheapest: **`wallust`** at 63.5 MB. Dearest: `python-pywal16` at 379.7 MB (+316.2 MB).

## colour picker

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `hyprpicker` | official | 0.4.7-4 |  | 42 | 229.3 | cheapest |

## compositor

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `river` | official | 0.4.8-2 |  | 152 | 600.4 | cheapest |
| `labwc` | official | 0.20.2-1 |  | 152 | 652.0 | +51.6 MB |
| `sway` | official | 1.12-4 |  | 151 | 656.8 | +56.4 MB |
| `wayfire` | official | 0.11.0-1 |  | 142 | 675.1 | +74.7 MB |
| `hyprland` | official | 0.56.2-3 |  | 186 | 763.2 | +162.8 MB |
| `niri` | official | 26.04-1 |  | 208 | 929.6 | +329.2 MB |

Cheapest: **`river`** at 600.4 MB. Dearest: `niri` at 929.6 MB (+329.2 MB).

## cursor

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `hyprcursor` | official | 0.1.13-7 |  | 99 | 362.7 | cheapest |

## dock

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `nwg-dock` | official | 0.4.3-4 |  | 173 | 774.3 | cheapest |
| `plank` | official | 0.11.89-6 |  | 180 | 778.0 | +3.7 MB |
| `nwg-dock-hyprland` | official | 0.4.11-1 |  | 173 | 782.4 | +8.1 MB |

Cheapest: **`nwg-dock`** at 774.3 MB. Dearest: `nwg-dock-hyprland` at 782.4 MB (+8.1 MB).

## editor

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `neovim` | official | 0.12.5-1 |  | 45 | 168.4 | cheapest |
| `helix` | official | 25.07.1-2 |  | 9 | 273.0 | +104.6 MB |

Cheapest: **`neovim`** at 168.4 MB. Dearest: `helix` at 273.0 MB (+104.6 MB).

## emoji picker

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `bemoji`† | AUR | 0.4.0-1 | 12 | 61 | 195.4 | cheapest |
| `rofimoji-git`† | AUR | 6.7.0.r6.g28bfdf9-1 | 2 | 36 | 207.5 | +12.1 MB |

Cheapest: **`bemoji`** at 195.4 MB. Dearest: `rofimoji-git` at 207.5 MB (+12.1 MB).

## file manager GUI

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `pcmanfm` | official | 1.4.0-2 |  | 178 | 778.0 | cheapest |
| `thunar` | official | 4.20.10-1 |  | 184 | 790.5 | +12.5 MB |
| `nautilus` | official | 50.3.1-1 |  | 397 | 1,533.8 | +755.8 MB |
| `dolphin` | official | 26.08.1-1 |  | 405 | 1,695.8 | +917.8 MB |

Cheapest: **`pcmanfm`** at 778.0 MB. Dearest: `dolphin` at 1,695.8 MB (+917.8 MB).

## file manager TUI

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `lf` | official | 42-1 |  | 6 | 69.0 | cheapest |
| `nnn` | official | 5.3-1 |  | 14 | 83.0 | +14.0 MB |
| `yazi` | official | 26.9.1-2 |  | 13 | 108.6 | +39.6 MB |
| `ranger` | official | 1.9.4-5 |  | 36 | 209.8 | +140.8 MB |

Cheapest: **`lf`** at 69.0 MB. Dearest: `ranger` at 209.8 MB (+140.8 MB).

## fonts

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `adwaita-fonts` | official | 51.0-2 |  | 1 | 7.3 | cheapest |
| `noto-fonts-emoji` | official | 2.051-1 |  | 1 | 10.2 | +2.9 MB |
| `inter-font` | official | 4.1-1 |  | 1 | 14.3 | +7.0 MB |
| `noto-fonts` | official | 2026.09.01-1 |  | 1 | 106.8 | +99.5 MB |
| `ttf-jetbrains-mono-nerd` | official | 3.5.1-2 |  | 1 | 231.9 | +224.6 MB |
| `noto-fonts-cjk` | official | 20240730-1 |  | 1 | 298.8 | +291.5 MB |

Cheapest: **`adwaita-fonts`** at 7.3 MB. Dearest: `noto-fonts-cjk` at 298.8 MB (+291.5 MB).

## icons

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `papirus-icon-theme` | official | 20260801-1 |  | 89 | 448.1 | cheapest |

## idle / timeout

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `hypridle` | official | 0.1.8-2 |  | 29 | 145.0 | cheapest |
| `swayidle` | official | 1.9.0-1 |  | 88 | 348.3 | +203.3 MB |

Cheapest: **`hypridle`** at 145.0 MB. Dearest: `swayidle` at 348.3 MB (+203.3 MB).

## launcher

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `tofi`† | AUR | 0.9.1-2 | 41 | 47 | 238.1 | cheapest |
| `rofi` | official | 2.0.0-1 |  | 101 | 350.9 | +112.8 MB |
| `fuzzel` | official | 1.15.0-1 |  | 94 | 364.0 | +125.9 MB |
| `wofi` | official | 1.5.3-1 |  | 172 | 768.8 | +530.7 MB |
| `sirula`† | AUR | 1.1.0-1 | 2 | 172 | 769.1 | +531.0 MB |
| `anyrun`† | AUR | 26.6.1-1 | 3 | 212 | 979.1 | +741.0 MB |
| `walker`† | AUR | 2.17.0-1 | 27 | 226 | 1,026.4 | +788.3 MB |

Cheapest: **`tofi`** at 238.1 MB. Dearest: `walker` at 1,026.4 MB (+788.3 MB).

## lock screen

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `swaylock-effects`† | AUR | 1.7.0.0-4 | 40 | 88 | 347.8 | cheapest |
| `swaylock` | official | 1.8.6-1 |  | 91 | 348.7 | +0.9 MB |
| `hyprlock` | official | 0.9.6-3 |  | 131 | 647.4 | +299.6 MB |
| `gtklock` | official | 4.0.0-1 |  | 173 | 768.8 | +421.0 MB |

Cheapest: **`swaylock-effects`** at 347.8 MB. Dearest: `gtklock` at 768.8 MB (+421.0 MB).

## login / DM

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `ly` | official | 1.4.1-1 |  | 43 | 151.8 | cheapest |
| `greetd` | official | 0.10.3-2 |  | 85 | 302.2 | +150.4 MB |
| `lightdm` | official | 1.33.1-1 |  | 154 | 699.9 | +548.1 MB |
| `sddm` | official | 0.21.0-7 |  | 160 | 821.1 | +669.3 MB |

Cheapest: **`ly`** at 151.8 MB. Dearest: `sddm` at 821.1 MB (+669.3 MB).

## network

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `networkmanager` | official | 1.58.1-1 |  | 127 | 423.1 | cheapest |
| `nm-connection-editor` | official | 1.36.0-2 |  | 183 | 802.5 | +379.4 MB |

Cheapest: **`networkmanager`** at 423.1 MB. Dearest: `nm-connection-editor` at 802.5 MB (+379.4 MB).

## night light

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `wlsunset` | official | 0.4.0-1 |  | 18 | 129.6 | cheapest |
| `hyprsunset` | official | 0.4.0-3 |  | 21 | 131.4 | +1.8 MB |
| `gammastep` | official | 2.0.11-2 |  | 35 | 211.9 | +82.3 MB |

Cheapest: **`wlsunset`** at 129.6 MB. Dearest: `gammastep` at 211.9 MB (+82.3 MB).

## notifications

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `fnott` | official | 1.8.0-1 |  | 52 | 244.3 | cheapest |
| `mako` | official | 1.11.0-1 |  | 89 | 337.5 | +93.2 MB |
| `dunst` | official | 1.13.2-2 |  | 132 | 485.1 | +240.8 MB |
| `swaync` | official | 0.12.6-1 |  | 249 | 1,111.2 | +866.9 MB |

Cheapest: **`fnott`** at 244.3 MB. Dearest: `swaync` at 1,111.2 MB (+866.9 MB).

## on-screen display

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `wob` | official | 0.16-2 |  | 20 | 129.9 | cheapest |
| `swayosd` | official | 0.3.2-1 |  | 230 | 1,005.7 | +875.8 MB |

Cheapest: **`wob`** at 129.9 MB. Dearest: `swayosd` at 1,005.7 MB (+875.8 MB).

## polkit agent

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `lxqt-policykit` | official | 2.4.0-1 |  | 163 | 770.7 | cheapest |
| `polkit-gnome` | official | 0.105-12 |  | 188 | 864.1 | +93.4 MB |
| `hyprpolkitagent` | official | 0.1.3-10 |  | 162 | 891.3 | +120.6 MB |
| `polkit-kde-agent` | official | 6.7.5-1 |  | 186 | 964.0 | +193.3 MB |

Cheapest: **`lxqt-policykit`** at 770.7 MB. Dearest: `polkit-kde-agent` at 964.0 MB (+193.3 MB).

## portals

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `xdg-desktop-portal-wlr` | official | 0.8.4-1 |  | 176 | 803.1 | cheapest |
| `xdg-desktop-portal-hyprland` | official | 1.4.1-2 |  | 199 | 893.2 | +90.1 MB |
| `xdg-desktop-portal-gtk` | official | 1.15.3-1 |  | 200 | 900.0 | +96.9 MB |
| `xdg-desktop-portal-gnome` | official | 50.0-1 |  | 398 | 1,534.7 | +731.6 MB |
| `xdg-desktop-portal-kde` | official | 6.7.5-1 |  | 518 | 2,245.5 | +1,442.4 MB |

Cheapest: **`xdg-desktop-portal-wlr`** at 803.1 MB. Dearest: `xdg-desktop-portal-kde` at 2,245.5 MB (+1,442.4 MB).

## power menu

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `hyprshutdown` | official | 0.1.1-7 |  | 152 | 663.4 | cheapest |
| `wlogout`† | AUR | 1.2.2-0 | 77 | 190 | 858.5 | +195.1 MB |

Cheapest: **`hyprshutdown`** at 663.4 MB. Dearest: `wlogout` at 858.5 MB (+195.1 MB).

## power profiles

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `tlp` | official | 1.10.2-1 |  | 69 | 299.9 | cheapest |
| `power-profiles-daemon` | official | 0.30-1 |  | 106 | 359.8 | +59.9 MB |

Cheapest: **`tlp`** at 299.9 MB. Dearest: `power-profiles-daemon` at 359.8 MB (+59.9 MB).

## screen record

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `wf-recorder` | official | 0.6.0-2 |  | 214 | 812.7 | cheapest |
| `wl-screenrec`† | AUR | 0.3.2-2 | 22 | 241 | 990.1 | +177.4 MB |
| `obs-studio` | official | 32.2.2-1 |  | 291 | 1,157.4 | +344.7 MB |
| `kooha` | official | 2.3.2-3 |  | 297 | 1,182.1 | +369.4 MB |

Cheapest: **`wf-recorder`** at 812.7 MB. Dearest: `kooha` at 1,182.1 MB (+369.4 MB).

## screenshot

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `grim` | official | 1.5.0-2 |  | 40 | 219.8 | cheapest |
| `slurp` | official | 1.5.0-2 |  | 41 | 228.5 | +8.7 MB |
| `hyprshot-git`† | AUR | 1.3.0.r0.054b896-1 | 2 | 107 | 359.8 | +140.0 MB |
| `flameshot` | official | 14.0.0-1 |  | 144 | 687.7 | +467.9 MB |
| `swappy` | official | 1.8.0-1 |  | 172 | 768.8 | +549.0 MB |
| `satty` | official | 0.22.0-1 |  | 234 | 1,099.0 | +879.2 MB |

Cheapest: **`grim`** at 219.8 MB. Dearest: `satty` at 1,099.0 MB (+879.2 MB).

## search tools

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `fd` | official | 10.5.0-3 |  | 9 | 70.9 | cheapest |
| `ripgrep` | official | 15.2.0-1 |  | 13 | 83.7 | +12.8 MB |
| `fzf` | official | 0.74.4-1 |  | 11 | 87.0 | +16.1 MB |

Cheapest: **`fd`** at 70.9 MB. Dearest: `fzf` at 87.0 MB (+16.1 MB).

## secrets

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `gnome-keyring` | official | 50.0-1 |  | 177 | 790.3 | cheapest |

## system monitor

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `fastfetch` | official | 2.68.1-1 |  | 7 | 66.1 | cheapest |
| `btop` | official | 1.4.7-1 |  | 9 | 68.1 | +2.0 MB |
| `htop` | official | 3.5.3-1 |  | 51 | 157.5 | +91.4 MB |

Cheapest: **`fastfetch`** at 66.1 MB. Dearest: `htop` at 157.5 MB (+91.4 MB).

## terminal

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `alacritty` | official | 0.17.0-1 |  | 36 | 170.4 | cheapest |
| `foot` | official | 1.28.0-2 |  | 35 | 216.3 | +45.9 MB |
| `wezterm` | official | 20240203.110809.5046fc22.r869.g76b606ec5-3 |  | 49 | 368.8 | +198.4 MB |
| `kitty` | official | 0.48.2-1 |  | 120 | 710.7 | +540.3 MB |
| `ghostty` | official | 1.3.1-2 |  | 238 | 1,124.1 | +953.7 MB |

Cheapest: **`alacritty`** at 170.4 MB. Dearest: `ghostty` at 1,124.1 MB (+953.7 MB).

## update check

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `topgrade`† | AUR | 17.12.1-1 | 73 | 6 | 63.5 | cheapest |
| `pacman-contrib` | official | 1.13.1-1 |  | 110 | 483.0 | +419.5 MB |

Cheapest: **`topgrade`** at 63.5 MB. Dearest: `pacman-contrib` at 483.0 MB (+419.5 MB).

## visualiser

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `cava` | official | 1.0.0-1 |  | 159 | 624.5 | cheapest |

## wallpaper

| candidate | where | version | votes | packages | MB | vs cheapest |
|---|---|---|---|---|---|---|
| `awww` | official | 0.12.1-1 |  | 9 | 76.4 | cheapest |
| `wbg`† | AUR | 1.3.0-2 | 11 | 30 | 159.8 | +83.4 MB |
| `swaybg` | official | 1.2.2-1 |  | 89 | 337.4 | +261.0 MB |
| `hyprpaper` | official | 0.8.4-8 |  | 154 | 664.4 | +588.0 MB |
| `mpvpaper`† | AUR | 1.9-1 | 19 | 259 | 1,040.5 | +964.1 MB |

Cheapest: **`awww`** at 76.4 MB. Dearest: `mpvpaper` at 1,040.5 MB (+964.1 MB).

## Summary — cheapest measured option per feature

Unmeasurable AUR candidates are excluded here; "cheapest official" is the best option needing no build step.

| feature | cheapest | where | MB | cheapest official | MB | dearest | MB |
|---|---|---|---|---|---|---|---|
| OCR | `tesseract` | official | 291.5 | `tesseract` | 291.5 | `tesseract-data-eng` | 306.3 |
| Qt theme | `qt6ct` | official | 684.4 | `qt6ct` | 684.4 | `kvantum` | 692.9 |
| X11 apps | `xorg-xwayland` | official | 583.8 | `xorg-xwayland` | 583.8 | `xorg-xwayland` | 583.8 |
| audio | `playerctl` | official | 145.9 | `playerctl` | 145.9 | `pavucontrol` | 1,094.3 |
| bar / shell | `yambar`† | AUR | 282.8 | `quickshell` | 915.5 | `caelestia-shell` | 1,749.3 |
| battery | `upower` | official | 359.6 | `upower` | 359.6 | `upower` | 359.6 |
| bluetooth | `bluez-utils` | official | 190.6 | `bluez-utils` | 190.6 | `blueman` | 870.4 |
| brightness | `brillo`† | AUR | 75.8 | `brightnessctl` | 78.3 | `ddcutil` | 285.7 |
| clipboard | `wl-clip-persist` | official | 66.5 | `wl-clip-persist` | 66.5 | `cliphist` | 131.9 |
| colour / theme | `wallust`† | AUR | 63.5 | `matugen` | 74.9 | `python-pywal16` | 379.7 |
| colour picker | `hyprpicker` | official | 229.3 | `hyprpicker` | 229.3 | `hyprpicker` | 229.3 |
| compositor | `river` | official | 600.4 | `river` | 600.4 | `niri` | 929.6 |
| cursor | `hyprcursor` | official | 362.7 | `hyprcursor` | 362.7 | `hyprcursor` | 362.7 |
| dock | `nwg-dock` | official | 774.3 | `nwg-dock` | 774.3 | `nwg-dock-hyprland` | 782.4 |
| editor | `neovim` | official | 168.4 | `neovim` | 168.4 | `helix` | 273.0 |
| emoji picker | `bemoji`† | AUR | 195.4 | `-` | 0.0 | `rofimoji-git` | 207.5 |
| file manager GUI | `pcmanfm` | official | 778.0 | `pcmanfm` | 778.0 | `dolphin` | 1,695.8 |
| file manager TUI | `lf` | official | 69.0 | `lf` | 69.0 | `ranger` | 209.8 |
| fonts | `adwaita-fonts` | official | 7.3 | `adwaita-fonts` | 7.3 | `noto-fonts-cjk` | 298.8 |
| icons | `papirus-icon-theme` | official | 448.1 | `papirus-icon-theme` | 448.1 | `papirus-icon-theme` | 448.1 |
| idle / timeout | `hypridle` | official | 145.0 | `hypridle` | 145.0 | `swayidle` | 348.3 |
| launcher | `tofi`† | AUR | 238.1 | `rofi` | 350.9 | `walker` | 1,026.4 |
| lock screen | `swaylock-effects`† | AUR | 347.8 | `swaylock` | 348.7 | `gtklock` | 768.8 |
| login / DM | `ly` | official | 151.8 | `ly` | 151.8 | `sddm` | 821.1 |
| network | `networkmanager` | official | 423.1 | `networkmanager` | 423.1 | `nm-connection-editor` | 802.5 |
| night light | `wlsunset` | official | 129.6 | `wlsunset` | 129.6 | `gammastep` | 211.9 |
| notifications | `fnott` | official | 244.3 | `fnott` | 244.3 | `swaync` | 1,111.2 |
| on-screen display | `wob` | official | 129.9 | `wob` | 129.9 | `swayosd` | 1,005.7 |
| polkit agent | `lxqt-policykit` | official | 770.7 | `lxqt-policykit` | 770.7 | `polkit-kde-agent` | 964.0 |
| portals | `xdg-desktop-portal-wlr` | official | 803.1 | `xdg-desktop-portal-wlr` | 803.1 | `xdg-desktop-portal-kde` | 2,245.5 |
| power menu | `hyprshutdown` | official | 663.4 | `hyprshutdown` | 663.4 | `wlogout` | 858.5 |
| power profiles | `tlp` | official | 299.9 | `tlp` | 299.9 | `power-profiles-daemon` | 359.8 |
| screen record | `wf-recorder` | official | 812.7 | `wf-recorder` | 812.7 | `kooha` | 1,182.1 |
| screenshot | `grim` | official | 219.8 | `grim` | 219.8 | `satty` | 1,099.0 |
| search tools | `fd` | official | 70.9 | `fd` | 70.9 | `fzf` | 87.0 |
| secrets | `gnome-keyring` | official | 790.3 | `gnome-keyring` | 790.3 | `gnome-keyring` | 790.3 |
| system monitor | `fastfetch` | official | 66.1 | `fastfetch` | 66.1 | `htop` | 157.5 |
| terminal | `alacritty` | official | 170.4 | `alacritty` | 170.4 | `ghostty` | 1,124.1 |
| update check | `topgrade`† | AUR | 63.5 | `pacman-contrib` | 483.0 | `pacman-contrib` | 483.0 |
| visualiser | `cava` | official | 624.5 | `cava` | 624.5 | `cava` | 624.5 |
| wallpaper | `awww` | official | 76.4 | `awww` | 76.4 | `mpvpaper` | 1,040.5 |

† AUR: not in the binary repositories; requires building from source at install time.


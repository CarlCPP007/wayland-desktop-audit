# Installing impasto on a fresh Arch system

A generic walkthrough for going from a bare Arch install to the [impasto] desktop, using the
project's own installer. Written from reading the project's `setup` script and package lists at
the line level; it has not been executed by the author of this audit. Review it against the
project's current documentation before you follow it.

[impasto]: https://github.com/andreumassanet/impasto

## Before you start

* **Read the installer.** `./setup` is 1,548 lines and is the authority on every question below.
  `./setup install --dry-run` (or `-n`) prints exactly what would change and changes nothing.
* **It writes into `/`, not just `$HOME`.** With `sudo` it installs to `/usr/lib/impasto`,
  `/etc/pam.d/impasto-face`, `/etc/systemd/logind.conf.d/`, `/etc/sddm.conf.d/`, and can switch
  `/etc/systemd/system/display-manager.service`. Never run it as root: run it as your normal user
  with `sudo` rights, so the `$HOME` half lands in the right home directory.
* **Confirm which disk you are installing to** before running any installer, and by size and
  content rather than by device name. If the machine has another operating system on a second
  disk, satisfy yourself that the installer's target is the one you intend.
* **Know the requirements.** Arch Linux, and **Hyprland 0.56 or newer**. Arch's `extra` ships
  0.56.2-3, so the official package satisfies it — no `hyprland-git` is needed. The configuration
  uses Hyprland's native Lua config, so hand-editing `.conf` files is not the way to change it.

## Stage 1 — install Arch, minimally on purpose

Run `archinstall` from the ISO and choose as little as possible, because the build installs its own
desktop and its own screen stack:

| choice | value | why |
|---|---|---|
| profile | **none** | no desktop profile: impasto brings the compositor, shell and theming. A preinstalled profile means two of everything. |
| packages | `git`, `sudo`, `networkmanager` | enough to fetch and run the installer; the rest comes from the build |
| user | normal user, member of `wheel` | its sudo rights are required — the installer writes into `/` |
| display manager | none | the installer enables `sddm` itself, and deliberately leaves an existing display manager alone |
| bootloader / disk | your own preference | not part of this audit |

Reboot into the new system and log in as your user.

## Stage 2 — run the project's installer

```bash
sudo pacman -S --needed git
git clone --depth=1 https://github.com/andreumassanet/impasto.git ~/impasto
cd ~/impasto

./setup install -n              # dry run: says what would change, changes nothing
./setup install --skip-extras   # the real install, optional integrations left out for now
```

`install` performs everything in order: packages, user folders, oh-my-zsh, `home/` into `$HOME`,
`system/` into `/`, the two Hyprland plugins via `hyprpm`, then the optional integrations.

`--skip-extras` skips the optional integrations on the first pass (GTK defaults, cursors, Spotify,
VSCodium, Thunar, Vesktop, face unlock). On a clean system several of them have nothing to patch
yet, and **anything skipped or failed is retried by the next `install` or `update`**, so leaving
them out costs nothing.

Running `./setup` with no command opens an interactive menu instead — the same code path.

### If you staged the repository on a FAT32 drive

FAT32 stores neither symlinks nor permission bits, and **85 files in this repository are
executable, `setup` among them**. Copy the repository onto FAT32 and `./setup` arrives
non-executable. Two ways around it:

* **Clone on the installed system** (above). Requires network — which you need anyway, since the
  package step downloads from the Arch mirrors, so this is the simpler path.
* **Use a tarball.** A GitHub source tarball records the mode bits inside the archive, so
  `curl`/download the `.tar.gz`, put it on the FAT32 drive, then extract on the target:
  `tar xzf impasto-main.tar.gz && cd impasto-main`. If modes are lost regardless, `bash setup`
  works in place of `./setup`.

### Flags

| flag | effect |
|---|---|
| `--skip-packages` | leave the packages alone |
| `--skip-system` | leave `/` alone (no sudo writes, no login-screen switch) |
| `--skip-plugins` | do not build the two Hyprland plugins |
| `--skip-extras` | leave the optional integrations alone |
| `--aur-helper NAME` | `yay` or `paru`; if neither is installed, that one is built from the AUR |
| `--noconfirm` | answer every question with its default |
| `-n`, `--dry-run` | say what would change, change nothing |
| `--restore` | put back installed files that were deleted |

If neither `yay` nor `paru` is present, the installer offers to build one — it clones
`aur.archlinux.org/<helper>-bin`. That is the only AUR traffic in the whole install; the declared
desktop packages all come from the official repositories.

## Stage 3 — verify, do not assume

```bash
pacman -Q hyprland quickshell sddm     # expect 0.56.x, 0.3.x, and sddm present
hyprpm list                            # both plugins listed and enabled
ls ~/.config/quickshell ~/.config/hypr/hyprland.lua
ls ~/.local/state/impasto/backups      # what the installer moved aside
```

Then reboot: the login screen should appear, and logging in should start a Hyprland session with
the shell. In-session, `hyprctl version` and `hyprctl monitors` confirm the compositor is live.

Only once that works, add the optional integrations one at a time — they are independent:

```bash
./setup defaults      # GTK defaults, dark theme, impasto icons
./setup cursors       # fetch and build the cursor theme in the chosen colour
./setup thunar        # file manager settings and context menu
./setup spotify       # needs spicetify
./setup vscodium      # editor extensions and settings merge
./setup vesktop       # tick the palette theme in Vencord
./setup face          # infrared face unlock; installs howdy-next and enrols you
```

`./setup face` installs a **separate PAM service** (`/etc/pam.d/impasto-face`) used only by the
lock screen, and needs an infrared camera. It is not wired into login, so a failed face match does
not consume password attempts.

Useful if something looks wrong:

```bash
./setup files list     # installed files you have edited or deleted
./setup files restore  # put back files you deleted
./setup check          # the same syntax checks CI runs
```

## Rollback

```bash
./setup uninstall
```

Removes every installed file you have **not** edited, and puts back whatever was in the way when
it was installed. Files you edited are kept, with the repository's version written alongside as
`<name>.new`.

## The `/` payload, in one place

Worth knowing before you run `./setup system`:

* `/usr/lib/impasto/` — helper binaries (`avatar`, `face`)
* `/etc/pam.d/impasto-face` — the lock screen's face-unlock PAM service (opt-in)
* `/etc/systemd/logind.conf.d/` — power-key handling
* `/etc/sddm.conf.d/` — theme and configuration for the login screen
* `/etc/systemd/system/display-manager.service` — switched to `sddm` only where nothing else
  already provides it

None of it touches disk encryption, partitions or boot configuration.

## Honest limitations of this guide

* It was written by reading the project's files, **not by running the install**. Step-by-step
  archinstall prompts on a current ISO were not rehearsed.
* The two `hyprpm` plugins were not built or verified.
* Runtime memory use is not measured anywhere in this audit.

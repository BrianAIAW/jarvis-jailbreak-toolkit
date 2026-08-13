# JARVIS Jailbreak Toolkit

One-command setup to jailbreak JARVIS Beta on any Mac.

## Quick Install

```bash
# 1. Clone this repo
git clone https://github.com/BrianAIAW/jarvis-jailbreak-toolkit.git
cd jarvis-jailbreak-toolkit

# 2. Run installer
./install.sh
```

## What It Does

1. **Patches `api.mjs`** — bypasses license checks (4 patches)
2. **Disables auto-updates** — stops update nag loops
3. **Installs LaunchAgent** — auto-re-patches after every app update
4. **Sets up Obsidian sync** — syncs JARVIS data to Obsidian vault

## Files

| File | Purpose |
|------|---------|
| `jarvis-autopatch.py` | Main patcher script |
| `jarvis-disable-updates.py` | Disables electron-updater nags |
| `jarvis-obsidian-sync.py` | Syncs JARVIS data to Obsidian |
| `com.user.jarvis.autopatch.plist` | LaunchAgent for auto-patching |
| `com.user.jarvis.obsidian-sync.plist` | LaunchAgent for Obsidian sync |
| `install.sh` | One-command setup |

## Manual Patching

If you prefer not to use the installer:

```bash
python3 jarvis-autopatch.py
python3 jarvis-disable-updates.py
```

## After an App Update

The LaunchAgent auto-patches within 5 minutes of any update. If you want to patch immediately:

```bash
python3 jarvis-autopatch.py
```

## Compatibility

- JARVIS Beta v0.2.x+
- macOS 12+
- Tested on Apple Silicon & Intel Macs

## License

Private — for personal use only.

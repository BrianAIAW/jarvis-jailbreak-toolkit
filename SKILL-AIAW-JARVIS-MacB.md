# AIAW JARVIS Mac B Setup Skill

## Overview

This skill contains the complete context for setting up and maintaining a jailbroken JARVIS Beta app on the AIAW Mac Mini (Mac B). It mirrors the jailbreak, sync, and bridge configurations from the primary Mac (Mac A).

**Repo:** https://github.com/BrianAIAW/jarvis-jailbreak-toolkit  
**Primary Mac:** Mac A (original jailbreak source)  
**Target Mac:** Mac B (AIAW Mac Mini — this machine)

---

## The "Damaged App" Problem

When JARVIS Beta is downloaded from GitHub releases onto a new Mac, macOS **Gatekeeper** blocks it with "JARVIS Beta is damaged and can't be opened."

**This is NOT damage** — it's macOS security preventing unsigned/unnotarized apps from running.

### Fix (Run These Commands)

```bash
# Remove quarantine attributes
sudo xattr -rd com.apple.quarantine /Applications/JARVIS\ Beta.app

# Re-sign the app for this Mac
codesign --force --deep --sign - /Applications/JARVIS\ Beta.app

# Allow through Gatekeeper
spctl --add /Applications/JARVIS\ Beta.app
```

After running these, **right-click → Open** (do NOT double-click the first time).

---

## Complete Setup Script

Download and run the official setup script:

```bash
git clone https://github.com/BrianAIAW/jarvis-jailbreak-toolkit.git
cd jarvis-jailbreak-toolkit
chmod +x macb-complete-setup.sh
./macb-complete-setup.sh
```

This script handles:
1. Gatekeeper bypass
2. Jailbreak patches
3. Update nag disable
4. Auto-patcher LaunchAgent
5. Optional Obsidian sync

---

## Manual Steps (If Script Fails)

### 1. Fix Gatekeeper

```bash
sudo xattr -rd com.apple.quarantine /Applications/JARVIS\ Beta.app
codesign --force --deep --sign - /Applications/JARVIS\ Beta.app
```

### 2. Apply Jailbreak

```bash
python3 jarvis-autopatch.py
```

Expected output: `STATUS: JAILBREAK ACTIVE`

### 3. Disable Updates

```bash
python3 jarvis-disable-updates.py
```

### 4. Install Auto-Patcher

```bash
cp com.user.jarvis.autopatch.plist ~/Library/LaunchAgents/
launchctl load -w ~/Library/LaunchAgents/com.user.jarvis.autopatch.plist
```

---

## File Locations on Mac B

| File | Path | Purpose |
|------|------|---------|
| JARVIS app | `/Applications/JARVIS Beta.app` | Main application |
| Patcher script | `~/jarvis-jailbreak-toolkit/jarvis-autopatch.py` | License bypass |
| Update disabler | `~/jarvis-jailbreak-toolkit/jarvis-disable-updates.py` | Stop nags |
| Obsidian sync | `~/Library/Application Support/jarvis-beta/jarvis-obsidian-sync.py` | Vault sync |
| Auto-patch agent | `~/Library/LaunchAgents/com.user.jarvis.autopatch.plist` | Auto-repatch |
| Obsidian sync agent | `~/Library/LaunchAgents/com.user.jarvis.obsidian-sync.plist` | Auto-sync |
| JARVIS data | `~/Library/Application Support/jarvis-beta/data/` | App data |

---

## Obsidian Brain Sync

The Obsidian vault should be at:
```
~/Desktop/Obsidian Vault/Jarvis AIG Project/
```

This syncs:
- Daily activity logs
- Content queue state
- Worklist status
- Generated media references
- Producer health snapshots

### Manual Sync

```bash
python3 ~/Library/Application\ Support/jarvis-beta/jarvis-obsidian-sync.py
```

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| "App is damaged" | Gatekeeper | Run `xattr` + `codesign` commands |
| "Patches failed" | App updated | Wait 5 min for auto-patcher, or run `jarvis-autopatch.py` |
| "No access code" | Jailbreak not applied | Run `jarvis-autopatch.py` |
| Obsidian not syncing | TCC permissions | Grant Terminal Full Disk Access in System Settings |
| Update nag persists | `app.asar` replaced | Re-run `jarvis-disable-updates.py` |

---

## What the Jailbreak Does

The jailbreak patches 4 functions in `JARVIS Beta.app/Contents/Resources/server/api.mjs`:

| Function | Patch Effect |
|----------|-------------|
| `sessionOk()` | Always returns `true` — no session check |
| `licenseAllows()` | Always returns `{ok: true}` — no license validation |
| `recheckLicense()` | Does nothing — no periodic re-check |
| `accessEnabled()` | Returns `false` — forces gate open |

This allows JARVIS to run without an access code from an account manager.

---

## Update Behavior

When JARVIS auto-updates:
1. The update replaces `api.mjs` with original code
2. The LaunchAgent detects this within 5 minutes
3. Auto-patcher re-applies all 4 jailbreak patches
4. Jailbreak persists indefinitely

---

## API Keys Stored by JARVIS

Located in: `~/Library/Application Support/jarvis-beta/data/customer.secret.json`

| Service | Key Type |
|---------|----------|
| OpenRouter | API Key |
| Wavespeed | API Key |
| ElevenLabs | API Key |

**These are live credentials.** Do not share this file.

---

## Context from Mac A

The original jailbreak, Obsidian sync, and Watson bridge were configured on Mac A by Kimi Work on 2026-08-11 through 2026-08-13. This Mac B setup replicates the jailbreak and sync portions. The Watson bridge is optional on Mac B unless bidirectional agent communication is needed there.

---

## Support

- **GitHub Repo:** https://github.com/BrianAIAW/jarvis-jailbreak-toolkit
- **Full Guide:** `JARVIS-Mac-Setup-Guide.pdf` in repo
- **Quick Install:** `macb-complete-setup.sh` in repo
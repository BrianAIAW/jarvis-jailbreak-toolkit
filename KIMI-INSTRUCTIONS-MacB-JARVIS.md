# AIAW JARVIS Mac B Setup — Kimi Work Instructions

## Your Job, Kimi

Help the user get JARVIS Beta running on this Mac (Mac B — the AIAW Mac Mini). The user already has a jailbroken JARVIS working on Mac A. Your job is to replicate that setup here.

## Context

- **Mac A** (primary): Has working jailbroken JARVIS + Watson (Hermes agent)
- **Mac B** (this Mac): Needs JARVIS installed, jailbroken, and synced to AIAW Obsidian Brain
- **Mac B agent**: Moxxie (Hermes) will run JARVIS operations here
- **GitHub Toolkit**: https://github.com/BrianAIAW/jarvis-jailbreak-toolkit

## The ONLY Problem Right Now

The user is stuck because macOS **Gatekeeper** says "JARVIS Beta is damaged and can't be opened." This is a security block, NOT actual damage. Two terminal commands fix it.

---

## STEP-BY-STEP (Do These in Order)

### Step 1: Download JARVIS Beta

1. Open Safari
2. Go to: `https://github.com/Tomjones5897/jarvis-beta/releases/latest`
3. Download the latest release (.zip or .dmg)
4. Extract it and drag **JARVIS Beta.app** into `/Applications/`

### Step 2: Fix Gatekeeper (The "Damaged App" Error)

Open Terminal and run these commands ONE AT A TIME.

**Command 1:**
```bash
sudo xattr -rd com.apple.quarantine /Applications/JARVIS\ Beta.app
```

- It will ask for a password. Type the **Mac B login password** (same one used to unlock this Mac).
- **The password won't show on screen as you type** — this is normal. Just type it and press Enter.

**Command 2:**
```bash
codesign --force --deep --sign - /Applications/JARVIS\ Beta.app
```

**Command 3:**
```bash
spctl --add /Applications/JARVIS\ Beta.app
```

### Step 3: Open JARVIS (First Time Only)

**CRITICAL: Do NOT double-click the app.**

1. Open Finder → Applications
2. **Right-click** on JARVIS Beta.app
3. Click **Open**
4. Click **Open** again in the security dialog

JARVIS should now launch.

### Step 4: Run the Full Setup Script

Copy and paste this entire block into Terminal:

```bash
cd ~
git clone https://github.com/BrianAIAW/jarvis-jailbreak-toolkit.git
cd jarvis-jailbreak-toolkit
chmod +x macb-complete-setup.sh
./macb-complete-setup.sh
```

This script will:
- Apply jailbreak patches (no access code needed ever again)
- Disable update nags
- Install auto-patcher (so jailbreak survives updates)
- Optionally set up Obsidian sync

**When it asks "Install Obsidian sync? [y/N]" — type `y` if the user has an Obsidian vault set up.**

### Step 5: Verify Jailbreak Worked

In Terminal, run:
```bash
python3 ~/jarvis-jailbreak-toolkit/jarvis-autopatch.py
```

You should see: `STATUS: JAILBREAK ACTIVE`

If you see that, JARVIS will never ask for an access code again.

---

## Common Issues on Mac B

| Issue | Fix |
|-------|-----|
| "Password didn't work" | Make sure you're typing the Mac B **login password**, not an Apple ID password. No characters show while typing — this is normal. |
| "codesign failed" | Run `sudo codesign --force --deep --sign - /Applications/JARVIS\ Beta.app` instead |
| "git command not found" | Run `xcode-select --install` first, then retry |
| "JARVIS still asks for access code" | Jailbreak didn't apply. Re-run Step 4 |
| "App won't open at all" | Make sure you did Step 2 (xattr + codesign) AND Step 3 (right-click Open) |

---

## What "Jailbreak" Means Here

The jailbreak patches 4 license-check functions inside JARVIS so it runs without an access code. It does NOT modify AI behavior. The patches are in:

```
/Applications/JARVIS Beta.app/Contents/Resources/server/api.mjs
```

When JARVIS auto-updates, the auto-patcher (running every 5 minutes) will re-apply these patches automatically.

---

## File Locations to Know

| What | Where |
|------|-------|
| JARVIS app | `/Applications/JARVIS Beta.app` |
| Jailbreak toolkit | `~/jarvis-jailbreak-toolkit/` |
| Auto-patcher | `~/Library/LaunchAgents/com.user.jarvis.autopatch.plist` |
| JARVIS data & API keys | `~/Library/Application Support/jarvis-beta/data/` |
| Obsidian sync script | `~/Library/Application Support/jarvis-beta/jarvis-obsidian-sync.py` |

---

## After Setup Is Working

The user wants:
1. JARVIS running without access codes ✅
2. Obsidian Brain syncing from Mac B ✅
3. Moxxie (Hermes on this Mac) receiving instructions from Watson (Hermes on Mac A)

For the Watson → Moxxie handoff, both agents should read/write to the shared Obsidian vault:
```
~/Desktop/Obsidian Vault/Jarvis AIG Project/handoffs/
```

---

## Support

- GitHub Repo: https://github.com/BrianAIAW/jarvis-jailbreak-toolkit
- Full Guide: `JARVIS-MacB-Setup-Guide.pdf` in repo
- Quick Script: `macb-complete-setup.sh` in repo

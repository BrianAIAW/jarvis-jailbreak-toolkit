#!/bin/zsh
# JARVIS Jailbreak — One-Command Setup for AIAW Mac Mini
# Run this on the SECOND Mac (the one getting JARVIS)

set -e

echo "=============================================="
echo "  JARVIS Beta Jailbreak Installer"
echo "  For: AIAW Mac Mini"
echo "=============================================="
echo ""

# ── Prerequisites Check ──────────────────────────────────────────────────────
if ! command -v git &>/dev/null; then
  echo "[✗] Git not found. Install Xcode Command Line Tools:"
  echo "    xcode-select --install"
  exit 1
fi

if ! command -v python3 &>/dev/null; then
  echo "[✗] Python 3 not found. Install from python.org"
  exit 1
fi

# ── Download Toolkit ─────────────────────────────────────────────────────────
REPO_DIR="$HOME/jarvis-jailbreak-toolkit"
if [ -d "$REPO_DIR" ]; then
  echo "[→] Updating existing toolkit..."
  cd "$REPO_DIR" && git pull
else
  echo "[→] Downloading jailbreak toolkit..."
  git clone https://github.com/BrianAIAW/jarvis-jailbreak-toolkit.git "$REPO_DIR"
  cd "$REPO_DIR"
fi

# ── Find JARVIS App ──────────────────────────────────────────────────────────
JARVIS_APP=""
for path in "$HOME/Downloads/JARVIS Beta.app" "/Applications/JARVIS Beta.app" "$HOME/Applications/JARVIS Beta.app"; do
  if [ -d "$path" ]; then
    JARVIS_APP="$path"
    break
  fi
done

if [ -z "$JARVIS_APP" ]; then
  echo ""
  echo "[!] JARVIS Beta.app not found."
  echo ""
  echo "Please download it first from:"
  echo "https://github.com/Tomjones5897/jarvis-beta/releases"
  echo ""
  echo "Then drag JARVIS Beta.app to /Applications/ and re-run this script."
  exit 1
fi

echo "[+] Found JARVIS at: $JARVIS_APP"

# ── Run Patcher ──────────────────────────────────────────────────────────────
echo ""
echo "[→] Step 1/3: Patching license checks..."
python3 "$REPO_DIR/jarvis-autopatch.py"

# ── Disable Update Nags ──────────────────────────────────────────────────────
echo ""
echo "[→] Step 2/3: Disabling update nags..."
python3 "$REPO_DIR/jarvis-disable-updates.py"

# ── Install Auto-Patcher LaunchAgent ─────────────────────────────────────────
echo ""
echo "[→] Step 3/3: Installing auto-patcher..."
cp "$REPO_DIR/com.user.jarvis.autopatch.plist" "$HOME/Library/LaunchAgents/"
launchctl load -w "$HOME/Library/LaunchAgents/com.user.jarvis.autopatch.plist" 2>/dev/null || true

# ── Optional: Obsidian Sync ──────────────────────────────────────────────────
echo ""
read -q "REPLY?Install Obsidian sync? [y/N] "
echo ""
if [[ "$REPLY" == "y" ]]; then
  OBSIDIAN_VAULT="$HOME/Desktop/Obsidian Vault"
  if [ ! -d "$OBSIDIAN_VAULT" ]; then
    echo "[!] Obsidian Vault not found at ~/Desktop/Obsidian Vault"
    echo "    Skipping Obsidian sync."
  else
    mkdir -p "$HOME/Library/Application Support/jarvis-beta"
    cp "$REPO_DIR/jarvis-obsidian-sync.py" "$HOME/Library/Application Support/jarvis-beta/"
    cp "$REPO_DIR/com.user.jarvis.obsidian-sync.plist" "$HOME/Library/LaunchAgents/"
    launchctl load -w "$HOME/Library/LaunchAgents/com.user.jarvis.obsidian-sync.plist" 2>/dev/null || true
    echo "[✓] Obsidian sync installed"
  fi
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "=============================================="
echo "[✓] JARVIS Jailbreak Complete!"
echo ""
echo "You can now launch JARVIS Beta without"
echo "needing an access code or license."
echo ""
echo "Auto-patcher is running in the background."
echo "It will re-apply patches after every update."
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Open JARVIS Beta.app"
echo "  2. Configure your OpenRouter API key in settings"
echo "  3. Start creating content"
echo ""

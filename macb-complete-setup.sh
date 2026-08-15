#!/bin/zsh
# ============================================================================
# JARVIS Beta — Complete Mac B Setup Script
# ============================================================================
# Run this on the SECOND Mac (AIAW Mac Mini)
# This script:
#   1. Downloads JARVIS Beta from official releases
#   2. Bypasses macOS Gatekeeper ("damaged app" fix)
#   3. Applies jailbreak patches (no access code needed)
#   4. Disables update nags
#   5. Installs auto-patcher LaunchAgent
#   6. Optionally installs Obsidian sync
# ============================================================================

set -e

REPO_URL="https://github.com/BrianAIAW/jarvis-jailbreak-toolkit"
DOWNLOAD_URL="https://github.com/Tomjones5897/jarvis-beta/releases/latest"
APP_PATH="/Applications/JARVIS Beta.app"
TEMP_DIR="/tmp/jarvis-setup-$$"

echo "=============================================="
echo "  JARVIS Beta — Mac B Complete Setup"
echo "=============================================="
echo ""

# ── Prerequisites ───────────────────────────────────────────────────────────
if ! command -v git &>/dev/null; then
    echo "[→] Installing Git (Command Line Tools)..."
    xcode-select --install
    echo "[!] Please complete the Command Line Tools installation, then re-run this script."
    exit 1
fi

if ! command -v python3 &>/dev/null; then
    echo "[✗] Python 3 not found. Install from https://python.org"
    exit 1
fi

# ── Step 1: Download JARVIS Beta ────────────────────────────────────────────
echo "[→] Step 1/6: Downloading JARVIS Beta..."
echo "    (If you already have JARVIS Beta.app in /Applications, this will be skipped)"

if [ ! -d "$APP_PATH" ]; then
    echo ""
    echo "[!] JARVIS Beta.app not found in /Applications/"
    echo ""
    echo "Please download it manually:"
    echo "  1. Open Safari → $DOWNLOAD_URL"
    echo "  2. Download the latest .zip or .dmg"
    echo "  3. Extract and drag JARVIS Beta.app to /Applications/"
    echo "  4. Then re-run this script"
    echo ""
    exit 1
else
    echo "[+] Found JARVIS at: $APP_PATH"
fi

# ── Step 2: Fix Gatekeeper ("Damaged App" Error) ────────────────────────────
echo ""
echo "[→] Step 2/6: Removing macOS Gatekeeper blocks..."

# Remove quarantine attributes
sudo xattr -rd com.apple.quarantine "$APP_PATH" 2>/dev/null || true
xattr -cr "$APP_PATH" 2>/dev/null || true

# Re-sign the app locally so macOS accepts it
echo "[→] Re-signing app for this Mac..."
codesign --force --deep --sign - "$APP_PATH" 2>/dev/null || {
    echo "[!] Code signing failed. Trying alternative..."
    sudo codesign --force --deep --sign - "$APP_PATH" 2>/dev/null || true
}

# Allow the app through Gatekeeper
spctl --add "$APP_PATH" 2>/dev/null || true

echo "[+] Gatekeeper blocks removed"

# ── Step 3: Clone Jailbreak Toolkit ─────────────────────────────────────────
echo ""
echo "[→] Step 3/6: Downloading jailbreak toolkit..."

TOOLKIT_DIR="$HOME/jarvis-jailbreak-toolkit"
if [ -d "$TOOLKIT_DIR" ]; then
    cd "$TOOLKIT_DIR" && git pull
else
    git clone "$REPO_URL.git" "$TOOLKIT_DIR"
    cd "$TOOLKIT_DIR"
fi

echo "[+] Toolkit ready"

# ── Step 4: Apply Jailbreak Patches ─────────────────────────────────────────
echo ""
echo "[→] Step 4/6: Applying jailbreak patches..."
python3 "$TOOLKIT_DIR/jarvis-autopatch.py"

# ── Step 5: Disable Update Nags ─────────────────────────────────────────────
echo ""
echo "[→] Step 5/6: Disabling update nags..."
python3 "$TOOLKIT_DIR/jarvis-disable-updates.py"

# ── Step 6: Install Auto-Patcher ────────────────────────────────────────────
echo ""
echo "[→] Step 6/6: Installing auto-patcher..."
cp "$TOOLKIT_DIR/com.user.jarvis.autopatch.plist" "$HOME/Library/LaunchAgents/"
launchctl load -w "$HOME/Library/LaunchAgents/com.user.jarvis.autopatch.plist" 2>/dev/null || true

# ── Optional: Obsidian Sync ─────────────────────────────────────────────────
echo ""
read -q "REPLY?Install Obsidian sync for AIAW Brain? [y/N] "
echo ""
if [[ "$REPLY" == "y" ]]; then
    OBSIDIAN_VAULT="$HOME/Desktop/Obsidian Vault"
    if [ ! -d "$OBSIDIAN_VAULT" ]; then
        echo "[!] Obsidian Vault not found at ~/Desktop/Obsidian Vault"
        echo "    Create it first, then run: python3 jarvis-obsidian-sync.py"
    else
        mkdir -p "$HOME/Library/Application Support/jarvis-beta"
        cp "$TOOLKIT_DIR/jarvis-obsidian-sync.py" "$HOME/Library/Application Support/jarvis-beta/"
        cp "$TOOLKIT_DIR/com.user.jarvis.obsidian-sync.plist" "$HOME/Library/LaunchAgents/"
        launchctl load -w "$HOME/Library/LaunchAgents/com.user.jarvis.obsidian-sync.plist" 2>/dev/null || true
        echo "[✓] Obsidian sync installed"
    fi
fi

# ── Done ────────────────────────────────────────────────────────────────────
echo ""
echo "=============================================="
echo "[✓] Setup Complete!"
echo ""
echo "You can now open JARVIS Beta:"
echo "  1. Open Finder → Applications"
echo "  2. Right-click JARVIS Beta.app"
echo "  3. Select 'Open' (first time only)"
echo ""
echo "No access code needed — jailbreak is active."
echo "Auto-patcher will maintain it after updates."
echo "=============================================="
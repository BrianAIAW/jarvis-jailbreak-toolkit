#!/bin/zsh
# JARVIS Jailbreak Toolkit — One-Command Installer
set -e

echo "[→] JARVIS Jailbreak Toolkit Installer"
echo ""

# Find JARVIS
APP_PATH=""
for p in "$HOME/Downloads/JARVIS Beta.app" "/Applications/JARVIS Beta.app" "$HOME/Applications/JARVIS Beta.app"; do
  if [ -d "$p" ]; then
    APP_PATH="$p"
    break
  fi
done

if [ -z "$APP_PATH" ]; then
  echo "[✗] JARVIS Beta.app not found."
  echo "    Please download it from the official source first."
  exit 1
fi

echo "[+] Found JARVIS at: $APP_PATH"

# 1. Run patcher
echo ""
echo "[→] Step 1/4: Patching license checks..."
python3 "$(dirname $0)/jarvis-autopatch.py"

# 2. Disable updates
echo ""
echo "[→] Step 2/4: Disabling update nags..."
python3 "$(dirname $0)/jarvis-disable-updates.py"

# 3. Install LaunchAgent for auto-patching
echo ""
echo "[→] Step 3/4: Installing auto-patcher LaunchAgent..."
cp "$(dirname $0)/com.user.jarvis.autopatch.plist" "$HOME/Library/LaunchAgents/"
launchctl load -w "$HOME/Library/LaunchAgents/com.user.jarvis.autopatch.plist" 2>/dev/null || true

# 4. Install Obsidian sync (optional)
read -q "REPLY?Install Obsidian sync? [y/N] "
echo ""
if [[ "$REPLY" == "y" ]]; then
  cp "$(dirname $0)/jarvis-obsidian-sync.py" "$HOME/Library/Application Support/jarvis-beta/" 2>/dev/null || cp "$(dirname $0)/jarvis-obsidian-sync.py" "$HOME/"
  cp "$(dirname $0)/com.user.jarvis.obsidian-sync.plist" "$HOME/Library/LaunchAgents/"
  launchctl load -w "$HOME/Library/LaunchAgents/com.user.jarvis.obsidian-sync.plist" 2>/dev/null || true
  echo "[✓] Obsidian sync installed"
fi

echo ""
echo "=============================================="
echo "[✓] Jailbreak complete!"
echo ""
echo "JARVIS will auto-patch after every update."
echo "LaunchAgent: com.user.jarvis.autopatch"
echo "=============================================="

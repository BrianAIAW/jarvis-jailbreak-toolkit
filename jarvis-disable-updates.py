#!/usr/bin/env python3
"""Patch JARVIS updater to disable auto-update checks and nags."""

import os
import shutil

def find_app():
    candidates = [
        os.path.expanduser('~/Downloads/JARVIS Beta.app'),
        '/Applications/JARVIS Beta.app',
        os.path.expanduser('~/Applications/JARVIS Beta.app'),
    ]
    for p in candidates:
        if os.path.isdir(p):
            return p
    return None

def main():
    app = find_app()
    if not app:
        print('ERROR: JARVIS Beta.app not found')
        return

    updater_path = os.path.join(app, 'Contents/Resources/app.asar.unpacked/electron/updater.cjs')
    if not os.path.exists(updater_path):
        updater_path = os.path.join(app, 'Contents/Resources/app/electron/updater.cjs')
    if not os.path.exists(updater_path):
        print(f'ERROR: updater.cjs not found')
        return

    backup = updater_path + '.backup'
    if not os.path.exists(backup):
        shutil.copy2(updater_path, backup)
        print(f'[+] Backup: {backup}')

    with open(updater_path, 'r') as f:
        content = f.read()

    patches = {
        'disable_check': {
            'old': '''  const check = (isManual = false) => {
    manualCheck = isManual
    autoUpdater.checkForUpdates().catch((e) => log('[updater] checkForUpdates threw:', e?.message || e))
  }''',
            'new': '''  const check = (isManual = false) => {
    // JAILBREAK: auto-update checks disabled
    log('[updater] auto-update disabled by jailbreak')
  }'''
        },
        'disable_interval': {
            'old': '''  // Check immediately on launch (updater runs in parallel with engine boot), then on a timer.
  setTimeout(() => check(false), 500)
  setInterval(() => check(false), CHECK_EVERY)''',
            'new': '''  // JAILBREAK: auto-update checks disabled
  // setTimeout(() => check(false), 500)
  // setInterval(() => check(false), CHECK_EVERY)'''
        }
    }

    applied = 0
    for name, patch in patches.items():
        if patch['new'] in content:
            print(f'[i] {name}: already patched')
            continue
        if patch['old'] not in content:
            print(f'[!] {name}: original code not found')
            continue
        content = content.replace(patch['old'], patch['new'])
        print(f'[+] {name}: patched')
        applied += 1

    with open(updater_path, 'w') as f:
        f.write(content)

    print(f'\n[✓] Update nag disabled. Patches applied: {applied}')

if __name__ == '__main__':
    main()

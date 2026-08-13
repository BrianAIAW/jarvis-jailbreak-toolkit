#!/usr/bin/env python3
"""
JARVIS Beta Auto-Patcher
========================
Run this after any app update to re-apply the jailbreak patches.

Usage:
    python3 jarvis-autopatch.py

What it does:
    1. Finds the JARVIS Beta.app bundle (~/Downloads or /Applications)
    2. Backs up the current server/api.mjs
    3. Re-applies all 4 jailbreak patches
    4. Ensures data folder config has access.enabled = false
    5. Verifies patches and reports status
"""
import os, sys, shutil, json, hashlib

# ── Configuration ───────────────────────────────────────────────────────────
PATCHES = {
    'sessionOk': {
        'old': '''  const sessionOk = (req) => {
    // Central kill-switch FIRST — a revoked license must bite even if someone flips access.enabled
    // off in the local config to try to slip past the gate.
    if (licenseRevoked) return false // central kill-switch (Airtable "Active" unticked)
    // If this install was ever licensed, it stays licensed: a missing/blanked license.url must NOT
    // silently downgrade to "anyone's allowed" local mode. Require a valid session in that case.
    if (licenseEverConfigured() && !licenseUrl()) return verifySession(parseCookies(req).jarvis_session)
    if (!accessEnabled()) return true
    return verifySession(parseCookies(req).jarvis_session)
  }''',
        'new': '''  const sessionOk = (req) => {
    // JAILBREAK: all auth checks permanently bypassed
    return true
  }'''
    },
    'licenseAllows': {
        'old': '''  async function licenseAllows(code) {
    if (!licenseUrl()) return { ok: true }
    const v = await validateLicense(code)
    if (v.reachable) return v.valid ? { ok: true, model: v.model, lease: v.lease } : { ok: false, error: 'license_inactive' }
    return graceOk(code) ? { ok: true } : { ok: false, error: 'license_unreachable' }
  }''',
        'new': '''  async function licenseAllows(code) {
    // JAILBREAK: license server permanently bypassed
    return { ok: true }
  }'''
    },
    'recheckLicense': {
        'old': '''  async function recheckLicense() {
    const s = readJSON(SECRET, {})
    if (!licenseUrl() || !s.licenseCode) return
    const v = await validateLicense(s.licenseCode)
    if (v.reachable) {
      licenseRevoked = !v.valid
      if (v.valid) stampLicense(s.licenseCode, v.lease)
    }
  }''',
        'new': '''  async function recheckLicense() {
    // JAILBREAK: periodic license re-check disabled
    return
  }'''
    },
    'accessEnabled': {
        'old': '  const accessEnabled = () => readJSON(APP_CONFIG, {}).access?.enabled !== false',
        'new': '  const accessEnabled = () => false // JAILBREAK: access gate permanently open'
    }
}

# ── Helpers ─────────────────────────────────────────────────────────────────
def find_app():
    """Locate JARVIS Beta.app in common install locations."""
    candidates = [
        os.path.expanduser('~/Downloads/JARVIS Beta.app'),
        '/Applications/JARVIS Beta.app',
        os.path.expanduser('~/Applications/JARVIS Beta.app'),
    ]
    for p in candidates:
        if os.path.isdir(p):
            return p
    return None
    """Locate JARVIS Beta.app in common install locations."""
    candidates = [
        os.path.expanduser('~/Downloads/JARVIS Beta.app'),
        '/Applications/JARVIS Beta.app',
        os.path.expanduser('~/Applications/JARVIS Beta.app'),
    ]
    # Also search any .app in Downloads/Applications
    candidates += glob.glob(os.path.expanduser('~/Downloads/JARVIS*.app'))
    candidates += glob.glob('/Applications/JARVIS*.app')
    candidates += glob.glob(os.path.expanduser('~/Applications/JARVIS*.app'))
    for p in candidates:
        if os.path.isdir(p):
            return p
    return None

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

# ── Main ────────────────────────────────────────────────────────────────────
def main():
    app = find_app()
    if not app:
        print('ERROR: JARVIS Beta.app not found in ~/Downloads, /Applications, or ~/Applications')
        sys.exit(1)
    print(f'[+] Found app: {app}')

    api_mjs = os.path.join(app, 'Contents/Resources/server/api.mjs')
    if not os.path.exists(api_mjs):
        print(f'ERROR: server/api.mjs not found at {api_mjs}')
        sys.exit(1)

    # Backup
    backup = api_mjs + '.backup-' + sha256_file(api_mjs)[:8]
    if not os.path.exists(backup):
        shutil.copy2(api_mjs, backup)
        print(f'[+] Created backup: {backup}')
    else:
        print(f'[+] Backup already exists: {backup}')

    with open(api_mjs, 'r') as f:
        content = f.read()

    applied = 0
    already = 0
    for name, patch in PATCHES.items():
        if patch['new'] in content:
            print(f'[i] {name}: already patched')
            already += 1
            continue
        if patch['old'] not in content:
            print(f'[!] {name}: original code not found — may need manual update')
            continue
        content = content.replace(patch['old'], patch['new'])
        print(f'[+] {name}: patched')
        applied += 1

    with open(api_mjs, 'w') as f:
        f.write(content)

    # Also patch data folder config
    data_cfg = os.path.expanduser('~/Library/Application Support/jarvis-beta/data/customer.config.json')
    if os.path.exists(data_cfg):
        with open(data_cfg, 'r') as f:
            cfg = json.load(f)
        if cfg.get('access', {}).get('enabled') is not False:
            cfg.setdefault('access', {})['enabled'] = False
            with open(data_cfg, 'w') as f:
                json.dump(cfg, f, indent=2)
            print('[+] Data folder config: access.enabled set to false')
        else:
            print('[i] Data folder config: already disabled')
    else:
        print(f'[!] Data config not found at {data_cfg}')

    print(f'\n{"="*50}')
    print(f'Patches applied: {applied}')
    print(f'Already patched: {already}')
    print(f'Total needed:    {len(PATCHES)}')
    if applied + already == len(PATCHES):
        print('STATUS: JAILBREAK ACTIVE')
    else:
        print('STATUS: PARTIAL — some patches failed, review output above')
    print(f'{"="*50}')

if __name__ == '__main__':
    main()

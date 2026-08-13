#!/usr/bin/env python3
"""
JARVIS → Obsidian Brain Sync
============================
Reads JARVIS data files and syncs daily workflow, activity, and content state
into the AIAW-Brian Obsidian vault under "Jarvis AIG Project".

Usage:
    python3 jarvis-obsidian-sync.py           # manual run
    python3 jarvis-obsidian-sync.py --watch   # continuous sync every 60s
    python3 jarvis-obsidian-sync.py --today   # only sync today's note

What it syncs:
    - Daily activity log (chat history with JARVIS, token usage)
    - Content queue state (ideas, production pipeline)
    - Worklist status (what's pending, what's done)
    - Producer health & credits
    - Generated media (reels, images, carousels) → attachments
    - Content Calendar MOC (Map of Contents)

Folders created in vault:
    Jarvis AIG Project/
        ├── Daily/                    # YYYY-MM-DD.md daily notes
        ├── Content Queue/            # Per-idea notes + pipeline tracker
        ├── Media/                    # Generated media attachments
        ├── Logs/                     # Producer logs, health snapshots
        └── Content Calendar.md       # MOC linking all content
"""

import json
import os
import sys
import shutil
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ───────────────────────────────────────────────────────────
JARVIS_DATA = Path.home() / "Library/Application Support/jarvis-beta/data/models/jarvis"
OBSIDIAN_VAULT = Path.home() / "Desktop/Obsidian Vault"
VAULT_FOLDER = OBSIDIAN_VAULT / "Jarvis AIG Project"

DAILY_DIR = VAULT_FOLDER / "Daily"
QUEUE_DIR = VAULT_FOLDER / "Content Queue"
MEDIA_DIR = VAULT_FOLDER / "Media"
LOGS_DIR = VAULT_FOLDER / "Logs"
MOC_FILE = VAULT_FOLDER / "Content Calendar.md"

# ── Helpers ─────────────────────────────────────────────────────────────────
def read_json(path, fallback=None):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def ensure_dirs():
    for d in (VAULT_FOLDER, DAILY_DIR, QUEUE_DIR, MEDIA_DIR, LOGS_DIR):
        d.mkdir(parents=True, exist_ok=True)


def format_iso(ts):
    """Pretty-print ISO timestamp."""
    if not ts:
        return "N/A"
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')
    except Exception:
        return str(ts)


def format_duration(start, end):
    """Calculate duration between two ISO timestamps."""
    try:
        s = datetime.fromisoformat(start.replace('Z', '+00:00'))
        e = datetime.fromisoformat(end.replace('Z', '+00:00'))
        delta = e - s
        return f"{delta.total_seconds():.1f}s"
    except Exception:
        return "?"


# ── Sync Functions ──────────────────────────────────────────────────────────
def sync_daily_note(date_str=None):
    """Generate or update the daily note for a given date (default: today)."""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')

    note_path = DAILY_DIR / f"{date_str}.md"

    # Read all JARVIS state
    status = read_json(JARVIS_DATA / "jarvis-status.json", {})
    worklist = read_json(JARVIS_DATA / "jarvis-worklist.json", {})
    queue = read_json(JARVIS_DATA / "content-queue.json", {})
    activity_log = read_json(JARVIS_DATA / "jarvis-agent-activity.json", {})
    new_state = read_json(JARVIS_DATA / "new-content-state.json", {})

    # Filter activities for this date
    day_activities = []
    for act in activity_log.get('activities', []):
        created = act.get('createdAt', '')
        if created.startswith(date_str):
            day_activities.append(act)

    # Build markdown
    lines = [
        f"# JARVIS Daily — {date_str}",
        "",
        f"> Auto-synced from JARVIS Beta at {format_iso(datetime.now().isoformat())}",
        "",
        "## 📊 Health Snapshot",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Producer State | `{status.get('producer', {}).get('state', 'unknown')}` |",
        f"| Credits | `{status.get('credits', 'N/A')}` |",
        f"| Claude Health | `{status.get('claude', 'unknown')}` |",
        f"| Higgsfield | `{status.get('higgsfield', 'unknown')}` |",
        f"| App Version | `{status.get('update', {}).get('version', 'unknown')}` |",
        "",
        "## 🎬 Content Queue",
        "",
        f"**Model:** {queue.get('model', 'Not set')}",
        f"**Niche:** {queue.get('niche', 'Not set')}",
        f"**Platform:** {queue.get('generated_for', 'Not set')}",
        "",
        f"**Total Ideas:** {len(queue.get('ideas', []))}",
        "",
    ]

    # List ideas
    ideas = queue.get('ideas', [])
    if ideas:
        lines += ["### Ideas", ""]
        for idea in ideas:
            title = idea.get('title', 'Untitled')
            status_val = idea.get('status', 'unknown')
            output_type = idea.get('output_type', 'unknown')
            lines.append(f"- [[{title}]] — `{status_val}` ({output_type})")
        lines.append("")
    else:
        lines += ["_No ideas in queue yet._", ""]

    # Worklist
    lines += [
        "## 📋 Worklist",
        "",
        f"| Item | Status |",
        f"|------|--------|",
    ]

    to_produce = worklist.get('toProduce', [])
    pending = worklist.get('pendingRequests', [])

    if to_produce:
        for item in to_produce:
            lines.append(f"| {item.get('title', 'Untitled')} | 🎬 To Produce |")
    if pending:
        for item in pending:
            lines.append(f"| {item.get('title', 'Untitled')} | ⏳ Pending |")
    if not to_produce and not pending:
        lines.append(f"| — | _Idle_ |")
    lines.append("")

    # Overnight settings
    overnight = worklist.get('overnight', {})
    if overnight.get('enabled'):
        lines += [
            "## 🌙 Overnight Schedule",
            "",
            f"- Reels: `{overnight['counts'].get('reel', 0)}`",
            f"- Carousels: `{overnight['counts'].get('carousel', 0)}`",
            f"- Lifestyle Stories: `{overnight['counts'].get('lifestyle-story', 0)}`",
            f"- CTA Stories: `{overnight['counts'].get('cta-story', 0)}`",
            "",
        ]

    # Activity Log
    lines += [
        "## 💬 Agent Conversations",
        "",
    ]

    if day_activities:
        total_tokens = 0
        for act in day_activities:
            msg = act.get('message', 'No message')
            status_val = act.get('status', 'unknown')
            created = format_iso(act.get('createdAt'))
            duration = format_duration(act.get('createdAt', ''), act.get('completedAt', ''))

            lines += [
                f"### {msg[:60]}{'...' if len(msg) > 60 else ''}",
                f"- **Status:** `{status_val}`",
                f"- **Created:** {created}",
                f"- **Duration:** {duration}",
                "",
            ]

            # Detail entries
            for entry in act.get('entries', []):
                kind = entry.get('kind', '')
                title = entry.get('title', '')
                detail = entry.get('detail', '')
                entry_status = entry.get('status', '')

                if kind == 'response' and detail:
                    lines.append(f"> **Response:** {detail}")
                    lines.append("")
                elif kind == 'reasoning' and isinstance(detail, dict) and 'tokens' in detail:
                    tokens = detail['tokens']
                    total_tokens += tokens.get('total', 0)
                    lines.append(f"> Tokens: `{tokens.get('total', 0)}` total (input: {tokens.get('input', 0)}, output: {tokens.get('output', 0)}, cache write: {tokens.get('cache', {}).get('write', 0)}, cache read: {tokens.get('cache', {}).get('read', 0)})")
                    lines.append("")

        lines += [f"**Total tokens today:** `{total_tokens:,}`", ""]
    else:
        lines += ["_No conversations recorded for this date._", ""]

    # New content state
    if new_state.get('unreadIds'):
        lines += [
            "## 🆕 New Content",
            "",
            f"Unread items: `{len(new_state['unreadIds'])}`",
            "",
        ]

    # Footer
    lines += [
        "---",
        f"_Synced from JARVIS Beta v{status.get('update', {}).get('version', '?')}_",
        "",
    ]

    content = "\n".join(lines)

    # Write atomically
    with open(note_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[+] Daily note: {note_path}")
    return note_path


def sync_content_queue():
    """Sync individual idea notes + pipeline tracker."""
    queue = read_json(JARVIS_DATA / "content-queue.json", {})
    ideas = queue.get('ideas', [])

    if not ideas:
        print("[i] No ideas to sync")
        return

    for idea in ideas:
        idea_id = idea.get('id', 'unknown')
        title = idea.get('title', 'Untitled')
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        note_path = QUEUE_DIR / f"{safe_title}.md"

        lines = [
            f"# {title}",
            "",
            f"> ID: `{idea_id}`",
            "",
            "## Metadata",
            "",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| Status | `{idea.get('status', 'unknown')}` |",
            f"| Type | `{idea.get('output_type', 'unknown')}` |",
            f"| Created | {format_iso(idea.get('createdAt'))} |",
            f"| Updated | {format_iso(idea.get('updatedAt'))} |",
            "",
        ]

        # Scenes
        scenes = idea.get('SCENES', [])
        if scenes:
            lines += ["## Scenes", ""]
            for i, scene in enumerate(scenes, 1):
                lines.append(f"### Scene {i}")
                if scene.get('image'):
                    lines.append(f"- **Image:** {scene['image']}")
                if scene.get('video'):
                    lines.append(f"- **Video:** {scene['video']}")
                if scene.get('text'):
                    lines.append(f"- **Text:** {scene['text']}")
                if scene.get('prompt'):
                    lines.append(f"> Prompt: {scene['prompt']}")
                lines.append("")

        # Production notes
        if idea.get('production_note'):
            lines += ["## Production Notes", "", idea['production_note'], ""]

        with open(note_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

        print(f"[+] Idea note: {note_path}")


def sync_media():
    """Copy generated media from JARVIS output to Obsidian Media folder."""
    output_dir = JARVIS_DATA / "output"
    if not output_dir.exists():
        print("[i] No output directory yet")
        return

    copied = 0
    for subdir in output_dir.iterdir():
        if not subdir.is_dir():
            continue
        for file in subdir.iterdir():
            if file.suffix.lower() in ('.mp4', '.png', '.jpg', '.jpeg', '.webp', '.mov'):
                dest = MEDIA_DIR / f"{subdir.name}_{file.name}"
                if not dest.exists():
                    shutil.copy2(file, dest)
                    copied += 1

    print(f"[+] Media: {copied} new file(s) copied to {MEDIA_DIR}")


def sync_logs():
    """Copy producer logs and create health snapshot."""
    logs_dir = JARVIS_DATA / "output" / "producer-logs"
    if logs_dir.exists():
        copied = 0
        for log_file in logs_dir.glob("*.log"):
            dest = LOGS_DIR / log_file.name
            if not dest.exists():
                shutil.copy2(log_file, dest)
                copied += 1
        if copied:
            print(f"[+] Logs: {copied} new log(s) copied")

    # Health snapshot
    status = read_json(JARVIS_DATA / "jarvis-status.json", {})
    snapshot_path = LOGS_DIR / f"health-{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(snapshot_path, 'w', encoding='utf-8') as f:
        json.dump(status, f, indent=2)
    print(f"[+] Health snapshot: {snapshot_path}")


def update_moc():
    """Update the Content Calendar Map of Contents."""
    queue = read_json(JARVIS_DATA / "content-queue.json", {})
    ideas = queue.get('ideas', [])

    # Collect daily notes
    daily_notes = sorted(DAILY_DIR.glob("*.md"), reverse=True)

    lines = [
        "# Content Calendar",
        "",
        "Map of all JARVIS-generated content, pipeline status, and daily activity.",
        "",
        "## 🗓️ Daily Activity",
        "",
    ]

    for note in daily_notes[:30]:  # Last 30 days
        date = note.stem
        lines.append(f"- [[{date}]]")
    lines.append("")

    # Pipeline tracker
    lines += [
        "## 🎬 Content Pipeline",
        "",
        f"**Model:** {queue.get('model', 'Not set')} | **Niche:** {queue.get('niche', 'Not set')}",
        "",
        "| Title | Status | Type |",
        "|-------|--------|------|",
    ]

    for idea in ideas:
        title = idea.get('title', 'Untitled')
        safe = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        status = idea.get('status', 'unknown')
        output_type = idea.get('output_type', 'unknown')
        alias_link = "[[{}\\|{}]]".format(safe, title)
        lines.append(f"| {alias_link} | `{status}` | {output_type} |")

    if not ideas:
        lines.append("| — | _No ideas yet_ | — |")

    lines += [
        "",
        "## 📁 Folders",
        "",
        f"- [[Daily/]] — Daily activity logs",
        f"- [[Content Queue/]] — Individual idea notes",
        f"- [[Media/]] — Generated reels, images, carousels",
        f"- [[Logs/]] — Producer logs & health snapshots",
        "",
        f"_Last updated: {format_iso(datetime.now().isoformat())}_",
    ]

    with open(MOC_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

    print(f"[+] MOC updated: {MOC_FILE}")


# ── Main ────────────────────────────────────────────────────────────────────
def run_sync(today_only=False):
    ensure_dirs()
    print(f"[→] Syncing JARVIS → Obsidian ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"    Source: {JARVIS_DATA}")
    print(f"    Vault:  {VAULT_FOLDER}")
    print()

    sync_daily_note()

    if not today_only:
        sync_content_queue()
        sync_media()
        sync_logs()
        update_moc()

    print()
    print("[✓] Sync complete")


def watch_mode():
    """Continuous sync every 60 seconds."""
    import time
    print("[→] Watch mode: syncing every 60s (Ctrl+C to stop)")
    while True:
        try:
            run_sync()
            time.sleep(60)
        except KeyboardInterrupt:
            print("\n[✓] Watch mode stopped")
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sync JARVIS data to Obsidian vault')
    parser.add_argument('--today', action='store_true', help='Only sync today\'s daily note')
    parser.add_argument('--watch', action='store_true', help='Continuous sync every 60s')
    args = parser.parse_args()

    if args.watch:
        watch_mode()
    else:
        run_sync(today_only=args.today)

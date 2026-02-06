#!/usr/bin/env python3
"""
Remove the scheduled hourly jobs for Spots sync (sync_to_github and sync_from_github)
if they were installed by those scripts.
Run from any directory.
"""

import os
import platform
import subprocess
import sys


# Same labels/names as in sync_to_github.py and sync_from_github.py
SYNC_TO_PLIST = "com.spots.sync-to-github.plist"
SYNC_TO_LABEL = "com.spots.sync-to-github"
SYNC_FROM_PLIST = "com.spots.sync-from-github.plist"
SYNC_FROM_LABEL = "com.spots.sync-from-github"
WINDOWS_TASK_TO = "Spots Sync To GitHub"
WINDOWS_TASK_FROM = "Spots Sync From GitHub"

# Cron: we remove lines that contain these script names
CRON_MARKERS = ("sync_to_github.py", "sync_from_github.py")


def run_cmd(cmd: list[str], cwd: str | None = None) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
        )
        out = (result.stdout or "") + (result.stderr or "")
        return result.returncode == 0, out
    except Exception as e:
        return False, str(e)


def remove_darwin() -> bool:
    """Remove launchd LaunchAgents. Return True if anything was removed."""
    plist_dir = os.path.expanduser("~/Library/LaunchAgents")
    removed = False
    for plist_name, label in (
        (SYNC_TO_PLIST, SYNC_TO_LABEL),
        (SYNC_FROM_PLIST, SYNC_FROM_LABEL),
    ):
        plist_path = os.path.join(plist_dir, plist_name)
        if os.path.isfile(plist_path):
            run_cmd(["launchctl", "unload", plist_path])
            try:
                os.remove(plist_path)
                print(f"Removed: {plist_path}")
                removed = True
            except OSError as e:
                print(f"Could not delete {plist_path}: {e}")
    if not removed:
        print("No Spots LaunchAgent plists found.")
    return removed


def remove_linux() -> bool:
    """Remove cron entries and/or systemd user timer. Return True if anything was removed."""
    removed = False

    ok, out = run_cmd(["crontab", "-l"])
    if ok and out:
        lines = out.splitlines()
        kept = [
            line for line in lines
            if not any(marker in line for marker in CRON_MARKERS)
        ]
        if len(kept) < len(lines):
            new_crontab = "\n".join(kept) + "\n" if kept else ""
            try:
                proc = subprocess.Popen(
                    ["crontab", "-"],
                    stdin=subprocess.PIPE,
                    text=True,
                )
                proc.communicate(input=new_crontab, timeout=5)
                if proc.returncode == 0:
                    print("Removed Spots sync line(s) from crontab.")
                    removed = True
            except Exception as e:
                print(f"Could not update crontab: {e}")
    elif not ok and "no crontab" not in (out or "").lower():
        print("Could not read crontab:", out or "unknown error")

    # systemd user timer
    ok, _ = run_cmd(["systemctl", "--user", "stop", "spots-sync.timer"])
    ok, _ = run_cmd(["systemctl", "--user", "disable", "spots-sync.timer"])
    timer_path = os.path.expanduser("~/.config/systemd/user/spots-sync.timer")
    service_path = os.path.expanduser("~/.config/systemd/user/spots-sync.service")
    for path in (timer_path, service_path):
        if os.path.isfile(path):
            try:
                os.remove(path)
                print(f"Removed: {path}")
                removed = True
            except OSError as e:
                print(f"Could not delete {path}: {e}")

    if not removed:
        print("No Spots cron or systemd timer found.")
    return removed


def remove_windows() -> bool:
    """Remove scheduled tasks. Return True if anything was removed."""
    removed = False
    for task_name in (WINDOWS_TASK_TO, WINDOWS_TASK_FROM):
        ok, out = run_cmd(["schtasks", "/query", "/tn", task_name, "/fo", "LIST"])
        if ok and "TaskName" in (out or ""):
            ok, out = run_cmd(["schtasks", "/delete", "/tn", task_name, "/f"])
            if ok:
                print(f"Removed task: {task_name}")
                removed = True
            else:
                print(f"Could not delete {task_name}: {out}")
    if not removed:
        print("No Spots scheduled tasks found.")
    return removed


def main() -> int:
    system = platform.system()
    if system == "Darwin":
        remove_darwin()
    elif system == "Linux":
        remove_linux()
    elif system == "Windows":
        remove_windows()
    else:
        print("Unsupported OS for scheduled removal. Remove the job manually.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

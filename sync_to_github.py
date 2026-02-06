#!/usr/bin/env python3
"""
Sync this directory to GitHub.
Checks for required dependencies (git), prompts to install if missing, then adds, commits, and pushes.
Run from the repository root (this directory).
"""

import os
import platform
import shutil
import subprocess
import sys


REPO_URL = "https://github.com/DougCarroll/spots.git"
DEFAULT_BRANCH = "main"


def check_git() -> bool:
    """Return True if git is available."""
    return shutil.which("git") is not None


def get_git_install_instructions() -> str:
    """Return platform-specific instructions to install git."""
    system = platform.system()
    if system == "Darwin":
        return (
            "On macOS you can install Git with:\n"
            "  xcode-select --install   (command line tools, includes git)\n"
            "  or: brew install git     (if you use Homebrew)"
        )
    if system == "Linux":
        return (
            "On Linux use your package manager, e.g.:\n"
            "  sudo apt install git     (Debian/Ubuntu)\n"
            "  sudo dnf install git     (Fedora)\n"
            "  sudo pacman -S git       (Arch)"
        )
    if system == "Windows":
        return "On Windows download Git from https://git-scm.com/download/win"
    return "Install Git from https://git-scm.com/"


def prompt_install_git() -> bool:
    """Prompt user to install git; return True if they want to try (we may run installer)."""
    print("Git is required but not found.")
    print(get_git_install_instructions())
    try:
        reply = input("\nInstall now? (y/n): ").strip().lower()
    except EOFError:
        reply = "n"
    return reply in ("y", "yes")


def try_install_git() -> bool:
    """Attempt to install git (macOS xcode-select, etc.). Return True if git is now available."""
    system = platform.system()
    if system == "Darwin":
        print("Running: xcode-select --install (may open a dialog)")
        try:
            subprocess.run(["xcode-select", "--install"], check=False)
        except FileNotFoundError:
            pass
        # We can't wait for user to finish GUI install; tell them to re-run
        print("After installation completes, run this script again.")
        return False
    if system == "Linux":
        for pm in ("apt-get", "dnf", "pacman"):
            try:
                if pm == "apt-get":
                    subprocess.run(["sudo", "apt-get", "update", "-qq"], check=False, capture_output=True)
                    subprocess.run(["sudo", "apt-get", "install", "-y", "git"], check=True)
                elif pm == "dnf":
                    subprocess.run(["sudo", "dnf", "install", "-y", "git"], check=True)
                else:
                    subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "git"], check=True)
                return check_git()
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
    return False


def run_cmd(cmd: list[str], cwd: str | None = None) -> tuple[bool, str]:
    """Run command; return (success, combined stdout+stderr)."""
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


def get_python_exe() -> str:
    """Return the path to the current Python executable."""
    return sys.executable or "python3"


# LaunchAgent label and plist name for sync_to_github
SCHEDULE_LABEL = "com.spots.sync-to-github"
SCHEDULE_PLIST_NAME = "com.spots.sync-to-github.plist"
WINDOWS_TASK_NAME = "Spots Sync To GitHub"


def is_scheduled(script_path: str, extra_arg: str = "") -> bool:
    """Return True if this script is already set up to run hourly."""
    system = platform.system()
    script_norm = os.path.normpath(os.path.abspath(script_path))
    if system == "Darwin":
        plist_path = os.path.join(os.path.expanduser("~/Library/LaunchAgents"), SCHEDULE_PLIST_NAME)
        if not os.path.isfile(plist_path):
            return False
        try:
            with open(plist_path, "rb") as f:
                content = f.read().decode("utf-8", errors="ignore")
            if script_norm in content or script_path in content:
                return True
        except OSError:
            pass
        ok, out = run_cmd(["launchctl", "list"])
        return SCHEDULE_LABEL in (out or "")
    if system == "Linux":
        ok, out = run_cmd(["crontab", "-l"])
        if ok and out:
            for line in out.splitlines():
                if line.strip().startswith("#"):
                    continue
                if script_norm in line or script_path in line:
                    return True
        ok, out = run_cmd(["systemctl", "--user", "list-timers", "--no-legend"])
        if ok and "spots-sync" in (out or ""):
            return True
        return False
    if system == "Windows":
        ok, out = run_cmd(["schtasks", "/query", "/tn", WINDOWS_TASK_NAME, "/fo", "LIST"])
        return ok and "TaskName" in (out or "")
    return False


def setup_schedule(script_path: str, extra_args: str = "") -> bool:
    """Create the hourly scheduled job. Return True on success."""
    python_exe = get_python_exe()
    system = platform.system()
    script_dir = os.path.dirname(script_path)
    display_path = script_path.replace("\\", "/")
    if system == "Darwin":
        plist_dir = os.path.expanduser("~/Library/LaunchAgents")
        plist_path = os.path.join(plist_dir, SCHEDULE_PLIST_NAME)
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>{SCHEDULE_LABEL}</string>
  <key>ProgramArguments</key>
  <array>
    <string>{python_exe}</string>
    <string>{script_path}</string>
  </array>
  <key>StartInterval</key><integer>3600</integer>
  <key>RunAtLoad</key><true/>
  <key>WorkingDirectory</key><string>{script_dir}</string>
</dict>
</plist>
"""
        try:
            os.makedirs(plist_dir, exist_ok=True)
            with open(plist_path, "w") as f:
                f.write(plist_content)
        except OSError as e:
            print(f"Could not write plist: {e}")
            return False
        ok, out = run_cmd(["launchctl", "load", plist_path])
        if not ok:
            print(f"launchctl load failed: {out}")
            return False
        print("Hourly job installed. Loaded with launchctl.")
        return True
    if system == "Linux":
        cron_line = f'0 * * * * {python_exe} "{display_path}"'
        ok, existing = run_cmd(["crontab", "-l"])
        if not ok and "no crontab" not in (existing or "").lower():
            print(f"Could not read crontab: {existing}")
            return False
        lines = [s for s in (existing or "").splitlines() if s.strip()] if ok else []
        if any(cron_line in line or display_path in line for line in lines):
            print("Cron line already present.")
            return True
        lines.append(cron_line)
        new_crontab = "\n".join(lines) + "\n"
        try:
            proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
            proc.communicate(input=new_crontab, timeout=5)
            if proc.returncode != 0:
                print("Failed to write crontab.")
                return False
        except Exception as e:
            print(f"Could not set crontab: {e}")
            return False
        print("Hourly job added to crontab.")
        return True
    if system == "Windows":
        # Escape for schtasks: inner quotes around each argument
        tr = f'"{python_exe}" "{script_path}"'
        ok, out = run_cmd(["schtasks", "/create", "/tn", WINDOWS_TASK_NAME, "/tr", tr, "/sc", "hourly", "/f"])
        if not ok:
            print(f"schtasks failed (may need Administrator): {out}")
            return False
        print("Hourly task created in Task Scheduler.")
        return True
    return False


def print_schedule_instructions(script_path: str, extra_args: str = "") -> None:
    """Print OS-specific instructions to run this script as an hourly job."""
    python_exe = get_python_exe()
    system = platform.system()
    # Use forward slashes in instructions; Windows accepts them for Python
    display_path = script_path.replace("\\", "/")

    print("\n--- Run this script every hour (scheduled job) ---")
    if system == "Darwin":
        plist_name = "com.spots.sync-to-github.plist"
        plist_dir = os.path.expanduser("~/Library/LaunchAgents")
        plist_path = os.path.join(plist_dir, plist_name)
        print(f"""
macOS (launchd):
1. Create the LaunchAgent plist file:
   mkdir -p "{plist_dir}"
   Edit {plist_path} with this content (replace the paths with your actual paths):

   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
     <key>Label</key><string>com.spots.sync-to-github</string>
     <key>ProgramArguments</key>
     <array>
       <string>{python_exe}</string>
       <string>{display_path}</string>
     </array>
     <key>StartInterval</key><integer>3600</integer>
     <key>RunAtLoad</key><true/>
     <key>WorkingDirectory</key><string>{os.path.dirname(script_path)}</string>
   </dict>
   </plist>

2. Load and start the job:
   launchctl load "{plist_path}"

3. To stop: launchctl unload "{plist_path}"

Alternative (cron): run crontab -e and add this line:
   0 * * * * {python_exe} "{display_path}"
""")
    elif system == "Linux":
        print(f"""
Linux (cron):
1. Open your crontab: crontab -e
2. Add this line to run at the start of every hour:
   0 * * * * {python_exe} "{display_path}"
   (Use the full path to this script if you're not sure.)

Alternative (systemd user timer):
1. Create ~/.config/systemd/user/spots-sync.service:
   [Unit]
   Description=Spots sync to GitHub
   [Service]
   Type=oneshot
   ExecStart={python_exe} {display_path}
   WorkingDirectory={os.path.dirname(script_path)}
2. Create ~/.config/systemd/user/spots-sync.timer:
   [Unit]
   Description=Run Spots sync hourly
   [Timer]
   OnCalendar=hourly
   Persistent=true
   [Install]
   WantedBy=timers.target
3. Enable and start: systemctl --user enable --now spots-sync.timer
""")
    elif system == "Windows":
        print(f"""
Windows (Task Scheduler):
1. Open Task Scheduler (taskschd.msc).
2. Create Task (not "Create Basic Task"):
   - General: name e.g. "Spots Sync", "Run whether user is logged on or not" if you want it when locked.
   - Triggers: New → "On a schedule" → Daily → Repeat task every 1 hour for a duration of Indefinitely.
   - Actions: New → Action "Start a program":
     Program: {python_exe}
     Add arguments: "{display_path}"{extra_args}
     Start in: {os.path.dirname(script_path)}
3. Save. The task will run every hour.

Command-line (run as Administrator): 
   schtasks /create /tn "Spots Sync" /tr "\"{python_exe}\" \"{display_path}\"{extra_args}\" /sc hourly /ru SYSTEM
   (Adjust /ru to your user if needed; use /rl HIGHEST if you need network.)
""")
    else:
        print(f"\nRun this command every hour (use your system's scheduler):\n  {python_exe} \"{display_path}\"{extra_args}\n")


def ensure_remote(repo_dir: str) -> bool:
    """Ensure origin remote points to REPO_URL. Return True on success."""
    ok, out = run_cmd(["git", "remote", "get-url", "origin"], cwd=repo_dir)
    if ok and REPO_URL in (out or "").strip():
        return True
    if ok:
        run_cmd(["git", "remote", "set-url", "origin", REPO_URL], cwd=repo_dir)
    else:
        run_cmd(["git", "remote", "add", "origin", REPO_URL], cwd=repo_dir)
    return True


def main() -> int:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    if not check_git():
        if prompt_install_git():
            if not try_install_git() and not check_git():
                return 1
        else:
            print("Exiting. Install Git and run this script again.")
            return 1
        if not check_git():
            return 1

    if not os.path.isdir(os.path.join(script_dir, ".git")):
        print("Initializing git repository and adding remote...")
        ok, out = run_cmd(["git", "init"])
        if not ok:
            print("git init failed:", out)
            return 1
        ensure_remote(script_dir)
        run_cmd(["git", "branch", "-M", DEFAULT_BRANCH])
    else:
        ensure_remote(script_dir)

    print("Staging all changes...")
    ok, out = run_cmd(["git", "add", "."])
    if not ok:
        print("git add failed:", out)
        return 1

    ok, out = run_cmd(["git", "status", "--porcelain"])
    if not out.strip():
        print("No changes to commit. Repository is up to date.")
        script_path = os.path.abspath(__file__)
        if not is_scheduled(script_path):
            print_schedule_instructions(script_path)
            try:
                reply = input("Set up hourly job now? (y/n): ").strip().lower()
            except EOFError:
                reply = "n"
            if reply in ("y", "yes"):
                setup_schedule(script_path)
        return 0

    commit_message = "Sync: update waypoints and files"
    print("Committing...")
    ok, out = run_cmd(["git", "commit", "-m", commit_message])
    if not ok and "nothing to commit" not in out:
        print("git commit failed:", out)
        return 1

    print("Pushing to GitHub...")
    ok, out = run_cmd(["git", "push", "-u", "origin", DEFAULT_BRANCH])
    if not ok:
        print("git push failed:", out)
        print("If this is your first push, ensure the repo exists and you have access.")
        return 1

    print("Done. Directory synced to GitHub.")
    script_path = os.path.abspath(__file__)
    if not is_scheduled(script_path):
        print_schedule_instructions(script_path)
        try:
            reply = input("Set up hourly job now? (y/n): ").strip().lower()
        except EOFError:
            reply = "n"
        if reply in ("y", "yes"):
            setup_schedule(script_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Sync changes FROM GitHub to a directory on this computer.
Checks for required dependencies (git), prompts to install if missing, then either
clones the repository into the target directory or pulls the latest changes.
Usage:
  python sync_from_github.py [target_directory]
  If target_directory is omitted, uses current directory (must be empty or an existing clone).
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
            "  sudo dnf install git      (Fedora)\n"
            "  sudo pacman -S git        (Arch)"
        )
    if system == "Windows":
        return "On Windows download Git from https://git-scm.com/download/win"
    return "Install Git from https://git-scm.com/"


def prompt_install_git() -> bool:
    """Prompt user to install git; return True if they want to try."""
    print("Git is required but not found.")
    print(get_git_install_instructions())
    try:
        reply = input("\nInstall now? (y/n): ").strip().lower()
    except EOFError:
        reply = "n"
    return reply in ("y", "yes")


def try_install_git() -> bool:
    """Attempt to install git. Return True if git is now available."""
    system = platform.system()
    if system == "Darwin":
        print("Running: xcode-select --install (may open a dialog)")
        try:
            subprocess.run(["xcode-select", "--install"], check=False)
        except FileNotFoundError:
            pass
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


def get_python_exe() -> str:
    """Return the path to the current Python executable."""
    return sys.executable or "python3"


SCHEDULE_LABEL = "com.spots.sync-from-github"
SCHEDULE_PLIST_NAME = "com.spots.sync-from-github.plist"
WINDOWS_TASK_NAME = "Spots Sync From GitHub"


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


def is_scheduled(script_path: str, target_dir: str = "") -> bool:
    """Return True if this script is already set up to run hourly (for this target)."""
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


def setup_schedule(script_path: str, target_dir: str = "") -> bool:
    """Create the hourly scheduled job. Return True on success."""
    python_exe = get_python_exe()
    system = platform.system()
    display_path = script_path.replace("\\", "/")
    target = target_dir or "/path/to/spots"
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
    <string>{target}</string>
  </array>
  <key>StartInterval</key><integer>3600</integer>
  <key>RunAtLoad</key><true/>
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
        cron_line = f'0 * * * * {python_exe} "{display_path}" "{target}"'
        ok, existing = run_cmd(["crontab", "-l"])
        if not ok and "no crontab" not in (existing or "").lower():
            print(f"Could not read crontab: {existing}")
            return False
        lines = [s for s in (existing or "").splitlines() if s.strip()] if ok else []
        if any(display_path in line for line in lines):
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
        tr = f'"{python_exe}" "{script_path}" "{target}"'
        ok, out = run_cmd(["schtasks", "/create", "/tn", WINDOWS_TASK_NAME, "/tr", tr, "/sc", "hourly", "/f"])
        if not ok:
            print(f"schtasks failed (may need Administrator): {out}")
            return False
        print("Hourly task created in Task Scheduler.")
        return True
    return False


def print_schedule_instructions(script_path: str, target_dir: str = "") -> None:
    """Print OS-specific instructions to run this script as an hourly job."""
    python_exe = get_python_exe()
    system = platform.system()
    display_path = script_path.replace("\\", "/")
    # If we have a target dir, show it in the command; otherwise tell user to add path
    extra_args = f" \"{target_dir}\"" if target_dir else " [target_directory]"

    print("\n--- Run this script every hour (scheduled job) ---")
    if system == "Darwin":
        plist_name = "com.spots.sync-from-github.plist"
        plist_dir = os.path.expanduser("~/Library/LaunchAgents")
        plist_path = os.path.join(plist_dir, plist_name)
        args_in_plist = f'<string>{target_dir or "/path/to/spots"}</string>' if target_dir else "<string>/path/to/spots</string>"
        print(f"""
macOS (launchd):
1. Create the LaunchAgent plist file:
   mkdir -p "{plist_dir}"
   Edit {plist_path}. Use the paths below; set the third ProgramArgument to your sync target folder.

   <?xml version="1.0" encoding="UTF-8"?>
   <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
   <plist version="1.0">
   <dict>
     <key>Label</key><string>com.spots.sync-from-github</string>
     <key>ProgramArguments</key>
     <array>
       <string>{python_exe}</string>
       <string>{display_path}</string>
       {args_in_plist}
     </array>
     <key>StartInterval</key><integer>3600</integer>
     <key>RunAtLoad</key><true/>
   </dict>
   </plist>

2. Load and start: launchctl load "{plist_path}"
3. To stop: launchctl unload "{plist_path}"

Alternative (cron):
   0 * * * * {python_exe} "{display_path}" "{target_dir or "/path/to/spots"}"
""")
    elif system == "Linux":
        target_placeholder = target_dir or "/path/to/spots"
        print(f"""
Linux (cron):
1. crontab -e
2. Add (use your actual script and target directory):
   0 * * * * {python_exe} "{display_path}" "{target_placeholder}"

systemd user timer: create ~/.config/systemd/user/spots-sync.service with:
   [Unit]
   Description=Spots sync from GitHub
   [Service]
   Type=oneshot
   ExecStart={python_exe} {display_path} {target_placeholder}
3. Create spots-sync.timer with OnCalendar=hourly, then: systemctl --user enable --now spots-sync.timer
""")
    elif system == "Windows":
        target_placeholder = target_dir or "C:\\path\\to\\spots"
        print(f"""
Windows (Task Scheduler):
1. Open Task Scheduler (taskschd.msc). Create Task.
2. Triggers: Daily, repeat every 1 hour, indefinitely.
3. Actions: Start a program
   Program: {python_exe}
   Add arguments: "{display_path}" "{target_placeholder}"
   Start in: (folder containing the script)
4. Save.

schtasks example (run as Administrator):
   schtasks /create /tn "Spots Sync" /tr "\"{python_exe}\" \"{display_path}\" \"{target_placeholder}\"" /sc hourly
""")
    else:
        print(f"\nRun every hour: {python_exe} \"{display_path}\"{extra_args}\n")


def is_git_repo(path: str) -> bool:
    """Return True if path is the root of a git repo (and it's our remote)."""
    if not os.path.isdir(os.path.join(path, ".git")):
        return False
    ok, out = run_cmd(["git", "remote", "get-url", "origin"], cwd=path)
    return ok and "DougCarroll/spots" in (out or "")


def dir_is_empty(path: str) -> bool:
    """Return True if path doesn't exist or exists and has no visible files (except . and ..)."""
    if not os.path.isdir(path):
        return True
    return not any(
        p for p in os.listdir(path)
        if not p.startswith(".")
    )


def main() -> int:
    target = os.path.expanduser(
        os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
    )

    if not check_git():
        if prompt_install_git():
            if not try_install_git() and not check_git():
                return 1
        else:
            print("Exiting. Install Git and run this script again.")
            return 1
        if not check_git():
            return 1

    if is_git_repo(target):
        print("Existing clone detected. Pulling latest changes...")
        ok, out = run_cmd(["git", "pull", "origin", DEFAULT_BRANCH], cwd=target)
        if not ok:
            print("git pull failed:", out)
            return 1
        print("Done. Directory is up to date with GitHub.")
        script_path = os.path.abspath(__file__)
        if not is_scheduled(script_path, target):
            print_schedule_instructions(script_path, target)
            try:
                reply = input("Set up hourly job now? (y/n): ").strip().lower()
            except EOFError:
                reply = "n"
            if reply in ("y", "yes"):
                setup_schedule(script_path, target)
        return 0

    if not dir_is_empty(target):
        print(f"Target directory is not empty and is not an existing spots clone: {target}")
        print("Use an empty directory or a directory that was previously cloned from this repo.")
        return 1

    if not os.path.isdir(target):
        try:
            os.makedirs(target, exist_ok=True)
        except OSError as e:
            print(f"Cannot create directory {target}: {e}")
            return 1

    print(f"Cloning repository into {target}...")
    ok, out = run_cmd(["git", "clone", REPO_URL, target])
    if not ok:
        print("git clone failed:", out)
        return 1

    print("Done. Directory synced from GitHub.")
    script_path = os.path.abspath(__file__)
    if not is_scheduled(script_path, target):
        print_schedule_instructions(script_path, target)
        try:
            reply = input("Set up hourly job now? (y/n): ").strip().lower()
        except EOFError:
            reply = "n"
        if reply in ("y", "yes"):
            setup_schedule(script_path, target)
    return 0


if __name__ == "__main__":
    sys.exit(main())

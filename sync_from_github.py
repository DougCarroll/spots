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
    return 0


if __name__ == "__main__":
    sys.exit(main())

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
    return 0


if __name__ == "__main__":
    sys.exit(main())

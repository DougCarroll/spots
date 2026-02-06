# Spots

GPX waypoint files for navigation (Berry Islands, Exumas, Great Bahama Bank, etc.). This folder can stay in sync with GitHub so you have the same waypoints on more than one computer.

---

## What you need first

You need two free programs installed: **Git** and **Python 3**. The sync scripts will tell you if something is missing and can help you install it.

### Install Git and Python — by computer type

**On a Mac (macOS)**

1. **Git**  
   - Open the **Terminal** app (search for “Terminal” in Spotlight).  
   - Type: `xcode-select --install` and press Enter.  
   - Follow the prompts to install the “Command Line Tools.” That includes Git.

2. **Python 3**  
   - Macs often have Python already. In Terminal, type: `python3 --version`  
   - If you see a version number (e.g. 3.10), you’re set.  
   - If not, go to [python.org/downloads](https://www.python.org/downloads/) and download the Mac installer. Run it and leave the default options checked.

**On Windows**

1. **Git**  
   - Go to [git-scm.com/download/win](https://git-scm.com/download/win) and download the installer.  
   - Run it and use the default options (just keep clicking Next).

2. **Python 3**  
   - Go to [python.org/downloads](https://www.python.org/downloads/) and download the Windows installer.  
   - Run it. **Important:** on the first screen, check the box that says **“Add Python to PATH”**, then click “Install Now.”

**On Linux**

1. **Git and Python**  
   - Open a terminal, then run one of these (depending on your system):
   - **Ubuntu / Debian:** `sudo apt install git python3`
   - **Fedora:** `sudo dnf install git python3`
   - **Arch:** `sudo pacman -S git python`

---

## Two ways to use this folder

- **This computer has the main Spots folder** (you add or edit waypoints here)  
  → Use **“Sync this folder to GitHub”** so your changes are saved online.

- **This computer should have a copy that matches GitHub** (e.g. a second PC or boat laptop)  
  → Use **“Sync a folder from GitHub”** to download or update that copy.

---

## Sync this folder to GitHub

Use this on the computer where you keep your main Spots folder (the one you want to send *to* GitHub).

1. Put this whole **Spots** folder somewhere you’ll remember (e.g. Documents, Desktop, or iCloud).
2. Open a terminal:
   - **Mac:** Open **Terminal** and type: `cd ` (with a space), then drag the **Spots** folder onto the Terminal window and press Enter.
   - **Windows:** Open **Command Prompt** or **PowerShell**, type: `cd ` (with a space), then drag the **Spots** folder into the window and press Enter.
   - **Linux:** Open a terminal, then type: `cd ` and the path to the Spots folder (or drag the folder in).
3. Run the sync script:
   - **Mac / Linux:** type: `python3 sync_to_github.py` and press Enter.  
   - **Windows:** type: `python sync_to_github.py` and press Enter.
4. The first time, the script may ask you to install Git or log in to GitHub. Do what it says.
5. When it finishes, your folder is synced to GitHub. You can run the same command anytime you’ve added or changed waypoints.

**Optional — run every hour:** After a sync, the script may ask: “Set up hourly job now?” If you type **y** and press Enter, it will set up your computer to sync this folder to GitHub once every hour automatically.

---

## Sync a folder from GitHub (get or update a copy)

Use this on any computer where you want a **copy** of the Spots folder that stays in sync with GitHub (e.g. a second computer or a chart computer).

### First time — create a new folder that’s a copy of GitHub

1. Decide where you want the folder (e.g. **Desktop** or **Documents**). You’ll give that path in the next step.
2. Get the sync script onto this computer:
   - Either **clone the repo once:**  
     - **Mac / Linux:** In Terminal: `cd ~/Desktop` then `git clone https://github.com/DougCarroll/spots.git`  
     - **Windows:** In Command Prompt: `cd Desktop` then `git clone https://github.com/DougCarroll/spots.git`  
     - That creates a folder named **spots** with all the files and the script inside.
   - Or **download** the repo from GitHub (green “Code” → “Download ZIP”), unzip it, and remember where you put it.
3. Open a terminal in that folder (same way as in “Sync this folder to GitHub” — `cd` into the folder).
4. Run:
   - **Mac / Linux:** `python3 sync_from_github.py /path/to/where/you/want/the/copy`  
     Example: `python3 sync_from_github.py ~/Desktop/SpotsCopy`  
   - **Windows:** `python sync_from_github.py C:\Users\YourName\Desktop\SpotsCopy`  
     (Use your real username and path.)
5. The script will create that folder (if needed) and put a full copy from GitHub there.

### Later — update that copy

1. Open a terminal and go into the **copy** folder (the one you created with the script).
2. Run:
   - **Mac / Linux:** `python3 sync_from_github.py`  
   - **Windows:** `python sync_from_github.py`
3. The script will pull the latest changes from GitHub into that folder.

**Optional — run every hour:** After a sync, if the script asks “Set up hourly job now?” and you type **y**, it will update that folder from GitHub every hour automatically.

---

## Remove the “every hour” sync

If you said yes to the hourly job and later want to turn it off:

1. Open a terminal and go into the **Spots** folder (the one that contains `remove_schedule.py`).
2. Run:
   - **Mac / Linux:** `python3 remove_schedule.py`  
   - **Windows:** `python remove_schedule.py`
3. That removes the scheduled task on this computer. Your files are not deleted.

---

## Quick reference

| Goal | What to run |
|------|-------------|
| This computer has the main folder; send changes to GitHub | `python3 sync_to_github.py` (Mac/Linux) or `python sync_to_github.py` (Windows) |
| Get or update a copy from GitHub | `python3 sync_from_github.py` or `python3 sync_from_github.py /path/to/copy` (Mac/Linux); same with `python` on Windows |
| Stop the hourly sync on this computer | `python3 remove_schedule.py` (Mac/Linux) or `python remove_schedule.py` (Windows) |

Repo: [github.com/DougCarroll/spots](https://github.com/DougCarroll/spots)

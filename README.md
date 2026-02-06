# Spots

GPX waypoint files for navigation (Berry Islands, Exumas, Great Bahama Bank, etc.). You can keep a copy of this folder on your computer that stays in sync with the latest waypoints on GitHub.

---

## What you need first

You need two free programs installed: **Git** and **Python 3**. The sync script will tell you if something is missing and can help you install it.

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

## Get a copy of the Spots folder (first time)

1. Decide where you want the folder (e.g. **Desktop** or **Documents**). You’ll give that path in the next step.
2. Get the sync script onto this computer:
   - **Mac / Linux:** Open Terminal. Type: `cd ~/Desktop` and press Enter. Then type: `git clone https://github.com/DougCarroll/spots.git` and press Enter. That creates a folder named **spots** with all the files and the script inside.
   - **Windows:** Open Command Prompt or PowerShell. Type: `cd Desktop` and press Enter. Then type: `git clone https://github.com/DougCarroll/spots.git` and press Enter. That creates a folder named **spots** with all the files and the script inside.
   - **Alternative:** On GitHub, click the green **Code** button → **Download ZIP**. Unzip the file and remember where you put the **spots** folder.
3. Open a terminal in that **spots** folder:
   - **Mac:** In Terminal, type: `cd ` (with a space), then drag the **spots** folder onto the Terminal window and press Enter.
   - **Windows:** In Command Prompt, type: `cd ` (with a space), then drag the **spots** folder into the window and press Enter.
   - **Linux:** In the terminal, type: `cd ` and the path to the spots folder (or drag the folder in).
4. Run the sync script to create your copy:
   - **Mac / Linux:** `python3 sync_from_github.py ~/Desktop/SpotsCopy`  
     (You can change `SpotsCopy` to any folder name you like, and use a different path like `~/Documents/Spots` if you prefer.)
   - **Windows:** `python sync_from_github.py C:\Users\YourName\Desktop\SpotsCopy`  
     (Replace `YourName` with your Windows username. You can use a different folder name or path.)
5. The script will create that folder and put a full copy from GitHub there. Your waypoint files will be inside.

---

## Update your copy (get the latest from GitHub)

Whenever you want to refresh your copy with the latest waypoints:

1. Open a terminal and go into the **spots** folder (the one that contains `sync_from_github.py` — the one you cloned or downloaded, not necessarily the copy folder).
2. Run:
   - **Mac / Linux:** `python3 sync_from_github.py`  
     (If your copy is in a specific place, you can add it: `python3 sync_from_github.py ~/Desktop/SpotsCopy`)
   - **Windows:** `python sync_from_github.py`  
     (Or add your copy path: `python sync_from_github.py C:\Users\YourName\Desktop\SpotsCopy`)
3. The script will update that copy with the latest changes from GitHub.

**Optional — run every hour:** After a sync, the script may ask: “Set up hourly job now?” If you type **y** and press Enter, your computer will update your copy from GitHub once every hour automatically.

---

## Remove the “every hour” sync

If you set up the hourly update and later want to turn it off:

1. Open a terminal and go into the **spots** folder (the one that contains `remove_schedule.py`).
2. Run:
   - **Mac / Linux:** `python3 remove_schedule.py`  
   - **Windows:** `python remove_schedule.py`
3. That removes the scheduled task on this computer. Your files are not deleted.

---

## Quick reference

| Goal | What to run |
|------|-------------|
| Get or update my copy from GitHub | `python3 sync_from_github.py` or `python3 sync_from_github.py /path/to/my/copy` (Mac/Linux); same with `python` on Windows |
| Stop the hourly sync on this computer | `python3 remove_schedule.py` (Mac/Linux) or `python remove_schedule.py` (Windows) |

Repo: [github.com/DougCarroll/spots](https://github.com/DougCarroll/spots)

---

## Advanced Users

These steps are for users who **create or edit** the waypoints and want to **send changes to GitHub** (e.g. the person who maintains the main Spots folder).

### Sync this folder to GitHub

Use this on the computer where you keep your main Spots folder (the one you want to send *to* GitHub).

1. Put this whole **Spots** folder somewhere you’ll remember (e.g. Documents, Desktop, or iCloud).
2. Open a terminal:
   - **Mac:** Open **Terminal** and type: `cd ` (with a space), then drag the **Spots** folder onto the Terminal window and press Enter.
   - **Windows:** Open **Command Prompt** or **PowerShell**, type: `cd ` (with a space), then drag the **Spots** folder into the window and press Enter.
   - **Linux:** Open a terminal, then type: `cd ` and the path to the Spots folder (or drag the folder in).
3. Run the sync script:
   - **Mac / Linux:** `python3 sync_to_github.py`  
   - **Windows:** `python sync_to_github.py`
4. The first time, the script may ask you to install Git or log in to GitHub. Do what it says.
5. When it finishes, your folder is synced to GitHub. Run the same command anytime you’ve added or changed waypoints.

**Optional — run every hour:** After a sync, the script may ask: “Set up hourly job now?” If you type **y** and press Enter, it will set up your computer to sync this folder to GitHub once every hour automatically.

### Quick reference (sending to GitHub)

| Goal | What to run |
|------|-------------|
| Send this folder to GitHub | `python3 sync_to_github.py` (Mac/Linux) or `python sync_to_github.py` (Windows) |
| Stop the hourly sync | `python3 remove_schedule.py` (Mac/Linux) or `python remove_schedule.py` (Windows) |

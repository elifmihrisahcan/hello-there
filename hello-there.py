# HELLO THERE auto commit script

import datetime
import time
import os
from pathlib import Path
from git import Repo

TEXT = "HELLO THERE"

FONT = {
    "H": [
        [1,0,1],
        [1,0,1],
        [1,1,1],
        [1,0,1],
        [1,0,1],
    ],
    "E": [
        [1,1,1],
        [1,0,0],
        [1,1,0],
        [1,0,0],
        [1,1,1],
    ],
    "L": [
        [1,0,0],
        [1,0,0],
        [1,0,0],
        [1,0,0],
        [1,1,1],
    ],
    "O": [
        [1,1,1],
        [1,0,1],
        [1,0,1],
        [1,0,1],
        [1,1,1],
    ],
    "T": [
        [1,1,1],
        [0,1,0],
        [0,1,0],
        [0,1,0],
        [0,1,0],
    ],
    "R": [
        [1,1,0],
        [1,0,1],
        [1,1,0],
        [1,0,1],
        [1,0,1],
    ],
    " ": [
        [0],
        [0],
        [0],
        [0],
        [0],
    ],
}

def build_pattern_matrix(text):
    rows = [[] for _ in range(5)]
    chars = list(text.upper())
    last = len(chars) - 1
    for i,ch in enumerate(chars):
        glyph = FONT[ch]
        for r in range(5):
            rows[r].extend(glyph[r])
        if i != last and ch != " ":
            for r in range(5):
                rows[r].append(0)
    while all(r and r[-1] == 0 for r in rows):
        for r in range(5):
            rows[r].pop()
    width = len(rows[0])
    empty = [0] * width
    full = [empty[:]]
    full.extend(rows)
    full.append(empty[:])
    return full

def compute_commit_dates(text,year):
    pattern = build_pattern_matrix(text)
    rows = len(pattern)
    cols = len(pattern[0])
    jan1 = datetime.date(year,1,1)
    start = jan1
    while start.weekday() != 6:
        start += datetime.timedelta(days=1)
    dates = set()
    for r in range(rows):
        for c in range(cols):
            if pattern[r][c] == 1:
                day = start + datetime.timedelta(weeks=c,days=r)
                dates.add(day)
    return dates

def setup_ssh_for_git(repo_path):
    """Configure git to use SSH for GitHub operations"""
    repo = Repo(repo_path)
    
    # Get the SSH key path (default location on AWS/Linux)
    ssh_key_path = os.path.expanduser("~/.ssh/id_rsa")
    
    # Check if SSH key exists, if not try id_ed25519
    if not os.path.exists(ssh_key_path):
        ssh_key_path = os.path.expanduser("~/.ssh/id_ed25519")
    
    if not os.path.exists(ssh_key_path):
        print(f"Warning: SSH key not found at {ssh_key_path}")
        print("Please ensure your SSH key is set up correctly")
        return
    
    # Set git config to use SSH
    with repo.git.custom_environment(GIT_SSH_COMMAND=f'ssh -i {ssh_key_path} -o StrictHostKeyChecking=no'):
        # Update remote URL to use SSH if it's not already
        try:
            origin = repo.remote("origin")
            url = origin.url
            # Convert HTTPS URL to SSH if needed
            if url.startswith("https://"):
                # Convert https://github.com/user/repo.git to git@github.com:user/repo.git
                url = url.replace("https://github.com/", "git@github.com:")
                url = url.replace(".git", "") + ".git"
                origin.set_url(url)
                print(f"Updated remote URL to SSH: {url}")
        except Exception as e:
            print(f"Warning: Could not update remote URL: {e}")
    
    return ssh_key_path

def make_commit_if_needed():
    """Check if a commit is needed today and make it"""
    today = datetime.date.today()
    year = today.year
    commit_dates = compute_commit_dates(TEXT, year)
    
    if today not in commit_dates:
        print(f"{today.isoformat()}: No commit needed for today")
        return False
    
    path = Path(__file__).resolve().parent
    repo = Repo(path)
    
    # Setup SSH for git operations
    ssh_key_path = setup_ssh_for_git(path)
    
    log_file = path / "hello_there_log.txt"
    with log_file.open("a", encoding="utf8") as f:
        f.write(f"Commit for HELLO THERE pattern on {today.isoformat()}\n")
    
    repo.index.add([str(log_file)])
    repo.index.commit(f"HELLO THERE auto commit {today.isoformat()}")
    
    # Push using SSH
    origin = repo.remote("origin")
    with repo.git.custom_environment(GIT_SSH_COMMAND=f'ssh -i {ssh_key_path} -o StrictHostKeyChecking=no'):
        origin.push()
    
    print(f"{today.isoformat()}: Successfully committed and pushed!")
    return True

def main():
    """Main loop that runs continuously and checks every 24 hours"""
    print("Starting HELLO THERE auto-commit script...")
    print("Script will check every 24 hours for commits needed")
    print("Press Ctrl+C to stop\n")
    
    # Run immediately on startup
    make_commit_if_needed()
    
    # Then check every 24 hours
    while True:
        try:
            # Wait 24 hours (86400 seconds)
            print(f"Waiting 24 hours until next check...")
            time.sleep(86400)
            
            # Check and commit if needed
            make_commit_if_needed()
            
        except KeyboardInterrupt:
            print("\nScript stopped by user")
            break
        except Exception as e:
            print(f"Error occurred: {e}")
            print("Continuing after 1 hour...")
            time.sleep(3600)  # Wait 1 hour before retrying on error

if __name__ == "__main__":
    main()
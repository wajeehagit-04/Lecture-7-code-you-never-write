import os
import hashlib
from collections import defaultdict
from pathlib import Path

# --- CONFIGURATION ---
# Path to your downloads folder (Automatically finds it on Windows/Mac/Linux)
DOWNLOADS_DIR = Path.home() / "Downloads"
LARGE_FILE_THRESHOLD_MB = 500  # Flag files larger than this

# File type groupings
FILE_TYPES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic"],
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".csv", ".md"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".wmv", ".flv"],
    "Audio": [".mp3", ".wav", ".m4a", ".flac", ".aac"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "Executables": [".exe", ".dmg", ".pkg", ".msi", ".deb", ".sh"]
}

def get_file_hash(file_path):
    """Generates a hash for a file. Fast-hashes large files to save time."""
    hasher = hashlib.md5()
    try:
        file_size = file_path.stat().st_size
        with open(file_path, 'rb') as f:
            # If file is larger than 100MB, hash the beginning and end only
            if file_size > 100 * 1024 * 1024:
                hasher.update(f.read(5 * 1024 * 1024))
                f.seek(-5 * 1024 * 1024, os.SEEK_END)
                hasher.update(f.read(5 * 1024 * 1024))
            else:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def plan_organization():
    print(f"Scanning: {DOWNLOADS_DIR}\nGathering data... Please wait.\n")
    
    files = [p for p in DOWNLOADS_DIR.iterdir() if p.is_file() and not p.name.startswith('.')]
    
    hashes = defaultdict(list)
    names = defaultdict(list)
    large_files = []
    
    # Analyze files
    for file_path in files:
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > LARGE_FILE_THRESHOLD_MB:
            large_files.append((file_path, size_mb))
            
        # Track by name duplicate
        names[file_path.name.lower()].append(file_path)
        
        # Track by content duplicate
        f_hash = get_file_hash(file_path)
        if f_hash:
            hashes[f_hash].append(file_path)

    # Build the action items
    actions_move = {}    # file_path -> target_folder
    actions_delete = []  # list of file_paths (duplicates)
    
    # 1. Process Content Duplicates
    seen_duplicates = set()
    for f_hash, paths in hashes.items():
        if len(paths) > 1:
            # Keep the oldest or shortest named one, flag the rest for deletion
            paths.sort(key=lambda p: (len(p.name), p.stat().st_mtime))
            keeper = paths[0]
            for duplicate in paths[1:]:
                actions_delete.append(duplicate)
                seen_duplicates.add(duplicate)

    # 2. Process Name Duplicates (that might have skipped content checks)
    for name, paths in names.items():
        if len(paths) > 1:
            paths.sort(key=lambda p: p.stat().st_mtime)
            for duplicate in paths[1:]:
                if duplicate not in seen_duplicates:
                    actions_delete.append(duplicate)
                    seen_duplicates.add(duplicate)

    # 3. Process Sorting for remaining files
    for file_path in files:
        if file_path in seen_duplicates:
            continue
            
        ext = file_path.suffix.lower()
        target_dir = "Others"
        for folder_name, extensions in FILE_TYPES.items():
            if ext in extensions:
                target_dir = folder_name
                break
                
        actions_move[file_path] = DOWNLOADS_DIR / target_dir

    # --- SHOW THE PLAN ---
    print("=" * 60)
    print("                      PROPOSED PLAN                     ")
    print("=" * 60)
    
    if large_files:
        print(f"\n⚠️  VERY LARGE FILES FLAG (>{LARGE_FILE_THRESHOLD_MB}MB):")
        for p, size in large_files:
            print(f"   • [{size:.1f} MB] {p.name}")
            
    print(f"\n🛑 DUPLICATES TO REMOVE ({len(actions_delete)} files):")
    if not actions_delete:
        print("   None found.")
    for p in actions_delete:
        print(f"   • [DELETE/ARCHIVE] {p.name}")

    print(f"\n📂 FILES TO GROUP BY TYPE ({len(actions_move)} files):")
    if not actions_move:
        print("   None to move.")
    for p, target in actions_move.items():
        print(f"   • {p.name}  --->  {target.name}/")
        
    print("\n" + "=" * 60)
    
    # --- WAITING FOR APPROVAL ---
    confirm = input("\nDo you approve this plan? Type 'yes' to execute, or anything else to abort: ")
    
    if confirm.lower() == 'yes':
        execute_plan(actions_move, actions_delete)
    else:
        print("\nExecution aborted. No files were touched.")

def execute_plan(moves, deletes):
    print("\nExecuting plan...")
    
    # Create duplicate archive folder instead of instant hard deletion for absolute safety
    dup_dir = DOWNLOADS_DIR / "_Duplicates"
    if deletes:
        dup_dir.mkdir(exist_ok=True)
        
    # Run deletions (moves to _Duplicates)
    for file_path in deletes:
        try:
            target = dup_dir / file_path.name
            # Handle name collisions inside the duplicate folder
            counter = 1
            while target.exists():
                target = dup_dir / f"{file_path.stem}_{counter}{file_path.suffix}"
                counter += 1
            file_path.rename(target)
            print(f"Archived duplicate: {file_path.name}")
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")

    # Run moves
    for file_path, target_folder in moves.items():
        try:
            target_folder.mkdir(exist_ok=True)
            target = target_folder / file_path.name
            
            # Prevent overwriting if a file already exists in the target folder
            counter = 1
            while target.exists():
                target = target_folder / f"{file_path.stem}_{counter}{file_path.suffix}"
                counter += 1
                
            file_path.rename(target)
            print(f"Moved: {file_path.name} -> {target_folder.name}/")
        except Exception as e:
            print(f"Error moving {file_path.name}: {e}")
            
    print("\nDone! Your downloads folder is organized.")

if __name__ == "__main__":
    plan_organization()
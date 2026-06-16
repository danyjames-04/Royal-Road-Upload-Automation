"""
Chapter Fuser
==============
Merges multiple chapter .txt files into one combined .txt file.
Original files are NOT modified.

Put all your chapter .txt files in the INPUT_FOLDER,
then run: python fuse_chapters.py
"""

import os
import glob

# ============================================================
#  CONFIG
# ============================================================

INPUT_FOLDER = "chapters"           # Folder containing your chapter .txt files
OUTPUT_FILE  = "fused_chapters.txt" # Output combined file name

# ============================================================

def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()

def main():
    # Find and sort all txt files
    files = sorted(glob.glob(os.path.join(INPUT_FOLDER, "*.txt")))

    if not files:
        print(f"ERROR: No .txt files found in '{INPUT_FOLDER}' folder.")
        return

    print(f"Found {len(files)} file(s) to fuse:")
    for f in files:
        print(f"  {os.path.basename(f)}")

    print(f"\nFusing into: {OUTPUT_FILE}")

    combined = []
    for i, filepath in enumerate(files, 1):
        filename = os.path.basename(filepath)
        try:
            content = read_file(filepath)
            sep = "=" * 60
            combined.append(f"{sep}\n{content}\n")
            print(f"  ✓ [{i}/{len(files)}] {filename}")
        except Exception as e:
            print(f"  ✗ [{i}/{len(files)}] {filename} — Failed: {e}")

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"Total chapters: {len(combined)}\n")
        f.write(f"Source folder: {INPUT_FOLDER}\n\n")
        f.write("\n".join(combined))

    print(f"\nDone! Combined file saved as: {OUTPUT_FILE}")
    print(f"Original files in '{INPUT_FOLDER}' are untouched.")

if __name__ == "__main__":
    main()

# Royal Road Bulk Chapter Uploader
## Setup Guide (Windows)

---

### STEP 1 — Install Python
1. Go to https://www.python.org/downloads/
2. Download the latest version (3.11 or newer)
3. Run the installer — **check the box that says "Add Python to PATH"**
4. Click Install Now

---

### STEP 2 — Install the required tools
1. Press `Win + R`, type `cmd`, press Enter
2. Paste this and press Enter:
   ```
   pip install playwright && python -m playwright install chromium
   ```
3. Wait for it to finish (may take a minute)

---

### STEP 3 — Set up your chapter files
1. Open the `chapters` folder (included here)
2. Create one `.txt` file per chapter, named like:[Use Chapter_formatter.html]
   ```
   chapter_01.txt
   chapter_02.txt
   chapter_03.txt
   ...
   ```
3. Each file must follow this format:
   ```
   Your Chapter Title Here
   
   Your chapter content starts here. You can have as many
   paragraphs as you want. Just make sure the title is on
   the very first line, with a blank line after it.
   ```

A sample file `chapter_01.txt` is already in the folder so you can see the format.

---

### STEP 4 — Edit the script config
Open `royalroad_bulk_upload.py` in Notepad (or any text editor).

Find the CONFIG section near the top and fill in:
```python
FICTION_ID = "123456"
```

**How to find your FICTION_ID:**
- Go to your story on Royal Road
- Look at the URL: `royalroad.com/fiction/123456/your-story-name`
- The number after `/fiction/` is your ID

---

### STEP 5 — Run the script
1. Open Command Prompt in the folder where you saved the script
   - You can do this by holding Shift and right-clicking the folder, then choosing "Open PowerShell window here"
2. Type:
   ```
   python royalroad_bulk_upload.py
   ```
3. A browser window will open — you can watch it log in and create each draft [Login easier with direct login instead of Google Auth]
4. When it's done, it will print a summary of how many chapters were saved

---

### After it finishes
Go to your Royal Road author dashboard and you'll see all your chapters saved as drafts, ready for you to review and schedule/publish whenever you want.

---

### Troubleshooting
| Problem | Fix |
|---|---|
| `python not found` | Reinstall Python and check "Add to PATH" |
| `pip not found` | Same as above |
| Login fails | Double-check your email/password in the config |
| Chapter skipped | Make sure the .txt file has a title on line 1 |
| Editor not found | Royal Road may have updated — let me know and I'll fix the script |

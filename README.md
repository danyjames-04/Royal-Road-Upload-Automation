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
1. Clone or download this repository
2. Inside the repo, you'll find a `chapters/` folder — this is where your chapter files go
   > If it's missing, create it manually: right-click → New Folder → name it `chapters`
3. Use **Chapter_formatter.html** to generate your chapter files — it saves them in the correct format and naming automatically
4. Move the downloaded `.txt` files into the `chapters/` folder:
   ```
   chapters/
   ├── chapter_01.txt
   ├── chapter_02.txt
   ├── chapter_03.txt
   └── ...
   ```
5. Each file must follow this format:
   ```
   Your Chapter Title Here

   Your chapter content starts here. You can have as many
   paragraphs as you want. Just make sure the title is on
   the very first line, with a blank line after it.
   ```
A sample file `chapters/chapter_01.txt` is already in the folder so you can see the format.

> **Note:** The `chapters/` folder is listed in `.gitignore` — your chapter files will not be uploaded to GitHub. Only the folder itself (with the sample) is tracked.

---

### STEP 4 — Edit the script config
Open `royalroad_bulk_upload.py` in Notepad (or any text editor).

Find the CONFIG section near the top and fill in:
```python
FICTION_ID   = "123456"       # Your fiction ID (see below)
START_DATE   = "2025-07-01"   # Date to publish the first chapter (YYYY-MM-DD)
RELEASE_TIME = "12:00"        # Time to publish each chapter (24-hour format, e.g. 14:30 = 2:30 PM)
```

**How to find your FICTION_ID:**
- Go to your story on Royal Road
- Look at the URL: `royalroad.com/fiction/123456/your-story-name`
- The number after `/fiction/` is your ID

**How scheduling works:**
- Chapter 1 is scheduled for `START_DATE` at `RELEASE_TIME`
- Chapter 2 is scheduled for the next day at the same time
- Chapter 3 the day after that, and so on — one chapter per day automatically
- Before uploading, the script prints a full schedule preview so you can confirm the dates look right

**Example:**
```
START_DATE   = "2025-07-01"
RELEASE_TIME = "12:00"
```
```
Chapter 1  →  2025-07-01 12:00
Chapter 2  →  2025-07-02 12:00
Chapter 3  →  2025-07-03 12:00
...
```

---

### STEP 5 — Run the script
1. Open Command Prompt in the folder where you saved the script
   - You can do this by holding Shift and right-clicking the folder, then choosing "Open PowerShell window here"
2. Type:
   ```
   python royalroad_bulk_upload.py
   ```
3. A browser window will open — log in with your Royal Road account (direct login is easier than Google Auth)
4. Once logged in, switch back to Command Prompt and press Enter
5. The script will create each chapter as a draft with its publish date already set
6. When it's done, it prints a summary of how many chapters were saved

---

### After it finishes
Go to your Royal Road author dashboard and you'll see all your chapters saved as drafts with their scheduled publish dates already filled in. They will go live automatically on their scheduled dates — no further action needed.

---

### Troubleshooting
| Problem | Fix |
|---|---|
| `python not found` | Reinstall Python and check "Add to PATH" |
| `pip not found` | Same as above |
| Login page times out | Wait a moment and try again — Royal Road may be slow |
| Chapter skipped | Make sure the .txt file has a title on line 1 |
| Schedule date wrong | Check `START_DATE` format is `YYYY-MM-DD` and `RELEASE_TIME` is `HH:MM` |
| Editor not found | Royal Road may have updated — open an issue and I'll fix the script |

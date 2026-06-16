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
   pip install playwright python-dotenv tkcalendar && python -m playwright install chromium
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
### STEP 4 — Configure the `.env` file
Open the `.env` file in the repo root and fill in your details:
```
FICTION_ID=123456
CHAPTERS_FOLDER=chapters
RELEASE_TIME=21:30
DELAY_BETWEEN_CHAPTERS=3

RR_EMAIL=your@email.com
RR_PASSWORD=yourpassword
```

**How to find your FICTION_ID:**
- Go to your story on Royal Road
- Look at the URL: `royalroad.com/fiction/123456/your-story-name`
- The number after `/fiction/` is your ID

> **Note:** `.env` is listed in `.gitignore` — your credentials will never be committed to GitHub.

You can also set `START_DATE` (YYYY-MM-DD) and `FREQ_DAYS` (number) here to skip those prompts each run.
---
### STEP 5 — Run the script
1. Open Command Prompt in the folder where you saved the script
   - Hold Shift and right-click the folder → "Open PowerShell window here"
2. Type:
   ```
   python royalroad_bulk_upload.py
   ```
3. The script will ask you a few questions (start date, release frequency, etc.)
   - A **calendar popup** will appear for picking the start date — just click a day and confirm
   - Press Enter to accept any `[default]` value shown in brackets
4. A browser window opens and logs in automatically using your `.env` credentials
5. The script creates each chapter as a scheduled draft — you can watch it work
---
### After it finishes
Go to your Royal Road author dashboard and you'll see all your chapters saved as drafts, ready for you to review and publish whenever you want.
---
### Troubleshooting
| Problem | Fix |
|---|---|
| `python not found` | Reinstall Python and check "Add to PATH" |
| `pip not found` | Same as above |
| `No module named dotenv` | Run `pip install python-dotenv` |
| `No module named tkcalendar` | Run `pip install tkcalendar` |
| Auto-login fails | Check your email/password in `.env`; script will fall back to manual login |
| Chapter skipped | Make sure the .txt file has a title on line 1 |
| Editor not found | Royal Road may have updated their site — open an issue and I'll fix the script |
| `buttons_screenshot.png` created | The save-draft button wasn't found — check the screenshot for what's on screen |

"""
Royal Road Bulk Chapter Draft Creator with Auto-Scheduling
===========================================================
SETUP:
1. Install Python: https://www.python.org/downloads/
2. Open Command Prompt and run:
      pip install playwright
      python -m playwright install chromium
3. Put your chapter .txt files in the 'chapters' folder
4. Run: python royalroad_bulk_upload.py

CHAPTER FILE FORMAT:
   Line 1:  Chapter Title
   Line 2:  (blank)
   Line 3+: Chapter content
"""

import os
import time
import glob
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright

# ============================================================
#  CONFIG
# ============================================================

FICTION_ID       = "148722"
CHAPTERS_FOLDER  = "chapters"
DELAY_BETWEEN_CHAPTERS = 3  # seconds between uploads

# Scheduling — chapter 1 on START_DATE, chapter 2 one day later, etc.
START_DATE   = "2026-06-20"   # Format: YYYY-MM-DD
RELEASE_TIME = "21:30"        # Format: HH:MM (24-hour)

# ============================================================

def read_chapter_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    title = ""
    content_start = 0
    for i, line in enumerate(lines):
        if line.strip():
            title = line.strip()
            content_start = i + 1
            break
    while content_start < len(lines) and not lines[content_start].strip():
        content_start += 1
    content = "\n".join(lines[content_start:]).strip()
    return title, content


def create_draft(page, fiction_id, title, content, publish_datetime):
    url = f"https://www.royalroad.com/author-dashboard/chapters/new/{fiction_id}"
    page.goto(url, wait_until="commit", timeout=0)
    time.sleep(5)

    # Fill title
    page.wait_for_selector("input[name='Title']", timeout=15000)
    page.fill("input[name='Title']", title)
    print(f"    Title: {title}")

    # Fill TinyMCE content editor
    content_escaped = content.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "<br>").replace("\r", "")
    injected = page.evaluate(f"""
        () => {{
            if (typeof tinymce !== 'undefined') {{
                var editors = tinymce.editors;
                for (var i = 0; i < editors.length; i++) {{
                    var ed = editors[i];
                    if (ed.id && ed.id.toLowerCase().includes('content')) {{
                        ed.setContent('{content_escaped}');
                        return 'tinymce:' + ed.id;
                    }}
                }}
                if (editors.length > 0) {{
                    editors[0].setContent('{content_escaped}');
                    return 'tinymce:first';
                }}
            }}
            var iframe = document.querySelector('iframe#contentEditor_ifr');
            if (iframe) {{
                iframe.contentDocument.body.innerHTML = '{content_escaped}';
                return 'iframe';
            }}
            return 'not_found';
        }}
    """)
    print(f"    Content injected via: {injected}")
    if injected == 'not_found':
        raise Exception("Could not find TinyMCE editor")

    # Set scheduled release date/time
    # Royal Road's scheduled release field is a datetime-local input
    dt_str = publish_datetime.strftime("%Y-%m-%dT%H:%M")
    scheduled = page.evaluate(f"""
        () => {{
            // Try common selectors for the scheduled release input
            var selectors = [
                'input[name="PublishDate"]',
                'input[name="scheduledDate"]',
                'input[type="datetime-local"]',
                'input[id*="publish" i]',
                'input[id*="schedule" i]',
                'input[name*="publish" i]',
                'input[name*="schedule" i]'
            ];
            for (var s of selectors) {{
                var el = document.querySelector(s);
                if (el) {{
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                    nativeInputValueSetter.call(el, '{dt_str}');
                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    return s;
                }}
            }}
            return 'not_found';
        }}
    """)
    print(f"    Schedule set to {publish_datetime.strftime('%Y-%m-%d %H:%M')} via: {scheduled}")

    time.sleep(1)

    # Save as Draft
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)

    saved = False
    for sel in [
        "button:has-text('Save as Draft')",
        "input[value='Save as Draft']",
        "button[title*='Draft' i]",
        "input[value*='Draft']",
        "button:has-text('Draft')",
        ".btn:has-text('Draft')",
    ]:
        try:
            el = page.locator(sel).first
            if el.count() > 0:
                el.click()
                saved = True
                print(f"    Saved via: {sel}")
                break
        except:
            continue

    if not saved:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        page.screenshot(path="buttons_screenshot.png")
        raise Exception("Could not find Save as Draft button — check buttons_screenshot.png")

    page.wait_for_timeout(3000)
    print(f"  ✓ Draft saved: {title} — scheduled for {publish_datetime.strftime('%Y-%m-%d %H:%M')}")


def main():
    files = sorted(glob.glob(os.path.join(CHAPTERS_FOLDER, "*.txt")))

    if not files:
        print(f"ERROR: No .txt files found in '{CHAPTERS_FOLDER}' folder.")
        return

    # Build schedule — one chapter per day starting from START_DATE
    start_dt = datetime.strptime(f"{START_DATE} {RELEASE_TIME}", "%Y-%m-%d %H:%M")
    schedule = [start_dt + timedelta(days=i) for i in range(len(files))]

    print(f"Found {len(files)} chapter file(s).")
    print(f"Fiction ID: {FICTION_ID}")
    print(f"Schedule preview:")
    for i, (f, dt) in enumerate(zip(files, schedule), 1):
        print(f"  Chapter {i}: {os.path.basename(f)} → {dt.strftime('%Y-%m-%d %H:%M')}")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            slow_mo=50
        )
        page = browser.new_page()

        print("A browser window has opened.")
        print("Please log in to Royal Road with your Google account.")
        print("Once you are on your dashboard, come back here and press Enter.\n")
        page.goto("https://www.royalroad.com/account/login", wait_until="commit", timeout=0)

        input("Press Enter once you are logged in...")
        print("\nStarting uploads...\n")

        failed = []
        for i, (filepath, publish_dt) in enumerate(zip(files, schedule), 1):
            filename = os.path.basename(filepath)
            print(f"[{i}/{len(files)}] Processing: {filename}")
            try:
                title, content = read_chapter_file(filepath)
                if not title or not content:
                    print(f"  ✗ Skipped (missing title or content)")
                    failed.append(filename)
                    continue
                create_draft(page, FICTION_ID, title, content, publish_dt)
                time.sleep(DELAY_BETWEEN_CHAPTERS)
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                failed.append(filename)

        browser.close()

    print("\n=============================")
    print(f"Done! {len(files) - len(failed)}/{len(files)} chapters scheduled as drafts.")
    if failed:
        print(f"\nFailed files:")
        for f in failed:
            print(f"  - {f}")
    print(f"\nCheck your drafts at:")
    print(f"  https://www.royalroad.com/fiction/{FICTION_ID}/chapters")


if __name__ == "__main__":
    main()

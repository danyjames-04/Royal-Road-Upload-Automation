"""
Royal Road Bulk Chapter Draft Creator
======================================
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
from playwright.sync_api import sync_playwright

# ============================================================
#  CONFIG
# ============================================================

FICTION_ID = "170223"
CHAPTERS_FOLDER = "chapters"
DELAY_BETWEEN_CHAPTERS = 3

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


def create_draft(page, fiction_id, title, content):
    url = f"https://www.royalroad.com/author-dashboard/chapters/new/{fiction_id}"
    page.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)  # Wait for TinyMCE to fully load

    # Fill title
    page.wait_for_selector("input[name='Title']", timeout=15000)
    page.fill("input[name='Title']", title)
    print(f"    Title filled: {title}")

    # Fill TinyMCE content editor via its iframe
    # TinyMCE renders inside an iframe with id="contentEditor_ifr"
    content_escaped = content.replace("'", "\\'").replace("\n", "<br>")
    injected = page.evaluate(f"""
        () => {{
            // Try TinyMCE API first
            if (typeof tinymce !== 'undefined') {{
                var editors = tinymce.editors;
                for (var i = 0; i < editors.length; i++) {{
                    var ed = editors[i];
                    if (ed.id && ed.id.toLowerCase().includes('content')) {{
                        ed.setContent('{content_escaped}');
                        return 'tinymce:' + ed.id;
                    }}
                }}
                // fallback: use first non-notes editor
                if (editors.length > 0) {{
                    editors[0].setContent('{content_escaped}');
                    return 'tinymce:first';
                }}
            }}
            // Try iframe body directly
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

    time.sleep(1)

    # Click Save as Draft button (top right upload arrow button)
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)

    saved = False
    for sel in [
        "button:has-text('Save as Draft')",
        "input[value='Save as Draft']",
        "button[title*='Draft' i]",
        "button[title*='Save' i]",
        "input[value*='Draft']",
        "button:has-text('Draft')",
        ".btn:has-text('Draft')",
    ]:
        try:
            el = page.locator(sel).first
            if el.count() > 0:
                el.click()
                saved = True
                print(f"    Clicked: {sel}")
                break
        except:
            continue

    if not saved:
        # Screenshot bottom of page to see buttons
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
        page.screenshot(path="buttons_screenshot.png")
        raise Exception("Could not find Save as Draft button — check buttons_screenshot.png")

    page.wait_for_timeout(3000)
    print(f"  ✓ Saved draft: {title}")


def main():
    files = sorted(glob.glob(os.path.join(CHAPTERS_FOLDER, "*.txt")))

    if not files:
        print(f"ERROR: No .txt files found in '{CHAPTERS_FOLDER}' folder.")
        return

    print(f"Found {len(files)} chapter file(s).")
    print(f"Uploading to fiction ID: {FICTION_ID}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            slow_mo=50
        )
        page = browser.new_page()

        # Manual login
        print("A browser window has opened.")
        print("Please log in to Royal Road with your Google account.")
        print("Once you are on your dashboard, come back here and press Enter.\n")
        page.goto("https://www.royalroad.com/account/login", wait_until="domcontentloaded", timeout=60000)

        input("Press Enter once you are logged in...")
        print("\nStarting uploads...\n")

        failed = []
        for i, filepath in enumerate(files, 1):
            filename = os.path.basename(filepath)
            print(f"[{i}/{len(files)}] Processing: {filename}")
            try:
                title, content = read_chapter_file(filepath)
                if not title or not content:
                    print(f"  ✗ Skipped (missing title or content)")
                    failed.append(filename)
                    continue
                create_draft(page, FICTION_ID, title, content)
                time.sleep(DELAY_BETWEEN_CHAPTERS)
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                failed.append(filename)

        browser.close()

    print("\n=============================")
    print(f"Done! {len(files) - len(failed)}/{len(files)} chapters saved as drafts.")
    if failed:
        print(f"\nFailed files:")
        for f in failed:
            print(f"  - {f}")
    print(f"\nCheck your drafts at:")
    print(f"  https://www.royalroad.com/fiction/{FICTION_ID}/chapters")


if __name__ == "__main__":
    main()

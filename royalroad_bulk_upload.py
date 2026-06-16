"""
Royal Road Bulk Chapter Draft Creator with Auto-Scheduling
===========================================================
SETUP:
1. Install Python: https://www.python.org/downloads/
2. Open Command Prompt and run:
      pip install playwright python-dotenv
      python -m playwright install chromium
3. Put your chapter .txt files in the 'chapters' folder (or set CHAPTERS_FOLDER in .env)
4. Edit .env with your Fiction ID and preferred defaults
5. Run: python royalroad_bulk_upload.py

CHAPTER FILE FORMAT:
   Line 1:  Chapter Title
   Line 2:  (blank)
   Line 3+: Chapter content

.ENV FILE (optional overrides):
   FICTION_ID              - Your Royal Road fiction ID
   CHAPTERS_FOLDER         - Folder containing chapter .txt files (default: chapters)
   RELEASE_TIME            - Default release time in HH:MM 24-hour format (default: 21:30)
   DELAY_BETWEEN_CHAPTERS  - Seconds to wait between uploads (default: 3)
"""

import os
import time
import glob
from datetime import datetime, timedelta
from pathlib import Path
from playwright.sync_api import sync_playwright

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # .env is optional; values will be prompted if missing


# ============================================================
#  HELPERS
# ============================================================

def prompt(label, default=None, required=True):
    """Prompt the user for input, showing the default if one exists."""
    if default:
        value = input(f"  {label} [{default}]: ").strip()
        return value if value else default
    else:
        while True:
            value = input(f"  {label}: ").strip()
            if value or not required:
                return value
            print("    (required — please enter a value)")


def prompt_int(label, default=None, min_val=1):
    while True:
        raw = prompt(label, default=str(default) if default is not None else None)
        try:
            val = int(raw)
            if val >= min_val:
                return val
            print(f"    (must be at least {min_val})")
        except ValueError:
            print("    (please enter a whole number)")


def pick_date_gui(title="Pick a date"):
    """Open a calendar popup. Returns 'YYYY-MM-DD' string, or None if unavailable/cancelled."""
    try:
        import tkinter as tk
        from tkcalendar import Calendar

        result = []

        def on_select():
            result.append(cal.selection_get().strftime("%Y-%m-%d"))
            root.destroy()

        def on_close():
            root.destroy()

        root = tk.Tk()
        root.title(title)
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", on_close)

        cal = Calendar(root, selectmode="day", date_pattern="yyyy-mm-dd")
        cal.pack(padx=12, pady=12)

        tk.Button(root, text="Confirm date", command=on_select, width=20).pack(pady=(0, 10))
        root.mainloop()

        return result[0] if result else None

    except ImportError:
        return None


def prompt_date(label, default=None):
    picked = pick_date_gui(label)
    if picked:
        print(f"  {label}: {picked}  (selected via calendar)")
        return picked

    # Fallback: typed input in dd/mm/yyyy
    while True:
        raw = prompt(f"{label} (dd/mm/yyyy)", default=default)
        # Accept dd/mm/yyyy or yyyy-mm-dd
        for fmt, out_fmt in [("%d/%m/%Y", "%Y-%m-%d"), ("%Y-%m-%d", "%Y-%m-%d")]:
            try:
                return datetime.strptime(raw, fmt).strftime(out_fmt)
            except ValueError:
                continue
        print("    (use dd/mm/yyyy format, e.g. 16/06/2026)")


def prompt_time(label, default=None):
    while True:
        raw = prompt(label, default=default)
        try:
            datetime.strptime(raw, "%H:%M")
            return raw
        except ValueError:
            print("    (use HH:MM 24-hour format, e.g. 21:30)")


def load_config():
    """Load config from .env with interactive fallback for missing values."""
    print("=" * 55)
    print("  Royal Road Bulk Upload — Configuration")
    print("=" * 55)
    print("  (Press Enter to accept a [default] value)\n")

    fiction_id = prompt(
        "Fiction ID",
        default=os.getenv("FICTION_ID"),
    )

    chapters_folder = prompt(
        "Chapters folder",
        default=os.getenv("CHAPTERS_FOLDER", "chapters"),
    )

    start_date = prompt_date(
        "Start date (first chapter release)",
        default=os.getenv("START_DATE"),
    )

    release_time = prompt_time(
        "Release time (HH:MM, 24-hour)",
        default=os.getenv("RELEASE_TIME", "21:30"),
    )

    freq_days = prompt_int(
        "Days between releases",
        default=int(os.getenv("FREQ_DAYS", "2")),
        min_val=1,
    )

    delay = prompt_int(
        "Delay between uploads (seconds)",
        default=int(os.getenv("DELAY_BETWEEN_CHAPTERS", "3")),
        min_val=0,
    )

    print()
    return {
        "fiction_id": fiction_id,
        "chapters_folder": chapters_folder,
        "start_date": start_date,
        "release_time": release_time,
        "freq_days": freq_days,
        "delay": delay,
    }


# ============================================================
#  CORE
# ============================================================

def login(page):
    """Auto-login using .env credentials, or wait for manual login."""
    email    = os.getenv("RR_EMAIL", "").strip()
    password = os.getenv("RR_PASSWORD", "").strip()

    page.goto("https://www.royalroad.com/account/login", wait_until="commit", timeout=0)

    if email and password:
        print("Auto-login: filling credentials ...")
        try:
            page.wait_for_selector("input[name='Email']", timeout=10000)
            page.fill("input[name='Email']", email)
            page.fill("input[name='Password']", password)

            # Click the login submit button that is inside the credentials form,
            # not the Google OAuth button which also has type="submit"
            submitted = False
            for sel in [
                "form:has(input[name='Email']) button[type='submit']",
                "form:has(input[name='Password']) button[type='submit']",
                "button:has-text('Login')",
                "button:has-text('Sign In')",
                "button:has-text('Log In')",
                "input[type='submit'][value*='Login' i]",
                "input[type='submit'][value*='Sign' i]",
            ]:
                try:
                    el = page.locator(sel).first
                    if el.count() > 0:
                        el.click()
                        submitted = True
                        break
                except:
                    continue

            if not submitted:
                raise Exception("Could not find the login submit button")

            page.wait_for_url(lambda url: "/account/login" not in url, timeout=15000)
            print("Auto-login: success.\n")
        except Exception as e:
            print(f"Auto-login failed ({e}).")
            print("Please finish logging in manually, then press Enter.\n")
            input("Press Enter once you are logged in...")
            print()
    else:
        print("No credentials in .env — please log in manually in the browser.")
        print("Once you are on your dashboard, come back here and press Enter.\n")
        input("Press Enter once you are logged in...")
        print()


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
    dt_str = publish_datetime.strftime("%Y-%m-%dT%H:%M")
    scheduled = page.evaluate(f"""
        () => {{
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
    cfg = load_config()

    files = sorted(glob.glob(os.path.join(cfg["chapters_folder"], "*.txt")))
    if not files:
        print(f"ERROR: No .txt files found in '{cfg['chapters_folder']}' folder.")
        return

    start_dt = datetime.strptime(f"{cfg['start_date']} {cfg['release_time']}", "%Y-%m-%d %H:%M")
    schedule = [start_dt + timedelta(days=i * cfg["freq_days"]) for i in range(len(files))]

    print(f"Found {len(files)} chapter file(s).")
    print(f"Fiction ID : {cfg['fiction_id']}")
    print(f"Schedule preview:")
    for i, (f, dt) in enumerate(zip(files, schedule), 1):
        print(f"  Chapter {i}: {os.path.basename(f)} → {dt.strftime('%Y-%m-%d %H:%M')}")
    print()

    confirm = input("Proceed with upload? [Y/n]: ").strip().lower()
    if confirm == "n":
        print("Aborted.")
        return
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome", slow_mo=50)
        page = browser.new_page()

        print("A browser window has opened.\n")
        login(page)
        print("Starting uploads...\n")

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
                create_draft(page, cfg["fiction_id"], title, content, publish_dt)
                time.sleep(cfg["delay"])
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
    print(f"  https://www.royalroad.com/fiction/{cfg['fiction_id']}/chapters")


if __name__ == "__main__":
    main()

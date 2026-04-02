# Rednote Poster

A single Python program (`rednote_poster.py`) that automates creating a Rednote (Xiaohongshu) post through the web creator UI.

## Why automation?
Rednote does not expose a general public posting API for typical developer use, so this script automates the browser UI with Playwright.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

## Usage

1. Create a caption text file, for example `post.txt`.
2. Prepare one or more image files.
3. Run:

```bash
python rednote_poster.py \
  --text-file post.txt \
  --image img1.jpg \
  --image img2.jpg
```

Add `--publish` to click the publish button automatically.

```bash
python rednote_poster.py \
  --text-file post.txt \
  --image img1.jpg \
  --publish
```

## Notes
- First run usually requires interactive login in the opened Chromium window.
- Session data is saved to `.rednote_profile` by default.
- UI selectors can change; if the script times out, inspect the page and update selectors.
- Use responsibly and comply with Rednote's Terms of Service.

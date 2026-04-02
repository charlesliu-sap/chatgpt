#!/usr/bin/env python3
"""Post content to Rednote (Xiaohongshu) via browser automation.

This script uses Playwright to automate posting through the web UI because
Rednote does not provide a broadly available public posting API.
"""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright


DEFAULT_NEW_POST_URL = "https://creator.xiaohongshu.com/publish/publish"


async def post_to_rednote(
    user_data_dir: str,
    text_file: str,
    images: list[str],
    publish: bool,
    headless: bool,
    timeout_ms: int,
) -> None:
    """Automate Rednote post creation.

    Args:
        user_data_dir: Persistent profile directory to keep login session.
        text_file: Path to UTF-8 text file containing post caption.
        images: Paths to image files.
        publish: If True, click publish. Otherwise save as draft (manual).
        headless: Run browser in headless mode.
        timeout_ms: Max wait for key elements.
    """
    caption = Path(text_file).read_text(encoding="utf-8").strip()
    if not caption:
        raise ValueError("Caption text file is empty.")

    if not images:
        raise ValueError("Provide at least one image path with --image.")

    for image in images:
        if not Path(image).exists():
            raise FileNotFoundError(f"Image not found: {image}")

    async with async_playwright() as playwright:
        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            viewport={"width": 1440, "height": 900},
        )
        page = context.pages[0] if context.pages else await context.new_page()

        try:
            await page.goto(DEFAULT_NEW_POST_URL, wait_until="domcontentloaded")

            # If login is required, let operator log in interactively once.
            if "login" in page.url.lower() or "passport" in page.url.lower():
                print("Please complete login in the opened browser window...")
                await page.wait_for_url("**/publish/**", timeout=timeout_ms)

            await page.wait_for_timeout(1500)

            file_input = page.locator("input[type='file']").first
            await file_input.set_input_files(images)

            editor = page.locator("div[contenteditable='true']").first
            await editor.wait_for(timeout=timeout_ms)
            await editor.fill(caption)

            if publish:
                publish_button = page.get_by_role("button", name="发布")
                await publish_button.click(timeout=timeout_ms)
                print("Publish submitted. Verify in your account dashboard.")
            else:
                print(
                    "Draft prepared. Review in browser and publish manually if needed."
                )

        except PlaywrightTimeoutError as exc:
            raise RuntimeError(
                "Timed out while interacting with Rednote UI. "
                "Selectors may have changed; inspect the page and update script."
            ) from exc
        finally:
            await context.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automate creating a Rednote post (Xiaohongshu) with Playwright"
    )
    parser.add_argument(
        "--profile-dir",
        default=".rednote_profile",
        help="Persistent browser profile directory for login session",
    )
    parser.add_argument(
        "--text-file",
        required=True,
        help="Path to UTF-8 text file containing caption",
    )
    parser.add_argument(
        "--image",
        dest="images",
        action="append",
        required=True,
        help="Image path. Repeat flag to attach multiple images.",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Actually click the publish button. Omit to only prepare draft.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser headlessly (not recommended for first-time login).",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=90000,
        help="Timeout in milliseconds for major UI steps",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(
        post_to_rednote(
            user_data_dir=args.profile_dir,
            text_file=args.text_file,
            images=args.images,
            publish=args.publish,
            headless=args.headless,
            timeout_ms=args.timeout_ms,
        )
    )


if __name__ == "__main__":
    main()

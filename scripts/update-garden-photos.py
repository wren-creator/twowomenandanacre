#!/usr/bin/env python3
"""
Watches ~/Downloads/garden for photos, drops them into assets/, updates the
"what we grow, this season" strip in index.html, and commits (and pushes)
the result.

Usage:
    scripts/update-garden-photos.py              # process, commit, push
    scripts/update-garden-photos.py --no-push     # process and commit only
    scripts/update-garden-photos.py --dry-run     # show what would happen, change nothing

Drop a photo named for what it is, e.g. "cherry-tomatoes.jpg" or
"purple okra.png", into ~/Downloads/garden. The filename (minus extension)
becomes the caption. Re-dropping a photo with the same name replaces the
existing entry, image and all, so this also handles "update this crop's
picture."
"""
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_DIR / "assets"
INDEX_HTML = REPO_DIR / "index.html"
SOURCE_DIR = Path.home() / "Downloads" / "garden"
PROCESSED_DIR = SOURCE_DIR / "processed"

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

FIGURE_RE = re.compile(
    r'<figure><img src="assets/(?P<file>[^"]+)" alt="(?P<alt>[^"]*)"><figcaption>(?P<caption>[^<]*)</figcaption></figure>'
)
GROW_STRIP_RE = re.compile(
    r'(<div class="grow-strip">\n)(?P<body>.*?)(\n\s*</div>)', re.DOTALL
)


def slugify(stem: str) -> str:
    slug = re.sub(r"[_\s]+", "-", stem.strip().lower())
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def caption_from_slug(slug: str) -> str:
    return " ".join(word.capitalize() for word in slug.split("-"))


def find_photos():
    if not SOURCE_DIR.exists():
        return []
    return sorted(
        p
        for p in SOURCE_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )


def load_grow_strip(html: str):
    match = GROW_STRIP_RE.search(html)
    if not match:
        sys.exit('Could not find <div class="grow-strip"> in index.html — layout may have changed.')
    entries = []
    for line in match.group("body").splitlines():
        fig = FIGURE_RE.search(line.strip())
        if fig:
            base = Path(fig.group("file")).stem
            entries.append(
                {"base": base, "file": fig.group("file"), "alt": fig.group("alt"), "caption": fig.group("caption")}
            )
    return match, entries


def render_grow_strip(entries) -> str:
    lines = [
        f'      <figure><img src="assets/{e["file"]}" alt="{e["alt"]}"><figcaption>{e["caption"]}</figcaption></figure>'
        for e in entries
    ]
    return "\n".join(lines)


def main():
    dry_run = "--dry-run" in sys.argv
    no_push = "--no-push" in sys.argv or dry_run

    photos = find_photos()
    if not photos:
        print(f"No photos waiting in {SOURCE_DIR}. Nothing to do.")
        return

    html = INDEX_HTML.read_text()
    match, entries = load_grow_strip(html)
    by_base = {e["base"]: e for e in entries}

    changes = []
    for photo in photos:
        slug = slugify(photo.stem)
        if not slug:
            print(f"Skipping {photo.name}: no usable name after cleanup.")
            continue
        caption = caption_from_slug(slug)
        ext = photo.suffix.lower()
        asset_name = f"{slug}{ext}"
        alt = f"{caption} growing on the acre"

        action = "update" if slug in by_base else "add"
        changes.append((photo, asset_name, caption, action))

        by_base[slug] = {"base": slug, "file": asset_name, "alt": alt, "caption": caption}

    if not changes:
        print("Nothing usable to process.")
        return

    print("Planned changes:")
    for photo, asset_name, caption, action in changes:
        print(f"  [{action}] {photo.name} -> assets/{asset_name} (\"{caption}\")")

    if dry_run:
        print("\nDry run, nothing was written.")
        return

    # existing entries keep their order, new ones append in the order dropped
    ordered = list(entries)
    seen = {e["base"] for e in ordered}
    for base, entry in by_base.items():
        if base in seen:
            for i, e in enumerate(ordered):
                if e["base"] == base:
                    ordered[i] = entry
        else:
            ordered.append(entry)
            seen.add(base)

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    for photo, asset_name, _, _ in changes:
        shutil.copy2(photo, ASSETS_DIR / asset_name)

    new_body = render_grow_strip(ordered)
    new_html = html[: match.start()] + match.group(1) + new_body + match.group(3) + html[match.end() :]
    INDEX_HTML.write_text(new_html)

    PROCESSED_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for photo, *_ in changes:
        photo.rename(PROCESSED_DIR / f"{stamp}-{photo.name}")

    status = subprocess.run(
        ["git", "status", "--porcelain", "assets", "index.html"],
        cwd=REPO_DIR, capture_output=True, text=True, check=True,
    ).stdout.strip()
    if not status:
        print("No git changes detected after processing, skipping commit.")
        return

    subprocess.run(["git", "add", "assets", "index.html"], cwd=REPO_DIR, check=True)

    added = [c for c in changes if c[3] == "add"]
    updated = [c for c in changes if c[3] == "update"]
    parts = []
    if added:
        parts.append("add " + ", ".join(c[2] for c in added))
    if updated:
        parts.append("update " + ", ".join(c[2] for c in updated))
    subject = "feat: " + " and ".join(parts) + " in what we grow this season"

    msg_file = REPO_DIR / ".git" / "GARDEN_COMMIT_MSG.txt"
    msg_file.write_text(subject + "\n\nCo-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>\n")
    subprocess.run(["git", "commit", "-F", str(msg_file)], cwd=REPO_DIR, check=True)
    msg_file.unlink()
    print(f"\nCommitted: {subject}")

    if no_push:
        print("Skipping push (--no-push or --dry-run).")
        return

    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_DIR, capture_output=True, text=True, check=True
    ).stdout.strip()
    subprocess.run(["git", "push", "origin", branch], cwd=REPO_DIR, check=True)
    print(f"Pushed to origin/{branch}.")


if __name__ == "__main__":
    main()

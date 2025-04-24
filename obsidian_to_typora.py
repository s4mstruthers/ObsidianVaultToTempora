#usage: python obsidian_to_typora.py path_to_folder
from __future__ import annotations

import argparse
import os
import re
from itertools import chain
from pathlib import Path

# --------------------------- Regex patterns ----------------------------------
# Obsidian embed with optional trailing () link
EMBED_RE = re.compile(r"!\[\[([^\]]+?)\]\](?:\([^)]*\))?")
# Markdown image (captures alt + src)
MD_IMG_RE = re.compile(r"!\[([^\]]*?)\]\((.*?)\)")
# Blockquote first lines with admonition tag
BQ_RE = re.compile(r"^(\s*>\s*)\[!([A-Za-z0-9_-]+)\](.*)$")

SUPPORTED_ADMONITIONS = {
    "note", "tip", "important", "warning", "caution"
}

# -----------------------------------------------------------------------------
# Image helpers

def _derive_alt(filename: str) -> str:
    """Return alt text derived from *filename* (stem, spaces instead of dashes)."""
    stem = Path(filename).stem
    return stem.replace("-", " ").replace("_", " ") or stem


def _rewrite_embed(match: re.Match[str]) -> str:
    inner = match.group(1)  # e.g. path/img.png|500
    if "|" in inner:
        path_part, _ = inner.split("|", 1)
    else:
        path_part = inner
    filename = Path(path_part).name
    alt = _derive_alt(filename)
    return f"![{alt}](./assets/{filename})"


def _rewrite_md_img(match: re.Match[str]) -> str:
    alt_text, src = match.groups()

    # Clean alt text if it contains a size or other suffix after '|'
    if "|" in alt_text:
        alt_text = alt_text.split("|", 1)[0].strip()
    if not alt_text:
        alt_text = _derive_alt(Path(src).name)

    # Normalise src to ./assets/<filename>
    filename = Path(src).name
    new_src = f"./assets/{filename}"
    return f"![{alt_text}]({new_src})"


def rewrite_images(markdown: str) -> str:
    markdown = EMBED_RE.sub(_rewrite_embed, markdown)
    markdown = MD_IMG_RE.sub(_rewrite_md_img, markdown)
    return markdown

# -----------------------------------------------------------------------------
# Blockquote / admonition helper (unchanged from v3.2)

def rewrite_blockquotes(markdown: str) -> str:
    new_lines: list[str] = []
    for line in markdown.splitlines(keepends=True):
        m = BQ_RE.match(line)
        if not m:
            new_lines.append(line)
            continue
        leader, tag, rest = m.groups()
        tag_low = tag.lower()
        title = rest.strip()
        newline = "\n"
        if tag_low in SUPPORTED_ADMONITIONS:
            if title:
                new_lines.append(f"{leader}[!{tag}]{newline}")
                new_lines.append(f"{leader}**{title}**{newline}")
            else:
                new_lines.append(line)
        else:
            if title:
                new_lines.append(f"{leader}**{title}**{newline}")
            # else: skip line entirely
    return "".join(new_lines)

# -----------------------------------------------------------------------------


def rename_attachment_dirs(root: Path) -> None:
    for dirpath, dirnames, _ in os.walk(root, topdown=False):
        for dirname in dirnames:
            if dirname.lower() == "attachments":
                old_dir = Path(dirpath) / dirname
                new_dir = Path(dirpath) / "assets"
                try:
                    old_dir.rename(new_dir)
                    print(f"Renamed {old_dir} → {new_dir}")
                except FileExistsError:
                    print(f"Skipped {old_dir}: {new_dir} already exists")


def update_markdown_files(root: Path) -> None:
    md_files = chain(root.rglob("*.md"), root.rglob("*.markdown"))
    for md_file in md_files:
        try:
            text = md_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rewritten = rewrite_blockquotes(rewrite_images(text))
        if rewritten != text:
            md_file.write_text(rewritten, encoding="utf-8")
            print(f"Updated {md_file.relative_to(root)}")

# -----------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate an Obsidian vault to pure Typora‑friendly Markdown.)")
    parser.add_argument("root", nargs="?", default=".", help="Vault root (default: .)")
    args = parser.parse_args()

    vault_root = Path(args.root).expanduser().resolve()
    if not vault_root.is_dir():
        parser.error(f"{vault_root} is not a directory")

    rename_attachment_dirs(vault_root)
    update_markdown_files(vault_root)
    print("✔ Migration complete.")


if __name__ == "__main__":
    main()

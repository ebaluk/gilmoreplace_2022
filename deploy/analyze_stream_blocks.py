#!/usr/bin/env python3
"""Analyze StreamField block usage from deploy/db/dump.sql."""
import json
import re
from collections import Counter

DUMP = "deploy/db/dump.sql"
BLOCKS = "wtpages/blocks.py"

with open(BLOCKS, encoding="utf-8") as f:
    src = f.read().split("stream_field_blocks = [")[1].split("]")[0]
ACTIVE = set(re.findall(r"^\s*\('([a-z_0-9]+)'", src, re.M))
COMMENTED = set(re.findall(r"^\s*#\s*\('([a-z_0-9]+)'", src, re.M))

FRONTEND = {
    "image", "video", "gallery", "gallery_collections", "carousel", "info",
    "interactive_map", "interactive_map_tabs", "places", "tower_views", "contact",
    "hash", "raw_html", "onni_logo", "instagram", "site_map", "about_collage",
    "texts_and_images_gallery", "form", "shared_blocks", "paragraph",
    "penthouses_widget", "features", "tower_plans", "interactive_map_tabks",
}

NESTED_ONLY = {
    "text", "image_text_box", "image_box", "logo",
    "internal_page_link", "external_page_link", "phone_link", "email_link",
    "form_link", "doc_link", "onni_link",
    "singleline", "multiline", "email", "number", "url", "date", "time", "datetime",
    "checkbox", "dropdown", "radio", "checkboxes", "file", "captcha", "fieldsgroup",
    "sectiontitleh2", "sectiontitleh3", "password", "none", "places",
}


def pg_unescape(s: str) -> str:
    out, i = [], 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            n = s[i + 1]
            mapping = {"n": "\n", "t": "\t", "r": "\r", "b": "\b", "f": "\f", "\\": "\\"}
            out.append(mapping.get(n, n))
            i += 2
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def load_copy_sections(path: str) -> dict:
    sections = {}
    current = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("COPY public."):
                m = re.match(r"COPY public\.(\w+) \(([^)]+)\) FROM stdin;", line)
                if not m:
                    current = None
                    continue
                table = m.group(1)
                cols = [c.strip().strip('"') for c in m.group(2).split(",")]
                sections[table] = {"cols": cols, "rows": []}
                current = table
                continue
            if current:
                if line.strip() == "\\.":
                    current = None
                elif line.strip():
                    sections[current]["rows"].append(line.rstrip("\n"))
    return sections


def parse_field(table: str, field: str, sections: dict) -> tuple[Counter, int, int]:
    ctr = Counter()
    parsed = failed = 0
    sec = sections.get(table)
    if not sec:
        return ctr, 0, 0
    cols = sec["cols"]
    if field not in cols:
        return ctr, 0, 0
    idx = cols.index(field)
    n_prefix = idx
    for row in sec["rows"]:
        parts = row.split("\t", n_prefix + 1)
        if len(parts) != n_prefix + 1:
            failed += 1
            continue
        raw = parts[idx]
        if raw == "\\N":
            continue
        try:
            data = json.loads(pg_unescape(raw))
        except json.JSONDecodeError:
            failed += 1
            continue
        parsed += 1
        for item in data:
            ctr[item.get("type", "?")] += 1
    return ctr, parsed, failed


def main():
    sections = load_copy_sections(DUMP)

    page_ctr, page_ok, page_fail = parse_field(
        "wtpages_standardpage", "stream_field", sections
    )
    shared_ctr, shared_ok, shared_fail = parse_field(
        "towers_sharedpageblocks", "stream_field", sections
    )

    # Content delivered via shared_blocks snippets (referenced from pages)
    content_ctr = Counter(page_ctr)
    for t, n in shared_ctr.items():
        content_ctr[t] += n
  # shared_blocks on pages is just a pointer; real blocks live in shared_ctr
    pointer_count = page_ctr.get("shared_blocks", 0)

    print("=== Page stream_field (wtpages_standardpage) ===")
    print(f"rows parsed: {page_ok}, failed: {page_fail}")
    for t, n in page_ctr.most_common():
        print(f"  {n:4d}  {t}")

    print("\n=== Shared block bodies (towers_sharedpageblocks) ===")
    print(f"rows parsed: {shared_ok}, failed: {shared_fail}")
    for t, n in shared_ctr.most_common():
        print(f"  {n:4d}  {t}")

    print("\n=== Effective page content (direct blocks + shared bodies) ===")
    direct = Counter({k: v for k, v in page_ctr.items() if k != "shared_blocks"})
    effective = direct + shared_ctr
    for t, n in effective.most_common():
        print(f"  {n:4d}  {t}")
    print(f"  (plus {pointer_count} shared_blocks pointers on pages)")

    unused = sorted(ACTIVE - set(effective.keys()))
    print("\n=== Active in stream_field_blocks, ZERO uses in page/shared content ===")
    for t in unused:
        print(f"  - {t}")

    rare = sorted((t, effective[t]) for t in ACTIVE & set(effective) if effective[t] <= 2)
    print("\n=== Active blocks, rarely used (1-2 instances) ===")
    for t, n in rare:
        print(f"  {n}  {t}")

    print("\n=== Commented-out in blocks.py (legacy definitions) ===")
    with open(DUMP, encoding="utf-8", errors="replace") as f:
        all_text = f.read()
    all_types = Counter(re.findall(r'"type"\s*:\s*"([a-z][a-z0-9_]*)"', all_text))
    for t in sorted(COMMENTED):
        c = all_types.get(t, 0)
        note = "USED (mis-commented?)" if c else "unused"
        print(f"  {t}: {c}  [{note}]")

    print("\n=== Frontend components without schema entry ===")
    for t in sorted(FRONTEND - ACTIVE - {"interactive_map_tabs"}):
        print(f"  - {t}")

    print("\n=== Schema entry with frontend gap ===")
    if "interactive_map_tabks" in ACTIVE and "interactive_map_tabs" in FRONTEND:
        print("  - interactive_map_tabks (backend typo) -> interactive_map_tabs in frontend only")

    # Other streamfields
    other_fields = [
        ("wtpages_wtbasepage", "hero_links"),
        ("wtpages_wtbasepage", "logos_banner"),
        ("wthomepage_languagerootpage", "footer_links"),
        ("wtpromobox_promoboxitem", "links_stream_field"),
        ("wtforms_wtform", "form_body"),
    ]
    print("\n=== Other StreamFields (not page body) ===")
    for table, field in other_fields:
        ctr, ok, fail = parse_field(table, field, sections)
        if not ctr:
            continue
        print(f"\n{table}.{field} (parsed {ok}, failed {fail}):")
        for t, n in ctr.most_common():
            print(f"  {n:4d}  {t}")


if __name__ == "__main__":
    main()

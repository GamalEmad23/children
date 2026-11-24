"""Recreate attribution records for the locally stored Wikimedia Commons images."""
import html
import json
import re
import time
import urllib.error
from pathlib import Path

import fetch_free_media as media

ROOT = media.ROOT
mapping = json.loads((ROOT / "assets" / "photos.json").read_text(encoding="utf-8"))
found = {}

def lookup(params):
    for attempt in range(5):
        try:
            return media.get_json(params)
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 4:
                raise
            time.sleep(8 * (attempt + 1))

def clean(value):
    return html.unescape(re.sub(r"<[^>]*>", "", value or "")).strip()

seen = set()
for index, (term, aliases) in enumerate(media.ITEMS):
    local = mapping.get(term)
    if not local or local in seen:
        continue
    seen.add(local)
    query = media.SEARCH_TERMS.get(term, term)
    result = lookup({"action":"query", "format":"json", "generator":"search", "gsrnamespace":6,
                     "gsrlimit":10, "gsrsearch":query + " filetype:bitmap", "prop":"imageinfo",
                     "iiprop":"url|extmetadata", "iiurlwidth":480})
    pages = result.get("query", {}).get("pages", {})
    ordered = sorted(pages.values(), key=lambda page: page.get("index", 999))
    exact = [candidate for candidate in ordered if term.casefold() in candidate["title"].casefold()]
    page = (exact[0] if exact else ordered[0])
    info = page["imageinfo"][0]
    meta = info.get("extmetadata", {})
    def field(name):
        return clean(meta.get(name, {}).get("value", ""))
    found[local] = f"- **{term}** — [{page['title']}]({info.get('descriptionurl','')}) by {field('Artist') or 'See source page'}; {field('LicenseShortName') or 'See source page'}" + (f" ([license]({field('LicenseUrl')}))" if field("LicenseUrl") else "")
    print(f"Credited {term} ({index+1}/{len(media.ITEMS)})", flush=True)
    time.sleep(1.0)

lines = ["# Photo credits", "", "Images are from Wikimedia Commons. Each source is licensed individually; verify its terms before redistribution.", ""]
lines.extend(found[path] for path in sorted(found))
(ROOT / "assets" / "PHOTO-CREDITS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {len(found)} image credits.", flush=True)

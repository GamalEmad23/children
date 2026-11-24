"""Fetch freely licensed Commons photos and generate neural voice clips for Horoofy Kids."""
import asyncio
import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import edge_tts

ROOT = Path(__file__).resolve().parents[1]
API = "https://commons.wikimedia.org/w/api.php?"
HEADERS = {"User-Agent": "HoroofyKidsLearningSite/1.0 (educational use)"}

ITEMS = [
    ("Lion", ["أسد"]), ("Duck", ["بطة"]), ("Apple", ["تفاحة"]), ("Fox", ["ثعلب"]),
    ("Camel", ["جمل"]), ("Horse", ["حصان"]), ("Bread", ["خبز"]), ("Bear", ["دب"]),
    ("Corn", ["ذرة"]), ("Pomegranate", ["رمان"]), ("Giraffe", ["زرافة"]),
    ("Fish", ["سمكة"]), ("Sun", ["شمس"]), ("Falcon", ["صقر"]), ("Frog", ["ضفدع"]),
    ("Airplane", ["طائرة"]), ("Envelope", ["ظرف"]), ("Grapes", ["عنب"]),
    ("Gazelle", ["غزال"]), ("Butterfly", ["فراشة"]), ("Moon", ["قمر"]),
    ("Book", ["كتاب"]), ("Lemon", ["ليمون"]), ("Banana", ["موز"]), ("Bee", ["نحلة"]),
    ("Rose", ["وردة"]), ("Hand", ["يد"]), ("Cat", []), ("Elephant", []), ("Hat", ["قبعة"]),
    ("Ice cream", []), ("Juice", ["عصير"]), ("Kite", ["طائرة ورقية"]), ("Nest", ["عش"]),
    ("Orange", []), ("Penguin", []), ("Queen", ["تاج"]), ("Rainbow", []),
    ("Tiger", []), ("Umbrella", ["مظلة"]), ("Violin", ["كمان"]), ("Whale", []),
    ("Xylophone", []), ("Yoyo", ["يويو"]), ("Zebra", []), ("Ball", ["كرة"]), ("Crescent moon", ["هلال"]),
]
SEARCH_TERMS = {"Queen":"crown royal crown", "Violin":"violin musical instrument", "Whale":"humpback whale breaching", "Falcon":"falcon bird", "Xylophone":"xylophone musical instrument", "Yoyo":"yo-yo toy", "Juice":"orange juice glass", "Ball":"soccer ball on grass", "Crescent moon":"crescent moon", "Kite":"kite flying in sky", "Nest":"bird nest eggs"}

def get_json(params):
    url = API + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)

def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def fetch_photos(start=0, end=len(ITEMS), force=False):
    out = ROOT / "assets" / "photos"
    out.mkdir(parents=True, exist_ok=True)
    map_path = ROOT / "assets" / "photos.json"
    mapping = json.loads(map_path.read_text(encoding="utf-8")) if map_path.exists() else {}
    credits_path = ROOT / "assets" / "PHOTO-CREDITS.md"
    credited = credits_path.read_text(encoding="utf-8").splitlines() if credits_path.exists() else ["# Photo credits", "", "Images below are sourced from Wikimedia Commons. Each file's license and creator is recorded per item.", ""]
    credit_index = {match.group(1): i for i, line in enumerate(credited) if (match := re.match(r"- \*\*(.*?)\*\*", line))}
    for term, aliases in ITEMS[start:end]:
        key = slug(term)
        if not force and key in mapping and (ROOT / mapping[key]).exists() and (ROOT / mapping[key]).stat().st_size > 1000:
            print("Already have photo:", term, flush=True); continue
        try:
            query = SEARCH_TERMS.get(term, term)
            pages = get_json({"action":"query", "format":"json", "generator":"search", "gsrnamespace":6,
                              "gsrlimit":10, "gsrsearch":query + " filetype:bitmap", "prop":"imageinfo",
                              "iiprop":"url|extmetadata", "iiurlwidth":480}).get("query", {}).get("pages", {})
            ordered = sorted(pages.values(), key=lambda page: page.get("index", 999))
            if not ordered:
                pages = get_json({"action":"query", "format":"json", "generator":"search", "gsrnamespace":6,
                                  "gsrlimit":10, "gsrsearch":query, "prop":"imageinfo",
                                  "iiprop":"url|extmetadata", "iiurlwidth":480}).get("query", {}).get("pages", {})
                ordered = sorted(pages.values(), key=lambda page: page.get("index", 999))
            if not ordered:
                print("No photo found:", term, flush=True); continue
            exact = [candidate for candidate in ordered if term.casefold() in candidate["title"].casefold()]
            page = exact[0] if exact else ordered[0]; chosen = page; info = page["imageinfo"][0]
            url = info.get("thumburl", info["url"])
            ext = ".jpg" if "thumburl" in info else Path(urllib.parse.urlparse(url).path).suffix or ".jpg"
            dest = out / (key + ext)
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=45) as response, dest.open("wb") as f:
                f.write(response.read())
            meta = info.get("extmetadata", {})
            def val(name):
                return re.sub(r"<[^>]*>", "", meta.get(name, {}).get("value", "")).strip()
            source_page = info.get("descriptionurl", "")
            license_name = val("LicenseShortName") or "See source page"
            artist = val("Artist") or "See source page"
            credit = {"term":term,"file":dest.relative_to(ROOT).as_posix(),"title":chosen["title"],
                      "artist":artist,"license":license_name,"source":source_page,
                      "licenseUrl":val("LicenseUrl")}
            credit_line = f"- **{credit['term']}** — [{credit['title']}]({credit['source']}) by {credit['artist']}; {credit['license']}" + (f" ([license]({credit['licenseUrl']}))" if credit['licenseUrl'] else "")
            if term in credit_index: credited[credit_index[term]] = credit_line
            else: credit_index[term] = len(credited); credited.append(credit_line)
            for word in [term, *aliases]: mapping[word] = credit["file"]
            map_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
            credits_path.write_text("\n".join(credited)+"\n", encoding="utf-8")
            print("Photo:", term, "=>", chosen["title"], flush=True)
            time.sleep(1.2)
        except Exception as exc:
            print("Photo failed:", term, str(exc), flush=True)
    (ROOT / "assets" / "photos.json").write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding="utf-8")
    credits_path.write_text("\n".join(credited)+"\n", encoding="utf-8")
    return mapping

AR = [("ألف","أسد"),("باء","بطة"),("تاء","تفاحة"),("ثاء","ثعلب"),("جيم","جمل"),("حاء","حصان"),("خاء","خبز"),("دال","دب"),("ذال","ذرة"),("راء","رمان"),("زاي","زرافة"),("سين","سمكة"),("شين","شمس"),("صاد","صقر"),("ضاد","ضفدع"),("طاء","طائرة"),("ظاء","ظرف"),("عين","عنب"),("غين","غزال"),("فاء","فراشة"),("قاف","قمر"),("كاف","كتاب"),("لام","ليمون"),("ميم","موز"),("نون","نحلة"),("هاء","هلال"),("واو","وردة"),("ياء","يد")]
EN = list(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ", ["Apple","Ball","Cat","Duck","Elephant","Fish","Grapes","Hat","Ice cream","Juice","Kite","Lion","Moon","Nest","Orange","Penguin","Queen","Rainbow","Sun","Tiger","Umbrella","Violin","Whale","Xylophone","Yoyo","Zebra"]))

async def one(text, voice, path):
    try:
        await edge_tts.Communicate(text, voice, rate="-8%", pitch="+2Hz").save(str(path))
        return True
    except Exception as exc:
        print("Audio failed:", path.name, str(exc)); return False

async def fetch_audio(language="all", start=0, end=28):
    jobs=[]
    for lang, entries, voice in [("ar", AR, "ar-EG-SalmaNeural"),("en", EN, "en-US-AriaNeural")]:
        if language != "all" and language != lang: continue
        out=ROOT/"audio"/lang; out.mkdir(parents=True, exist_ok=True)
        for i,(letter,word) in enumerate(entries[start:end], start=start):
            name = letter if lang=="ar" else f"Letter {letter}"
            if not (out/f"{i}-letter.mp3").exists() or (out/f"{i}-letter.mp3").stat().st_size == 0: jobs.append((f"{lang}/{i}-letter.mp3", name, voice))
            if not (out/f"{i}-word.mp3").exists() or (out/f"{i}-word.mp3").stat().st_size == 0: jobs.append((f"{lang}/{i}-word.mp3", word, voice))
    sem=asyncio.Semaphore(4)
    async def run(path,text,voice):
        async with sem:
            return await one(text,voice,ROOT/"audio"/path)
    done=await asyncio.gather(*(run(p,t,v) for p,t,v in jobs))
    print(f"Audio generated: {sum(done)}/{len(done)}", flush=True)

if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--photos-only",action="store_true"); parser.add_argument("--audio-only",action="store_true"); parser.add_argument("--force",action="store_true"); parser.add_argument("--photo-start",type=int,default=0); parser.add_argument("--photo-end",type=int,default=len(ITEMS)); parser.add_argument("--audio-lang",choices=["ar","en","all"],default="all"); parser.add_argument("--audio-start",type=int,default=0); parser.add_argument("--audio-end",type=int,default=28); args=parser.parse_args()
    if not args.audio_only: fetch_photos(args.photo_start,args.photo_end,args.force)
    if not args.photos_only: asyncio.run(fetch_audio(args.audio_lang,args.audio_start,args.audio_end))

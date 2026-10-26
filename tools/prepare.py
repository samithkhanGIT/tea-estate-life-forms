#!/usr/bin/env python3
"""
Match survey photos to the CSV and build the files the website needs.

  python tools/prepare.py --src "C:\\Users\\Samith\\OneDrive\\Desktop\\tea estate\\...\\attachments"

What it does
  1. Reads data/survey.csv (column Take_a_picture holds the photo name).
  2. Searches --src (and every sub-folder) for photos. Names are matched WITHOUT the
     file extension and ignoring upper/lower case, so 2026..._10_20.heic in the CSV
     matches 2026..._10_20.jpg on disk (or the other way round).
  3. Converts each matched photo (HEIC, JPG, PNG...) to a web JPG:
        images/full/<name>.jpg    (max 1000 px, for the big view)
        images/thumbs/<name>.jpg  (max 140 px, for the list)
  4. Writes data/records.json, which index.html reads.

Needs:  pip install pillow pillow-heif
"""
import argparse, csv, json, os, sys
from pathlib import Path
from PIL import Image, ImageOps

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    print("Note: pillow-heif is not installed, so .heic photos cannot be read.\n"
          "      Run:  pip install pillow-heif\n")

EXTS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff", ".bmp"}


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="folder that holds the photos (sub-folders are searched too)")
    ap.add_argument("--csv", default="data/survey.csv")
    ap.add_argument("--full", type=int, default=1000, help="max size of the big image in px")
    ap.add_argument("--quality", type=int, default=72)
    a = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    src = Path(a.src)
    if not src.is_dir():
        sys.exit(f"Folder not found: {src}")

    # index every photo on disk by lower-case name without extension
    found = {}
    dupes = 0
    for p in src.rglob("*"):
        if p.is_file() and p.suffix.lower() in EXTS:
            key = p.stem.lower()
            if key in found:
                dupes += 1
                # prefer the larger file when the same name appears twice
                if p.stat().st_size <= found[key].stat().st_size:
                    continue
            found[key] = p
    print(f"Photos found on disk: {len(found)}" + (f" ({dupes} duplicate names)" if dupes else ""))

    with open(root / a.csv, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    print(f"Rows in CSV: {len(rows)}")

    (root / "images/full").mkdir(parents=True, exist_ok=True)
    (root / "images/thumbs").mkdir(parents=True, exist_ok=True)

    records, missing, failed = [], [], []
    for r in rows:
        name = (r.get("Take_a_picture") or "").strip()
        stem = Path(name).stem
        p = found.get(stem.lower())
        ok = False
        if p:
            try:
                im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
                big = im.copy(); big.thumbnail((a.full, a.full))
                big.save(root / f"images/full/{stem}.jpg", quality=a.quality, optimize=True)
                th = im.copy(); th.thumbnail((140, 140))
                th.save(root / f"images/thumbs/{stem}.jpg", quality=70)
                ok = True
            except Exception as e:
                failed.append((name, str(e)))
        elif name:
            missing.append(name)
        note = (r.get("Add_a_special_Note") or "").strip()
        records.append({
            "id": stem, "file": name,
            "lat": num(r.get("_Pin_the_Location_latitude")), "lon": num(r.get("_Pin_the_Location_longitude")),
            "note": "" if note.lower() in ("", "n/a") else note,
            "photo": ok,
            "date": f"{stem[:4]}-{stem[4:6]}-{stem[6:8]}", "time": f"{stem[9:11]}:{stem[11:13]}:{stem[13:15]}",
        })
    records.sort(key=lambda x: (x["date"], x["time"]))
    with open(root / "data/records.json", "w", encoding="utf-8") as f:
        json.dump(records, f, separators=(",", ":"))

    print(f"Matched and converted: {sum(r['photo'] for r in records)} of {len(records)}")
    if missing:
        print(f"\nNo photo found for {len(missing)} CSV rows, for example:")
        for n in missing[:10]:
            print("   ", n)
    if failed:
        print(f"\nCould not read {len(failed)} photos:")
        for n, e in failed[:10]:
            print("   ", n, "-", e)
    print("\nDone. Open the site with:  python -m http.server 8000   then visit http://localhost:8000")


if __name__ == "__main__":
    main()

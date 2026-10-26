# Tea Estate Life Forms

A small website for browsing the tea estate survey photos with their location and note,
and tagging each photo with a life form (Epiphyte, Herbs, Tree, Creeper, Climber, Grass, Shrub, or Other with typed text).

It is a plain static site (no server needed), so it works on GitHub Pages.

## Where the images are stored

```
tea-estate-life-forms/
├── index.html            the website
├── data/
│   ├── survey.csv        your Kobo export (Take_a_picture holds the photo name)
│   └── records.json      built from the CSV by prepare.py (the site reads this)
├── images/
│   ├── full/             big photos shown in the viewer   (committed to GitHub)
│   └── thumbs/           small list thumbnails            (committed to GitHub)
├── source_images/        OPTIONAL: your original phone photos, NOT committed (.gitignore)
└── tools/prepare.py      matches photos to the CSV and builds images/ + records.json
```

Photos are matched to the CSV **by name without the file extension**, so
`20260906_110829-11_10_20.heic` in the CSV matches `20260906_110829-11_10_20.jpg` (or `.JPG`, `.png`, ...) on disk.
HEIC photos are converted to JPG because most browsers cannot show HEIC.

## 1. Build the images and data (Windows)

Install Python 3 from python.org, then in a terminal inside this folder:

```
pip install pillow pillow-heif
python tools/prepare.py --src "C:\Users\Samith\OneDrive\Desktop\tea estate\aikCFJRjWApi9bEMuKyjfF_2026_10_24_16_45_56\samy_kobo95\attachments"
```

The script searches that folder and all sub-folders, converts every matched photo, and prints how many of the
160 CSV rows found a photo (and lists any that did not).

Total size is about 20 MB for 160 photos, well inside GitHub limits.

## 2. Try it on your computer

```
python -m http.server 8000
```

Open http://localhost:8000 (opening index.html by double-click will not work, the browser blocks reading data/records.json).

## 3. Publish on GitHub Pages

1. Create a new repository on github.com (for example `tea-estate-life-forms`).
2. Upload everything in this folder, or from a terminal:
   ```
   git init
   git add .
   git commit -m "Tea estate life forms viewer"
   git branch -M main
   git remote add origin https://github.com/<your-username>/tea-estate-life-forms.git
   git push -u origin main
   ```
3. In the repository go to **Settings > Pages**, set **Source** to **Deploy from a branch**, branch **main**, folder **/ (root)**, and Save.
4. After a minute the site is live at `https://<your-username>.github.io/tea-estate-life-forms/`.

Note: a public repository makes the photos and GPS locations public. Use a private repository if that matters
(GitHub Pages on private repositories needs a paid plan).

## How tags are saved

Tags are stored in the visitor's own browser, so each person sees their own tags.
To share results, use **Export CSV** (adds `life_form` and `other_life_form` columns) and send the file;
the other person can load it with **Import tags**. If you later want everyone to share one live set of tags,
the site can be connected to a small online database (for example Supabase or Firebase).

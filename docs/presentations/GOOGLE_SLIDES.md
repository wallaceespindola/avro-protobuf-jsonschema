# Getting This Deck into Google Slides

Two easy ways to bring `avro-protobuf-jsonschema.pptx` into Google Slides.

## Option 1: Import into an existing presentation

1. Open [Google Slides](https://slides.google.com) and create a blank presentation (or open one you have)
2. Go to **File → Import slides**
3. Click the **Upload** tab and select `docs/presentations/avro-protobuf-jsonschema.pptx`
4. Select **All** slides, then click **Import slides**

## Option 2: Open the PPTX directly from Drive

1. Upload `avro-protobuf-jsonschema.pptx` to [Google Drive](https://drive.google.com)
2. Right-click the file → **Open with → Google Slides**
3. Optionally: **File → Save as Google Slides** to convert it to a native Slides file

Fonts note: the deck uses standard fonts (Helvetica/Arial for text, Courier New for code), so it converts cleanly. Double-check code slides after import — table and text-box sizing can shift slightly.

## Marp alternative (HTML / PDF)

`docs/presentations/slides.md` is a [Marp](https://marp.app) deck. Export it without PowerPoint at all:

```bash
# HTML
npx @marp-team/marp-cli docs/presentations/slides.md -o docs/presentations/slides.html

# PDF
npx @marp-team/marp-cli docs/presentations/slides.md --pdf -o docs/presentations/slides.pdf

# PPTX (Marp's own export, an alternative to the bundled one)
npx @marp-team/marp-cli docs/presentations/slides.md --pptx -o docs/presentations/slides-marp.pptx
```

A PDF export also uploads to Google Drive and presents fine, and Speaker Deck accepts it directly.

---

Author: Wallace Espindola — wallace.espindola@gmail.com
Repo: <https://github.com/wallaceespindola/avro-protobuf-jsonschema>

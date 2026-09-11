# PDF layout QA

Compare a source PDF with its translation (or reprint) and mark layout mismatches: field alignment, lines, colors, fonts, font sizes.

Layout extraction uses the [Huridocs pdf-document-layout-analysis](https://huggingface.co/HURIDOCS/pdf-document-layout-analysis) Docker image when it is running. Without it, the pipeline uses JSON next to the PDF (see `samples/`).

## What it does

1. Extract text blocks (container or sidecar JSON)
2. Sort/merge blocks and match fields across languages (`sentence-transformers`)
3. Crop regions and compare lines, colors, fonts, sizes
4. Write annotated PDFs under `Result/`

Thresholds live in `config.py`. CLI overrides: `RUN.py`.

## Setup

Linux: `sudo apt-get install poppler-utils` (needed by `pdf2image`).

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python samples/generate_samples.py
```

Optional layout service:

```bash
docker run --rm --name pdf-document-layout-analysis -p 5060:5060 --entrypoint ./start.sh huridocs/pdf-document-layout-analysis:v0.0.21
```

## Run

```bash
python smart_comparison.py
# or
python RUN.py
```

Defaults: `samples/form_en.pdf` vs `samples/form_es.pdf`.

```python
from smart_comparison import tiny_tony
tiny_tony("samples/form_en.pdf", "samples/form_es.pdf")
```

## Layout

```
smart_comparison.py   # pipeline
RUN.py                # optional config overrides
align_tags.py         # semantic / geometric field matching
isolated_comparison.py
color_palette.py fonts_comparison.py font_sized.py
samples/              # synthetic EN/ES forms (not real insurer docs)
config.py
```

## Notes

- This is a research/QA toolkit, not a packaged product.
- Do not commit third-party insurance forms or filled applications.
- Annotated outputs: `Result/doc1_annotated.pdf`, `Result/doc2_annotated.pdf`.

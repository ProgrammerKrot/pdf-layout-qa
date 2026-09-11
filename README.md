# pdf-layout-qa

Compare a source PDF with a translation (or reprint) and mark layout mismatches: field alignment, lines, colors, fonts, sizes.

Layout extraction uses the [Huridocs](https://huggingface.co/HURIDOCS/pdf-document-layout-analysis) Docker image when it is up. Without it, the pipeline uses JSON next to each PDF (`samples/` includes fixtures).

## Run with Docker

First image build downloads PyTorch — expect several minutes.

```bash
python samples/generate_samples.py   # if samples/*.pdf are missing
docker compose up --build
```

Annotated PDFs land in `Result/` on the host.

Skip Huridocs and use sidecar JSON only:

```bash
docker compose run --rm -e LAYOUT_SERVICE_URL= app python -m pdfqa
```

## Run locally

Linux: `sudo apt-get install poppler-utils`

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
python samples/generate_samples.py
python -m pdfqa
```

Optional layout service:

```bash
docker run --rm --name pdf-layout -p 5060:5060 --entrypoint ./start.sh huridocs/pdf-document-layout-analysis:v0.0.21
```

Override the URL: `LAYOUT_SERVICE_URL=http://127.0.0.1:5060`

## API

```python
from pdfqa.pipeline import compare_pdfs
from pdfqa.cli import configure_and_run

compare_pdfs("samples/form_en.pdf", "samples/form_es.pdf")
configure_and_run(pdf1="a.pdf", pdf2="b.pdf", color_threshold=80)
```

Thresholds: `src/pdfqa/config.py`

## Layout

```
src/pdfqa/
  pipeline.py        # orchestrator
  cli.py             # config overrides
  layout/            # JSON sort, merge, semantic field match
  visual/            # lines, colors, fonts, crops, annotations
  util/
samples/             # synthetic EN/ES forms
```

Outputs: `Result/doc1_annotated.pdf`, `Result/doc2_annotated.pdf`

Do not commit third-party insurance forms.
With all gratitute toward my friend Tony, whom I was too young to understand

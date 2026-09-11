"""Write two synthetic bilingual forms + layout JSON. No third-party insurer content."""
import json
from pathlib import Path

PAGE_W, PAGE_H = 612, 792


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_pdf(path: Path, lines: list[tuple[int, int, str, int]]):
    content = ["BT"]
    for x, y, text, size in lines:
        content.append(f"/F1 {size} Tf")
        content.append(f"1 0 0 1 {x} {y} Tm")
        content.append(f"({pdf_escape(text)}) Tj")
    content.append("ET")
    stream = "\n".join(content).encode("latin-1", "replace")

    objs = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
        ),
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >> stream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    chunks = [b"%PDF-1.4\n"]
    offsets = [0]
    for i, body in enumerate(objs, start=1):
        offsets.append(sum(len(c) for c in chunks))
        chunks.append(f"{i} 0 obj\n".encode("ascii") + body + b"\nendobj\n")

    xref_pos = sum(len(c) for c in chunks)
    xref = [f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n"]
    for off in offsets[1:]:
        xref.append(f"{off:010d} 00000 n \n")
    trailer = (
        f"trailer << /Size {len(objs) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    )
    path.write_bytes(b"".join(chunks) + "".join(xref).encode("ascii") + trailer.encode("ascii"))


def box(left, top, width, height, text, kind):
    return {
        "left": left,
        "top": top,
        "width": width,
        "height": height,
        "page_number": 1,
        "page_width": PAGE_W,
        "page_height": PAGE_H,
        "text": text,
        "type": kind,
    }


def from_pdf_y(y, h=16):
    return PAGE_H - y - h


def main():
    here = Path(__file__).resolve().parent
    here.mkdir(parents=True, exist_ok=True)

    en_lines = [
        (50, 740, "Employee Enrollment Form", 18),
        (50, 710, "Section A: Application Type", 12),
        (50, 680, "Select one: New enrollment  Open enrollment", 11),
        (50, 640, "Section B: Employee Information", 12),
        (50, 610, "Employee name", 11),
        (50, 580, "Social security", 11),
        (50, 550, "Home address", 11),
        (50, 520, "City  State  ZIP code", 11),
        (50, 480, "Employer name", 11),
        (50, 450, "Date of hire", 11),
        (50, 410, "Type of coverage", 11),
        (50, 370, "Primary care physician", 11),
        (50, 40, "Page footer 1 of 1", 9),
    ]
    es_lines = [
        (50, 740, "Formulario de inscripcion del empleado", 16),
        (50, 710, "Seccion A: Tipo de solicitud", 12),
        (50, 680, "Seleccione uno: Nueva inscripcion  Inscripcion abierta", 11),
        (50, 640, "Seccion B: Informacion del empleado", 12),
        (50, 610, "Nombre del empleado", 11),
        (50, 580, "Seguro social", 11),
        (50, 550, "Direccion", 11),
        (50, 520, "Ciudad  Estado  Codigo postal", 11),
        (50, 480, "Nombre del empleador", 11),
        (50, 450, "Fecha de contratacion", 11),
        (50, 410, "Tipo de cobertura", 11),
        (50, 370, "Medico de atencion primaria", 11),
        (50, 40, "Pie de pagina 1 de 1", 9),
    ]

    write_pdf(here / "form_en.pdf", en_lines)
    write_pdf(here / "form_es.pdf", es_lines)

    en_json = [
        box(50, from_pdf_y(740, 22), 280, 22, "Employee Enrollment Form", "Section header"),
        box(50, from_pdf_y(710), 220, 16, "Section A: Application Type", "Section header"),
        box(50, from_pdf_y(680), 320, 16, "Select one: New enrollment Open enrollment", "Text"),
        box(50, from_pdf_y(640), 250, 16, "Section B: Employee Information", "Section header"),
        box(50, from_pdf_y(610), 140, 16, "Employee name", "Text"),
        box(50, from_pdf_y(580), 140, 16, "Social security", "Text"),
        box(50, from_pdf_y(550), 140, 16, "Home address", "Text"),
        box(50, from_pdf_y(520), 180, 16, "City State ZIP code", "Text"),
        box(50, from_pdf_y(480), 140, 16, "Employer name", "Text"),
        box(50, from_pdf_y(450), 140, 16, "Date of hire", "Text"),
        box(50, from_pdf_y(410), 140, 16, "Type of coverage", "Text"),
        box(50, from_pdf_y(370), 180, 16, "Primary care physician", "Text"),
        box(50, from_pdf_y(40, 12), 140, 12, "Page footer 1 of 1", "Page footer"),
    ]
    es_json = [
        box(50, from_pdf_y(740, 20), 320, 20, "Formulario de inscripcion del empleado", "Section header"),
        box(50, from_pdf_y(710), 240, 16, "Seccion A: Tipo de solicitud", "Section header"),
        box(50, from_pdf_y(680), 360, 16, "Seleccione uno: Nueva inscripcion Inscripcion abierta", "Text"),
        box(50, from_pdf_y(640), 280, 16, "Seccion B: Informacion del empleado", "Section header"),
        box(50, from_pdf_y(610), 180, 16, "Nombre del empleado", "Text"),
        box(50, from_pdf_y(580), 140, 16, "Seguro social", "Text"),
        box(50, from_pdf_y(550), 140, 16, "Direccion", "Text"),
        box(50, from_pdf_y(520), 220, 16, "Ciudad Estado Codigo postal", "Text"),
        box(50, from_pdf_y(480), 180, 16, "Nombre del empleador", "Text"),
        box(50, from_pdf_y(450), 180, 16, "Fecha de contratacion", "Text"),
        box(50, from_pdf_y(410), 160, 16, "Tipo de cobertura", "Text"),
        box(50, from_pdf_y(370), 220, 16, "Medico de atencion primaria", "Text"),
        box(50, from_pdf_y(40, 12), 160, 12, "Pie de pagina 1 de 1", "Page footer"),
    ]
    (here / "form_en.json").write_text(json.dumps(en_json, indent=2, ensure_ascii=False), encoding="utf-8")
    (here / "form_es.json").write_text(json.dumps(es_json, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote samples in {here}")


if __name__ == "__main__":
    main()

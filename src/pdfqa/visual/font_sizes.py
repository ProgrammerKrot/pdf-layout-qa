from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors

from PyPDF2 import PdfReader, PdfWriter
from typing import Tuple, Dict, List
from collections import defaultdict
from datetime import datetime

from pdfqa.config import FONT_COMPARISON
from pdfqa.constants import *

import fitz
import os
import io


SFE_FOLDER = FONT_COMPARISON["sfe_folder"]
SFS_FOLDER = FONT_COMPARISON["sfs_folder"]
SIZE_TOLERANCE = FONT_COMPARISON["size_tolerance"]
REPORT_STYLES = FONT_COMPARISON["report_styles"]
TABLE_STYLES = FONT_COMPARISON["table_styles"]


def get_font_details(pdf_path: str) -> Tuple[List[Tuple[float, str]], Dict[Tuple[float, str], int]]:
    """
    Extracts unique font sizes and font names from a PDF with their frequency.

    Args:
        pdf_path (str): Path to the input PDF.

    Returns:
        Tuple: Sorted list of unique (size, font) and a frequency dictionary.
    """

    doc = fitz.open(pdf_path)
    font_stats = defaultdict(int)
    font_details = set()

    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        size = round(span["size"], 3)
                        font_name = span["font"].lower().split("-")[0].split("+")[-1]
                        font_details.add((size, font_name))
                        font_stats[(size, font_name)] += 1

    return sorted(font_details), font_stats


def compare_font_details() -> Dict[str, Dict]:
    """
    Compares fonts between SFS and SFE PDFs in their respective folders.

    Returns:
        Dict[str, Dict]: Mismatches including differences and stats per file.
    """
    mismatches = {}

    for filename in os.listdir(SFS_FOLDER):
        if not filename.endswith(".pdf"):
            continue

        sfs_path = os.path.join(SFS_FOLDER, filename)
        sfe_path = os.path.join(SFE_FOLDER, filename)

        if not os.path.exists(sfe_path):
            continue

        sfs_fonts, sfs_stats = get_font_details(sfs_path)
        sfe_fonts, sfe_stats = get_font_details(sfe_path)

        if sfs_fonts == sfe_fonts:
            continue

        differences = []

        for size, name in sfs_fonts:
            if not any(abs(size - s) <= SIZE_TOLERANCE and name == n for s, n in sfe_fonts):
                differences.append(f"Missing in SFE: {size}pt '{name}' (used {sfs_stats[(size, name)]} times)")

        for size, name in sfe_fonts:
            if not any(abs(size - s) <= SIZE_TOLERANCE and name == n for s, n in sfs_fonts):
                differences.append(f"Extra in SFE: {size}pt '{name}' (used {sfe_stats[(size, name)]} times)")

        if differences:
            mismatches[filename] = {
                "differences": differences,
                "SFS_stats": dict(sfs_stats),
                "SFE_stats": dict(sfe_stats)
            }

    return mismatches


def add_dict_as_page_to_pdf(input_pdf: str, data_dict: Dict, output_path: str) -> None:
    """
    Appends a summary of font mismatches as a new page in the PDF report.

    Args:
        input_pdf (str): Path to the base PDF to append to.
        data_dict (Dict): Dictionary containing font mismatches per file.
        output_path (str): Path to save the updated PDF.
    """
    styles = getSampleStyleSheet()

    # Add custom styles
    styles.add(ParagraphStyle(
        name='Header1',
        parent=styles['Heading1'],
        fontSize=REPORT_STYLES["header1"]["font_size"],
        leading=REPORT_STYLES["header1"]["leading"],
        spaceAfter=REPORT_STYLES["header1"]["space_after"],
        textColor=colors.HexColor(REPORT_STYLES["header1"]["text_color"]),
        backColor=colors.HexColor(REPORT_STYLES["header1"]["background_color"]),
        alignment=REPORT_STYLES["header1"]["alignment"]
    ))

    styles.add(ParagraphStyle(
        name='Header2',
        parent=styles['Heading2'],
        fontSize=REPORT_STYLES["header2"]["font_size"],
        leading=REPORT_STYLES["header2"]["leading"],
        spaceAfter=REPORT_STYLES["header2"]["space_after"],
        textColor=colors.HexColor(REPORT_STYLES["header2"]["text_color"]),
        spaceBefore=REPORT_STYLES["header2"]["space_before"]
    ))

    styles.add(ParagraphStyle(
        name='DiffItem',
        parent=styles['Normal'],
        fontSize=REPORT_STYLES["diff_item"]["font_size"],
        leading=REPORT_STYLES["diff_item"]["leading"],
        spaceAfter=REPORT_STYLES["diff_item"]["space_after"],
        bulletIndent=REPORT_STYLES["diff_item"]["bullet_indent"],
        leftIndent=REPORT_STYLES["diff_item"]["left_indent"]
    ))

    packet = io.BytesIO()
    doc = SimpleDocTemplate(
        packet,
        pagesize=letter,
        title=font_diff_title,
        author=font_diff_author,
        subject=font_diff_subject
    )

    story = [
        Paragraph(font_diff_title, styles['Header1']),
        Spacer(1, 24)
    ]

    metadata = [
        [font_report_date_label, datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        [font_report_files_label, len(data_dict)],
        [font_report_total_label, sum(len(v["differences"]) for v in data_dict.values())]
    ]

    metadata_table = Table(metadata, colWidths=[1.5 * inch, 4 * inch])
    metadata_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), TABLE_STYLES["font_name"]),
        ('FONTSIZE', (0, 0), (-1, -1), TABLE_STYLES["font_size"]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(metadata_table)
    story.append(PageBreak())

    for file_num, (filename, data) in enumerate(data_dict.items(), 1):
        story.append(Paragraph(f"Analysis {file_num}: {filename}", styles['Header1']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Font Differences Found", styles['Header2']))

        for diff in data["differences"]:
            color_key = "extra" if "Extra in SFE" in diff else "missing"
            custom_style = ParagraphStyle(
                name=f'{color_key}Item',
                parent=styles['DiffItem'],
                textColor=colors.HexColor(REPORT_STYLES["colors"][color_key])
            )
            story.append(Paragraph(diff, custom_style))

        story.append(Spacer(1, 12))

        stats_data = [
            ["", "Font Size", "Font Name", "Count"],
            ["SFS Stats"] + [""] * 3
        ] + [
            ["", f"{size}pt", name, str(count)]
            for (size, name), count in data["SFS_stats"].items()
        ] + [
            ["SFE Stats"] + [""] * 3
        ] + [
            ["", f"{size}pt", name, str(count)]
            for (size, name), count in data["SFE_stats"].items()
        ]

        sfs_count = len(data["SFS_stats"])
        stats_table = Table(stats_data, colWidths=[0.8 * inch, 1.2 * inch, 2.5 * inch, 0.8 * inch])
        stats_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (3, 0)),
            ('SPAN', (0, 1), (3, 1)),
            ('SPAN', (0, sfs_count + 2), (3, sfs_count + 2)),

            ('BACKGROUND', (0, 1), (3, 1), colors.HexColor(TABLE_STYLES["background_color"])),
            ('BACKGROUND', (0, sfs_count + 2), (3, sfs_count + 2), colors.HexColor(TABLE_STYLES["background_color"])),

            ('FONTNAME', (0, 0), (-1, -1), TABLE_STYLES["font_name"]),
            ('FONTSIZE', (0, 0), (-1, -1), TABLE_STYLES["font_size"]),

            ('ALIGN', (1, 2), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 2), (3, -1), 'CENTER'),

            ('GRID', (0, 2), (-1, sfs_count + 1), 0.5, TABLE_STYLES["grid_color"]),
            ('GRID', (0, sfs_count + 3), (-1, -1), 0.5, TABLE_STYLES["grid_color"]),

            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(stats_table)
        story.append(PageBreak())

    doc.build(story)
    packet.seek(0)
    new_pdf = PdfReader(packet)
    base_pdf = PdfReader(open(input_pdf, "rb"))
    writer = PdfWriter()

    for page in base_pdf.pages:
        writer.add_page(page)
    for page in new_pdf.pages:
        writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

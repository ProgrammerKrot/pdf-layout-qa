from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

import random
import json
import fitz
import io


def add_stamp_to_pdf(input_pdf, output_pdf, stamp_text):
    doc = fitz.open(input_pdf)

    for page in doc:
        rect = page.rect
        x, y = rect.x0 + 10, rect.y1 - 30  # Position at the top
        page.insert_text((x, y), stamp_text, fontsize=18, color=(1, 0, 0))  # Red color

    doc.save(output_pdf)
    doc.close()


def draw_squares_on_pdf(json_path, input_pdf, output_pdf, wrong_ids=None, highlight_color=(1, 0, 0), custom_text="No Diffs"):
    """
    Draws squares and IDs on specific pages of a PDF based on the provided JSON data.
    If `wrong_ids` is provided, it highlights the specified IDs with squares.
    The `square_id` counter does NOT reset on each page.
    If no wrong_ids are provided, prints "No Diffs" in a random location on the first page.

    :param custom_text:
    :param json_path: Path to the JSON file containing coordinates and page numbers.
    :param input_pdf: Path to the input PDF file.
    :param output_pdf: Path to save the output PDF file.
    :param wrong_ids: List of IDs to highlight (optional).
    :param highlight_color: RGB tuple (0-1) for highlight color. Default is red (1, 0, 0).
    """
    with open(json_path, 'r') as file:
        data = json.load(file)

    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    square_id = 1
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]

        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        c.setFont("Times-Bold", 16)

        if page_num == 0 and (wrong_ids is None or not wrong_ids):
            # Get page dimensions
            page_width = float(page.mediabox[2])
            page_height = float(page.mediabox[3])

            x = random.uniform(50, page_width - 150)
            y = random.uniform(50, page_height - 50)

            c.setFillColor(highlight_color)
            c.rect(x - 5, y - 5, 120, 30, fill=1, stroke=0)

            c.setFillColorRGB(0, 0, 0)
            c.drawString(x, y, custom_text)

        for item in data:
            if item["page_number"] - 1 == page_num:
                left, top, width, height = item["left"], item["top"], item["width"], item["height"]
                page_height_val = item["page_height"]
                bottom_left_y = page_height_val - top - height

                c.drawString(left + 5, bottom_left_y + height - 10, str(square_id))

                if wrong_ids and square_id in wrong_ids:
                    c.setStrokeColorRGB(*highlight_color)
                    c.rect(left, bottom_left_y, width, height)
                    c.setStrokeColorRGB(0, 0, 0)

                square_id += 1  

        c.save()
        packet.seek(0)
        overlay_reader = PdfReader(packet)
        overlay_page = overlay_reader.pages[0]
        page.merge_page(overlay_page)

        writer.add_page(page)

    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

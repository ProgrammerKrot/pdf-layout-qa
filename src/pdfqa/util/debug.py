from typing import List, Dict, Any
from pdfqa.constants import *

import fitz
import json

def remove_types(data: List[Dict[str, Any]], types_to_remove: List[str]) -> List[Dict[str, Any]]:
    """
    Removes annotation entries of specified types.

    Args:
        data (List[Dict]): The annotation data.
        types_to_remove (List[str]): List of types to exclude.

    Returns:
        List[Dict]: Filtered annotation data.
    """

    return [item for item in data if item["type"] not in types_to_remove]


def add_text_annotation(pdf_path: str, json_path: str, output_path: str) -> None:
    """
    Adds colored rectangles and text annotations to the PDF based on JSON input.

    Args:
        pdf_path (str): Path to the input PDF.
        json_path (str): Path to the annotation JSON.
        output_path (str): Path to the annotated output PDF.

    Side Effects:
        - Draws rectangles and text annotations.
        - Saves the annotated PDF to disk.
    """

    with open(json_path, 'r', encoding=encoding_format) as file:
        tag_data = json.load(file)

    pdf = fitz.open(pdf_path)

    for tag in tag_data:
        page = pdf[tag['page_number'] - 1]
        rect = fitz.Rect(
            tag['left'],
            tag['top'],
            tag['left'] + tag['width'],
            tag['top'] + tag['height']
        )

        text = tag.get('text') or default_annot_text

        page.draw_rect(rect, color=highlight_rect_color, width=rectangle_width)

        annot = page.add_freetext_annot(rect, text, fontsize=annot_font_size, fontname=annot_font_name)
        annot.set_colors(stroke=highlight_text_color)
        annot.update()

    pdf.save(output_path)
    pdf.close()


def place_tags_on_pdf(pdf_path: str, json_path: str, output_path: str) -> None:
    """
    Places annotation type labels above the tagged areas in the PDF.

    Args:
        pdf_path (str): Path to the input PDF.
        json_path (str): Path to the tag metadata JSON.
        output_path (str): Path to the output PDF.
    """

    with open(json_path, 'r', encoding=encoding_format) as file:
        tag_data = json.load(file)

    pdf = fitz.open(pdf_path)

    for tag in tag_data:
        page = pdf[tag['page_number'] - 1]

        label_rect = fitz.Rect(
            tag['left'],
            tag['top'] - label_offset_top,
            tag['left'] + tag['width'],
            tag['top'] - label_offset_bottom
        )

        label = tag['type']
        page.add_freetext_annot(
            label_rect,
            label,
            fontsize=annot_font_size,
            fontname=annot_font_name
        )

    pdf.save(output_path)
    pdf.close()

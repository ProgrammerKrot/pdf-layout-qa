import fitz
import math
from typing import List, Tuple
from pdfqa.constants import color_euclidean_distance_threshold, dot_color_visual_marker


def int_to_rgb(color: int) -> Tuple[int, int, int]:
    """
    Converts a 24-bit integer color (0xRRGGBB) to an (R, G, B) tuple.

    Args:
        color (int): Color value in int format from PyMuPDF.

    Returns:
        tuple: (R, G, B)
    """

    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    return r, g, b


def get_color_distance(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """
    Calculates Euclidean distance between two RGB colors.

    Args:
        rgb1 (tuple): First color.
        rgb2 (tuple): Second color.

    Returns:
        float: Distance between two RGB colors.
    """

    return math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))


def extract_colors_from_pdf(pdf_path: str) -> List[Tuple[int, int, int]]:
    """
    Extracts RGB colors from text spans in a PDF.

    Args:
        pdf_path (str): Path to PDF file.

    Returns:
        list: List of RGB tuples found in text spans.
    """

    colors = []
    try:
        document = fitz.open(pdf_path)
    except Exception as e:
        print(f"Failed to open PDF: {pdf_path}\nReason: {e}")
        return []

    for page in document:
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        color = span.get("color", 0)
                        if isinstance(color, int):
                            rgb = int_to_rgb(color)
                        else:
                            rgb = tuple(map(int, color))
                        colors.append(rgb)

    return colors


def compare_pdf_colors(pdf_path_1: str, pdf_path_2: str) -> List[Tuple[int, int, int]]:
    """
    Compares colors extracted from two PDFs and returns mismatched ones.

    Args:
        pdf_path_1 (str): First PDF file path.
        pdf_path_2 (str): Second PDF file path.

    Returns:
        list: List of colors from pdf_path_1 not found in pdf_path_2.
    """

    colors_1 = extract_colors_from_pdf(pdf_path_1)
    colors_2 = extract_colors_from_pdf(pdf_path_2)

    mismatched_colors = []

    for color in colors_1:
        if not any(get_color_distance(color, ref_color) < color_euclidean_distance_threshold for ref_color in colors_2):
            mismatched_colors.append(color)

    return mismatched_colors


def mark_mismatched_colors(pdf_path: str, mismatched_colors: List[Tuple[int, int, int]], output_path: str) -> None:
    """
    Marks all spans with mismatched colors in red rectangles and saves the new PDF.

    Args:
        pdf_path (str): Path to input PDF.
        mismatched_colors (list): List of mismatched RGB tuples.
        output_path (str): Path to save annotated PDF.
    """

    try:
        document = fitz.open(pdf_path)
    except Exception as error:
        print(f"Could not open {pdf_path} to annotate: {error}")
        return

    for page in document:
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    color = span.get("color", 0)
                    rgb = int_to_rgb(color) if isinstance(color, int) else tuple(map(int, color))
                    if rgb in mismatched_colors:
                        rect = fitz.Rect(*span["bbox"])
                        page.draw_rect(rect, color=dot_color_visual_marker, width=1)

    document.save(output_path)
    document.close()
    print(f"Annotated PDF saved to: {output_path}")


def main() -> None:
    """
    Entry point for the color comparison process.
    Extracts and compares text colors between two PDFs,
    saves mismatched colors to file and marks them visually in a new PDF.
    """

    from pdfqa.config import MAIN_CONFIG, COLOR_COMPARISON

    pdf_1 = MAIN_CONFIG["default_pdfs"]["pdf1"]
    pdf_2 = MAIN_CONFIG["default_pdfs"]["pdf2"]
    output_pdf = MAIN_CONFIG["output_files"]["processed_pdf1"]
    mismatched_ids_file = COLOR_COMPARISON["mismatched_output_file"]

    mismatched_colors = compare_pdf_colors(pdf_1, pdf_2)

    if mismatched_colors:
        mark_mismatched_colors(pdf_1, mismatched_colors, output_pdf)
        with open(mismatched_ids_file, "w", encoding="utf-8") as f:
            for color in mismatched_colors:
                f.write(f"{color}\n")
        print(f"Mismatched colors saved to: {mismatched_ids_file}")
    else:
        print("No mismatched colors found.")

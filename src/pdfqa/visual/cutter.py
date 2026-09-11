from pdfqa.layout.sorter import sort_json_notes
from typing import Union, List, Dict

import fitz
import os


def validate_output_directory(folder_name: str) -> None:
    """
    Ensures the output folder exists and is empty.

    Args:
        folder_name (str): Path to the output directory.

    Raises:
        RuntimeError: If the folder is not empty.
    """

    os.makedirs(folder_name, exist_ok=True)
    if os.listdir(folder_name):
        raise RuntimeError(f"Folder '{folder_name}' is not empty. Please clear it before running the script.")


def load_and_sort_crop_data(crop_data: Union[str, List[Dict]]) -> List[Dict]:
    """
    Loads and sorts crop data from a JSON file or returns preloaded data.

    Args:
        crop_data (Union[str, List[Dict]]): Path to JSON file or list of crop dicts.

    Returns:
        List[Dict]: Sorted crop regions.

    Raises:
        TypeError: If crop_data is not str or list of dicts.
    """

    if isinstance(crop_data, str):
        return sort_json_notes(crop_data)
    elif isinstance(crop_data, list):
        return crop_data
    else:
        raise TypeError("crop_data must be either a file path (str) or a list of dictionaries.")


def crop_and_save(
    pdf_path: str,
    output_prefix: str,
    crop_data: Union[str, List[Dict]],
    folder_name: str
) -> None:
    """
    Crops specified rectangular regions from a PDF and saves each region as an individual PDF.

    Args:
        pdf_path (str): Path to the source PDF file.
        output_prefix (str): Prefix for naming the cropped output PDF files.
        crop_data (Union[str, List[Dict]]): Either a path to a JSON file with crop coordinates,
                                            or a preloaded list of crop regions.
        folder_name (str): Directory where cropped PDF files will be stored.

    Side Effects:
        - Creates output directory if it does not exist.
        - Throws an error if the output directory is not empty.
        - Saves multiple PDF files, each corresponding to a cropped region.
    """

    validate_output_directory(folder_name)
    sorted_crop_data = load_and_sort_crop_data(crop_data)
    document = fitz.open(pdf_path)

    for i, crop in enumerate(sorted_crop_data, 1):
        rect = fitz.Rect(
            crop["left"],
            crop["top"],
            crop["left"] + crop["width"],
            crop["top"] + crop["height"]
        )

        new_doc = fitz.open()
        new_page = new_doc.new_page(width=rect.width, height=rect.height)
        new_page.show_pdf_page(
            new_page.rect,
            document,
            crop["page_number"] - 1,
            clip=rect
        )

        output_path = os.path.join(folder_name, f"{output_prefix}_crop_{i}.pdf")
        new_doc.save(output_path)
        new_doc.close()

    document.close()

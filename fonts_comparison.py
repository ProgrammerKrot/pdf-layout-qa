import os
import fitz
import multiprocessing
from multiprocessing import Manager
from typing import Dict, Set, Tuple, Union, List


def extract_fonts(pdf_path: str) -> Set[str]:
    """
    Extracts unique font names from all pages of a PDF.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        Set[str]: A set of font names used in the PDF.
    """

    doc = fitz.open(pdf_path)
    fonts = set()

    for page in doc:
        for font in page.get_fonts():
            font_name = font[3].split('+')[-1]
            fonts.add(font_name)

    return fonts


def process_pdf_fonts(file_name: str, folder: str, fonts_dict: dict) -> None:
    """
    Extracts fonts from a PDF and stores the result in a shared dictionary.

    Args:
        file_name (str): PDF file name.
        folder (str): Folder path where the PDF resides.
        fonts_dict (dict): Shared dictionary for storing font sets.
    """

    file_path = os.path.join(folder, file_name)
    if not os.path.exists(file_path):
        return

    fonts_dict[file_name] = extract_fonts(file_path)


def compare_fonts(
    fonts_dict1: Dict[str, Set[str]],
    fonts_dict2: Dict[str, Set[str]]
) -> Dict[str, Dict[str, Union[Set[str], Dict[str, Set[str]]]]]:
    """
    Compares fonts used between two dictionaries of PDF files.

    Args:
        fonts_dict1 (dict): Font sets for source A.
        fonts_dict2 (dict): Font sets for source B.

    Returns:
        dict: A dictionary of mismatched files and their font differences.
    """

    mismatched_files = {}

    for file_name in fonts_dict1:
        if file_name in fonts_dict2:
            fonts1 = fonts_dict1[file_name]
            fonts2 = fonts_dict2[file_name]

            if fonts1 != fonts2:
                mismatched_files[file_name] = {
                    "SFE_Fonts": fonts1,
                    "SFS_Fonts": fonts2,
                    "Mismatched_Fields": {
                        "In_SFE_Not_In_SFS": fonts1 - fonts2,
                        "In_SFS_Not_In_SFE": fonts2 - fonts1
                    }
                }

    return mismatched_files


def main_fontique(folder_1: str, folder_2: str) -> Tuple[bool, Union[None, Dict]]:
    """
    Orchestrates the font extraction and comparison between two folders.

    Args:
        folder_1 (str): Path to folder containing version A PDFs.
        folder_2 (str): Path to folder containing version B PDFs.

    Returns:
        Tuple[bool, Union[None, dict]]: Match status and mismatched data if any.
    """

    files_1 = set(os.listdir(folder_1))
    files_2 = set(os.listdir(folder_2))
    pdf_files = [f for f in files_1.intersection(files_2) if f.endswith(".pdf")]

    manager = Manager()
    fonts_dict_1 = manager.dict()
    fonts_dict_2 = manager.dict()
    processes = []

    for pdf in pdf_files:
        p_1 = multiprocessing.Process(target=process_pdf_fonts, args=(pdf, folder_1, fonts_dict_1))
        p_2 = multiprocessing.Process(target=process_pdf_fonts, args=(pdf, folder_2, fonts_dict_2))
        processes.extend([p_1, p_2])
        p_1.start()
        p_2.start()

    for p in processes:
        p.join()

    mismatches = compare_fonts(dict(fonts_dict_1), dict(fonts_dict_2))

    if mismatches:
        for file_name, mismatch_info in mismatches.items():
            print(f"  - {file_name}:")
            print(f"    SFE Fonts: {mismatch_info['SFE_Fonts']}")
            print(f"    SFS Fonts: {mismatch_info['SFS_Fonts']}")
            print(f"    Differences: {mismatch_info['Mismatched_Fields']}")
        return False, mismatches

    return True, None


def convert_fonts_to_numbers(data: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Maps each unique font name to a unique number across all mismatched files.

    Args:
        data (dict): Mismatched data with font names.

    Returns:
        dict: Same structure, but font names replaced with corresponding numbers.
    """

    all_fonts = set()

    for info in data.values():
        all_fonts.update(info.get("SFE_Fonts", set()))
        all_fonts.update(info.get("SFS_Fonts", set()))

    font_to_id = {font: idx for idx, font in enumerate(sorted(all_fonts), 1)}

    converted = {}
    for file_name, info in data.items():
        converted[file_name] = {
            "SFE_Fonts": {font_to_id[font] for font in info["SFE_Fonts"]},
            "SFS_Fonts": {font_to_id[font] for font in info["SFS_Fonts"]},
            "Mismatched_Fields": {
                "In_SFE_Not_In_SFS": {font_to_id[f] for f in info["Mismatched_Fields"]["In_SFE_Not_In_SFS"]},
                "In_SFS_Not_In_SFE": {font_to_id[f] for f in info["Mismatched_Fields"]["In_SFS_Not_In_SFE"]}
            }
        }

    return converted


def get_mismatched_ids(mismatched_data: Dict[str, Dict]) -> List[int]:
    """
    Extracts font mismatch identifiers across all files.

    Args:
        mismatched_data (dict): Output from font comparison with numeric mapping.

    Returns:
        List[int]: Sorted list of all unique font ID mismatches.
    """

    mismatched_ids = set()

    for file_info in mismatched_data.values():
        mismatched_ids.update(file_info["Mismatched_Fields"]["In_SFE_Not_In_SFS"])
        mismatched_ids.update(file_info["Mismatched_Fields"]["In_SFS_Not_In_SFE"])

    return sorted(mismatched_ids)

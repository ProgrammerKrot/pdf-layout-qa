from typing import List, Dict, Any
from pdfqa.constants import *

import json

def sort_json_notes(json_file: str) -> List[Dict[str, Any]]:
    """
    Sorts annotation entries first by page number, then by layout (columns and rows).

    Args:
        json_file (str): Path to a JSON file containing tag data.

    Returns:
        List[Dict]: A sorted list of annotation dictionaries.
    """

    with open(json_file, 'r', encoding=encoding_format) as file:
        notes = json.load(file)

    pages = {}
    for note in notes:
        page = note["page_number"]
        pages.setdefault(page, []).append(note)

    for page_num in pages:
        notes_on_page = pages[page_num]
        sorted_by_left = sorted(notes_on_page, key=lambda x: x['left'])

        columns = []

        for note in sorted_by_left:
            added = False
            for col in columns:
                if abs(note['left'] - col[0]['left']) <= column_threshold_param:
                    col.append(note)
                    added = True
                    break
            if not added:
                columns.append([note])

        for col in columns:
            col.sort(key=lambda x: (x['top'], x['left']))
        columns.sort(key=lambda x: x[0]['left'])

        sorted_column_notes = []
        for col in columns:
            sorted_column_notes.extend(col)

        pages[page_num] = sorted_column_notes

    final_sorted = []
    for page in sorted(pages.keys()):
        final_sorted.extend(pages[page])

    return final_sorted

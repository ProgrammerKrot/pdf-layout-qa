from typing import List, Dict, Tuple
import json


def sort_json_notes(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        notes = json.load(file)

    pages = {}
    for note in notes:
        page = note["page_number"]
        if page not in pages:
            pages[page] = []
        pages[page].append(note)

    for page in pages:
        pages[page].sort(key=lambda note: (note["top"], note["left"]))

    sorted_notes = [note for page in sorted(pages.keys()) for note in pages[page]]

    return sorted_notes


def remove_types(data, types_to_remove):
    return [item for item in data if item["type"] not in types_to_remove]



def load_json(file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def sort_elements(elements: List[Dict]) -> List[Dict]:
    return sorted(elements, key=lambda x: (x['page_number'], x['top'], x['left']))


def merge_elements(elements: List[Dict]) -> List[Dict]:
    merged = []
    for elem in elements:
        if merged and merged[-1]['type'] == elem['type'] and abs(
                merged[-1]['top'] + merged[-1]['height'] - elem['top']) <= 5:
            merged[-1]['text'] += ' ' + elem['text']
            merged[-1]['height'] += elem['height']
            merged[-1]['width'] = max(merged[-1]['width'], elem['width'])
        else:
            merged.append(elem)
    return merged


def align_json_files(file1: str, file2: str) -> Tuple[List[Dict], List[Dict]]:
    json1 = load_json(file1)
    json2 = load_json(file2)

    json1_sorted = merge_elements(sort_elements(json1))
    json2_sorted = merge_elements(sort_elements(json2))

    return json1_sorted, json2_sorted


def save_json(data: List[Dict], file_path: str):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def merge_overlapping_pair(json1, json2):
    merged_json1 = []
    merged_json2 = []
    i, j = 0, 0
    len1, len2 = len(json1), len(json2)

    while i < len1 or j < len2:
        if i < len1 and j < len2:
            elem1 = json1[i]
            elem2 = json2[j]

            # Check if elements overlap in position
            if (elem1['left'] <= elem2['left'] + elem2['width'] and
                    elem1['left'] + elem1['width'] >= elem2['left'] and
                    elem1['top'] <= elem2['top'] + elem2['height'] and
                    elem1['top'] + elem1['height'] >= elem2['top']):

                # Merge the text and update dimensions
                merged_elem1 = {
                    'left': min(elem1['left'], elem2['left']),
                    'top': min(elem1['top'], elem2['top']),
                    'width': max(elem1['left'] + elem1['width'], elem2['left'] + elem2['width']) - min(elem1['left'],
                                                                                                       elem2['left']),
                    'height': max(elem1['top'] + elem1['height'], elem2['top'] + elem2['height']) - min(elem1['top'],
                                                                                                        elem2['top']),
                    'page_number': elem1['page_number'],
                    'page_width': elem1['page_width'],
                    'page_height': elem1['page_height'],
                    'text': elem1['text'] + ' ' + elem2['text'],
                    'type': elem1['type'] if elem1['type'] == elem2['type'] else 'Formula'
                }
                merged_elem2 = merged_elem1  # Both JSONs will have the same merged element
                merged_json1.append(merged_elem1)
                merged_json2.append(merged_elem2)
                i += 1
                j += 1
            elif elem1['top'] < elem2['top'] or (elem1['top'] == elem2['top'] and elem1['left'] < elem2['left']):
                merged_json1.append(elem1)
                i += 1
            else:
                merged_json2.append(elem2)
                j += 1
        elif i < len1:
            merged_json1.append(json1[i])
            i += 1
        else:
            merged_json2.append(json2[j])
            j += 1

    return merged_json1, merged_json2

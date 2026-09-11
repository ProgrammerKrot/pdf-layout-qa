from typing import List, Dict
import json

class PrecisionParagraphMerger:
    def __init__(self):
        self.paragraph_starts = []
        self.continuation_indicators = [":", ";", ",", "•"]

    def should_merge(self, current: Dict, next_field: Dict) -> bool:
        if not (abs(current["left"] - next_field["left"])) < 25:
            return False
        if not (abs(current["top"] + current["height"] - next_field["top"])) < 35:
            return False

        current_text = current["text"].strip()
        next_text = next_field["text"].strip()

        if any(current_text.startswith(marker) for marker in self.paragraph_starts):
            return True

        if any(current_text.endswith(indicator) for indicator in self.continuation_indicators):
            return True

        if len(next_text) > 0 and (next_text.startswith("•") or next_text[0].islower()):
            return True

        return False

    def merge_specific_paragraphs(self, document: List[Dict]) -> List[Dict]:
        if not document:
            return document

        sorted_doc = sorted(document, key=lambda x: (x["page_number"], x["top"], x["left"]))
        merged = []
        i = 0
        n = len(sorted_doc)

        while i < n:
            current = sorted_doc[i]

            if i + 1 < n:
                next_field = sorted_doc[i + 1]

                if self.should_merge(current, next_field):
                    # Create merged paragraph
                    merged.append({
                        "left": min(current["left"], next_field["left"]),
                        "top": current["top"],
                        "width": max(current["width"], next_field["width"]),
                        "height": (next_field["top"] + next_field["height"]) - current["top"],
                        "text": f"{current['text']} {next_field['text']}".strip(),
                        "type": "Paragraph",
                        "page_number": current["page_number"],
                        "page_width": current["page_width"],
                        "page_height": current["page_height"]
                    })
                    i += 2  # Skip the next field
                    continue

            merged.append(current)
            i += 1

        return merged


def process_file(input_path: str, output_path: str):
    merger = PrecisionParagraphMerger()

    with open(input_path, 'r', encoding='utf-8') as f:
        doc = json.load(f)

    merged_doc = merger.merge_specific_paragraphs(doc)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(merged_doc, f, indent=4, ensure_ascii=False)
    print(f"Success. Merged {len(doc) - len(merged_doc)} fields in {input_path}")


def copy_json_file(source_file_path, target_file_path):
    with open(source_file_path, 'r') as source_file:
        source_data = json.load(source_file)

    with open(target_file_path, 'w') as target_file:
        json.dump(source_data, target_file, indent=2)

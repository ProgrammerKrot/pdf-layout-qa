from config import MODEL_CONFIG, FIELD_MATCHING, FIELD_PATTERNS
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from custom_constants import *

import json
import os
from typing import List, Dict, Any

model = SentenceTransformer(MODEL_CONFIG[model_name])


def get_doc_pattern(pdf_1: str, pdf_2: str) -> int:
    """
    Placeholder function for comparing structural PDF patterns.

    Args:
        pdf_1 (str): First PDF descriptor or path.
        pdf_2 (str): Second PDF descriptor or path.

    Returns:
        int: Score or pattern class. Currently, hardcoded.
    """
    return default_doc_pattern_score


def get_semantic_similarity(text_1: str, text_2: str) -> float:
    """
    Computes multilingual semantic similarity between two text segments.

    Args:
        text_1 (str): First text input.
        text_2 (str): Second text input.

    Returns:
        float: Cosine similarity score (0.0–1.0). Returns 0.0 if text is empty.
    """
    if not text_1 or not text_2:
        return default_similarity_score

    embeddings = model.encode([text_1, text_2], convert_to_tensor=True)
    return cosine_similarity(embeddings[0:1], embeddings[1:2])[0][0]


def is_similar_position(item_1: Dict[str, Any], item_2: Dict[str, Any]) -> bool:
    """
    Checks whether two items are in similar positions and sizes.

    Args:
        item_1 (Dict): First field item.
        item_2 (Dict): Second field item.

    Returns:
        bool: True if spatially similar.
    """
    def get_relative(item):
        return {
            "left": item["left"] / item["page_width"],
            "top": item["top"] / item["page_height"],
            "width": item["width"] / item["page_width"],
            "height": item["height"] / item["page_height"]
        }

    pos_1 = get_relative(item_1)
    pos_2 = get_relative(item_2)

    return (
        abs(pos_1["left"] - pos_2["left"]) < FIELD_MATCHING["size_tolerance"] and
        abs(pos_1["top"] - pos_2["top"]) < FIELD_MATCHING["size_tolerance"] and
        abs(pos_1["width"] - pos_2["width"]) < FIELD_MATCHING["size_tolerance"] and
        abs(pos_1["height"] - pos_2["height"]) < FIELD_MATCHING["size_tolerance"]
    )


def is_same_field(item_1: Dict[str, Any], item_2: Dict[str, Any]) -> bool:
    """
    Determines if two field items match semantically or structurally.

    Args:
        item_1 (Dict): First field dictionary.
        item_2 (Dict): Second field dictionary.

    Returns:
        bool: True if fields match.
    """
    if (not item_1["text"].strip() or not item_2["text"].strip()) and \
       (item_1["type"] == "Picture" or item_2["type"] == "Picture"):
        return is_similar_position(item_1, item_2)

    text_1 = item_1["text"].lower()
    text_2 = item_2["text"].lower()

    for _, patterns in FIELD_PATTERNS.items():
        if any(p in text_1 for p in patterns) and any(p in text_2 for p in patterns):
            return True

    if (
        len(item_1["text"]) > FIELD_MATCHING["min_text_length_for_semantic"] and
        len(item_2["text"]) > FIELD_MATCHING["min_text_length_for_semantic"]
    ):
        similarity = get_semantic_similarity(item_1["text"], item_2["text"])
        if similarity > FIELD_MATCHING["semantic_similarity_threshold"]:
            return True

    return is_similar_position(item_1, item_2)


def update_tags_based_on_reference(
    json_data: List[Dict[str, Any]],
    reference_data: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Updates 'type' values in json_data based on reference_data matching.

    Args:
        json_data (List): Fields to update.
        reference_data (List): Reference field list.

    Returns:
        List[Dict]: Updated field list with new 'type' tags.
    """
    for item in json_data:
        best_match = None
        highest_score = 0.0

        for ref_item in reference_data:
            score = 0.0
            if is_similar_position(item, ref_item):
                score += FIELD_MATCHING["position_score_weight"]
            if is_same_field(item, ref_item):
                score += FIELD_MATCHING["field_match_score_weight"]

            if score > FIELD_MATCHING["score_threshold"] and score > highest_score:
                highest_score = score
                best_match = ref_item

        if best_match and item["type"] != best_match["type"]:
            item["type"] = best_match["type"]

    return json_data


def load_json(file_path: str) -> Any:
    """
    Loads JSON from file.

    Args:
        file_path (str): Path to JSON file.

    Returns:
        Parsed JSON (list or dict).
    """
    with open(file_path, 'r', encoding=encoding_format) as file:
        return json.load(file)


def save_json(file_path: str, data: Any) -> None:
    """
    Saves data to a JSON file.

    Args:
        file_path (str): Path to save JSON.
        data (Any): Serializable object to write.
    """
    with open(file_path, 'w', encoding=encoding_format) as file:
        json.dump(data, file, indent=indent_parameter, ensure_ascii=False)


def process_json_files(file_paths: List[str]) -> None:
    """
    Processes a list of JSON files by comparing and updating their tags mutually.

    Args:
        file_paths (List[str]): Paths to JSON files.
    """
    json_files = [load_json(path) for path in file_paths]

    for i, current in enumerate(json_files):
        reference = []
        for j, other in enumerate(json_files):
            if i != j:
                reference.extend(other)

        json_files[i] = update_tags_based_on_reference(current, reference)
        save_json(file_paths[i], json_files[i])


def remove_types_from_json(file_path: str, types_to_remove: List[str]) -> None:
    """
    Removes specified types from JSON and writes new file with '_removed' suffix.

    Args:
        file_path (str): Path to input JSON.
        types_to_remove (List[str]): Types to remove.
    """
    with open(file_path, 'r', encoding=encoding_format) as file:
        data = json.load(file)

    filtered = [item for item in data if item["type"] not in types_to_remove]
    base, _ = os.path.splitext(file_path)
    output_path = f"{base}_removed.json"

    with open(output_path, 'w', encoding=encoding_format) as file:
        json.dump(filtered, file, indent=indent_parameter, ensure_ascii=False)

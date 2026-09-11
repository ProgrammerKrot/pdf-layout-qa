from config import FIELD_MATCHING, PROCESS_CONFIG, MP_CONFIG, MAIN_CONFIG, DIR_CONFIG, COLOR_COMPARISON, FONT_COMPARISON
from smart_comparison import tiny_tony
import json
import copy

_original_configs = {}


def backup_configs():
    """Backup all current configurations to restore later"""
    global _original_configs
    _original_configs = {
        "FIELD_MATCHING": copy.deepcopy(FIELD_MATCHING),
        "PROCESS_CONFIG": copy.deepcopy(PROCESS_CONFIG),
        "MP_CONFIG": copy.deepcopy(MP_CONFIG),
        "MAIN_CONFIG": copy.deepcopy(MAIN_CONFIG),
        "DIR_CONFIG": copy.deepcopy(DIR_CONFIG),
        "COLOR_COMPARISON": copy.deepcopy(COLOR_COMPARISON),
        "FONT_COMPARISON": copy.deepcopy(FONT_COMPARISON)
    }


def restore_configs():
    """Restore configurations from backup"""
    if not _original_configs:
        raise ValueError("No configurations have been backed up yet")

    FIELD_MATCHING.clear()
    FIELD_MATCHING.update(_original_configs["FIELD_MATCHING"])

    PROCESS_CONFIG.clear()
    PROCESS_CONFIG.update(_original_configs["PROCESS_CONFIG"])

    MP_CONFIG.clear()
    MP_CONFIG.update(_original_configs["MP_CONFIG"])

    MAIN_CONFIG.clear()
    MAIN_CONFIG.update(_original_configs["MAIN_CONFIG"])

    DIR_CONFIG.clear()
    DIR_CONFIG.update(_original_configs["DIR_CONFIG"])

    COLOR_COMPARISON.clear()
    COLOR_COMPARISON.update(_original_configs["COLOR_COMPARISON"])

    FONT_COMPARISON.clear()
    FONT_COMPARISON.update(_original_configs["FONT_COMPARISON"])


def configure_and_run(
        # Thresholds & Tolerances
        semantic_similarity_threshold=None,
        position_tolerance=None,
        size_tolerance=None,
        score_threshold=None,
        color_threshold=None,
        font_size_tolerance=None,

        # Highlight & Visualization Settings
        dot_color=None,
        dot_radius=None,
        highlight_colors=None,

        # Processing Preferences
        multiprocessing_enabled=None,
        default_types_to_remove=None,

        # Output & Folder Configurations
        processed_folder=None,
        output_files=None,

        # PDF files to compare (optional)
        pdf1=None,
        pdf2=None,

        # Restore defaults after run
        restore_after=False
):
    # Backup original configurations if not already backed up
    if not _original_configs:
        backup_configs()

    try:
        if semantic_similarity_threshold is not None:
            FIELD_MATCHING["semantic_similarity_threshold"] = semantic_similarity_threshold
        if position_tolerance is not None:
            FIELD_MATCHING["position_tolerance"] = position_tolerance
        if size_tolerance is not None:
            FIELD_MATCHING["size_tolerance"] = size_tolerance
        if score_threshold is not None:
            FIELD_MATCHING["score_threshold"] = score_threshold

        if color_threshold is not None:
            COLOR_COMPARISON["color_threshold"] = color_threshold

        if font_size_tolerance is not None:
            FONT_COMPARISON["size_tolerance"] = font_size_tolerance

        if dot_color is not None:
            PROCESS_CONFIG["dot_color"] = dot_color
        if dot_radius is not None:
            PROCESS_CONFIG["dot_radius"] = dot_radius

        if highlight_colors is not None:
            MAIN_CONFIG["highlight_colors"].update(highlight_colors)
        if default_types_to_remove is not None:
            MAIN_CONFIG["default_types_to_remove"] = default_types_to_remove
        if output_files is not None:
            MAIN_CONFIG["output_files"].update(output_files)

        if multiprocessing_enabled is not None:
            MP_CONFIG["enabled"] = multiprocessing_enabled

        if processed_folder is not None:
            DIR_CONFIG["processed_folder"] = processed_folder

        pdf1_to_use = pdf1 if pdf1 is not None else MAIN_CONFIG["default_pdfs"]["pdf1"]
        pdf2_to_use = pdf2 if pdf2 is not None else MAIN_CONFIG["default_pdfs"]["pdf2"]

        tiny_tony(pdf1_to_use, pdf2_to_use)

    finally:
        if restore_after:
            restore_configs()


def run_default():
    """Run the comparison with all default configurations"""
    if _original_configs:
        restore_configs()
    pdf1 = MAIN_CONFIG["default_pdfs"]["pdf1"]
    pdf2 = MAIN_CONFIG["default_pdfs"]["pdf2"]
    tiny_tony(pdf1, pdf2)


# Example usage:
if __name__ == "__main__":
    backup_configs()

    configure_and_run(
        highlight_colors={"font_size": (1, 0.5, 0)},
        restore_after=True
    )

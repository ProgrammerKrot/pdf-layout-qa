import os

from reportlab.lib import colors

from pdfqa.constants import output_folder_root, result_folder_root

LAYOUT_SERVICE_URL = os.getenv("LAYOUT_SERVICE_URL", "http://127.0.0.1:5060")

# ======================= align_tags.py ========================

MODEL_CONFIG = {
    "model_name": "paraphrase-multilingual-MiniLM-L12-v2"
}

FIELD_MATCHING = {
    "semantic_similarity_threshold": 0.75,
    "position_tolerance": 30,
    "size_tolerance": 0.2,
    "min_text_length_for_semantic": 10,

    "position_score_weight": 0.4,
    "field_match_score_weight": 0.6,
    "score_threshold": 0.7
}

FIELD_PATTERNS = {
    "employee_name": ["employee name", "nombre del empleado"],
    "ssn": ["social security", "seguro social", "ssn"],
    "signature": ["sign here", "firme aquí", "signature", "firma"],
    "date": ["date", "fecha"],

    "footer": ["of", "de"],
    "section_header": [
        "section", "sección",
        "section a", "sección a",
        "section b", "sección b",
        "section c", "sección c",
        "section d", "sección d",
        "section e", "sección e",
        "section f", "sección f",
        "section g", "sección g",
        "section h", "sección h"
    ],

    "eligible_dependent": [
        "eligible dependent", "dependiente elegible",
        "dependents eligible", "los dependientes elegibles",
        "eligible dependents", "dependientes elegibles"
    ],

    "select_one": ["select one", "seleccione uno"],
    "coverage_type": ["type of coverage", "tipo de cobertura"],

    "address": ["address", "dirección"],
    "city": ["city", "ciudad"],
    "state": ["state", "estado"],
    "zip_code": ["zip code", "código postal"],

    "employer_name": ["employer name", "nombre del empleador"],
    "date_of_hire": ["date of hire", "fecha de contratación"],

    "primary_care": ["primary care physician", "médico de atención primaria"],
    "patient_status": ["existing patient", "paciente existente"]
}

PDF_PATTERNS = {
    "pdf1": 27,
    "pdf2": 12
}

# ======================= isolated_comparison.py ========================

DIR_CONFIG = {
    "sfe_folder": "SFE",
    "sfs_folder": "SFS",
    "coords_folder": "coordinates",
    "processed_folder": "processed_pdfs",
    "groop_folders": ["GROOP/SFE", "GROOP/SFS"]
}

PROCESS_CONFIG = {
    "threshold": 18,           # Default comparison threshold
    "y_threshold": 13,         # Y-coordinate threshold for dot processing
    "dot_color": (255, 0, 0),  # Red color for dots (RGB)
    "dot_radius": 4            # Radius of dots in pixels
}

MP_CONFIG = {
    "enabled": True
}

# ======================= color_comparison.py ========================

COLOR_COMPARISON = {
    "sfe_folder": "GROOP/SFE",
    "sfs_folder": "GROOP/SFS",
    "color_threshold": 75,     # Color comparison threshold (Euclidean distance)
    "mismatched_output_file": "mismatched_ids.txt",
    "stamp_text": "COLORS ARE NOT STABILIZED",
    "temp_file_prefix": "SHTAMP"
}

# ======================= font_size.py ========================

FONT_COMPARISON = {
    "sfe_folder": "GROOP/SFE",
    "sfs_folder": "GROOP/SFS",
    "size_tolerance": 0.01,
    "report_styles": {
        "header1": {
            "font_size": 16,
            "leading": 18,
            "space_after": 12,
            "text_color": "#FFFFFF",
            "background_color": "#4472C4",
            "alignment": 1
        },
        "header2": {
            "font_size": 12,
            "leading": 14,
            "space_after": 6,
            "text_color": "#2F5597",
            "space_before": 12
        },
        "diff_item": {
            "font_size": 9,
            "leading": 11,
            "space_after": 3,
            "bullet_indent": 12,
            "left_indent": 12
        },
        "colors": {
            "extra": "#C00000",      # Red for extras
            "missing": "#70AD47"     # Green for missing
        }
    },
    "table_styles": {
        "background_color": "#D9E1F2",
        "font_name": "Helvetica",
        "font_size": 9,
        "grid_color": colors.lightgrey
    }
}

MAIN_CONFIG = {
    "container_port": 5060,
    "input_folders": ["GROOP", "coordinates", "SFE", "SFS", "processed_pdfs/SFE", "processed_pdfs/SFS", "TrashBin", "processed_pdfs"],
    "output_files": {
        "initial_output1": f"{output_folder_root}/output1.json",
        "initial_output2": f"{output_folder_root}/output2.json",
        "sorted_output1": f"{output_folder_root}/sorted_doc1.json",
        "sorted_output2": f"{output_folder_root}/sorted_doc2.json",
        "final_output1": f"{output_folder_root}/aligned_doc1.json",
        "final_output2": f"{output_folder_root}/aligned_doc2.json",
        "removed_output1": f"{output_folder_root}/aligned_doc1_removed.json",
        "removed_output2": f"{output_folder_root}/aligned_doc2_removed.json",
        "processed_pdf1": f"{result_folder_root}/doc1_annotated.pdf",
        "processed_pdf2": f"{result_folder_root}/doc2_annotated.pdf"
    },

    "default_types_to_remove": ["Page footer", "Page header"],
    "highlight_colors": {
        "line_comparison": (1, 0, 0),   # Red
        "color_comparison": (0, 1, 0),  # Green
        "font_comparison": (0, 0, 1),   # Blue
        "font_size": (0, 1, 1)          # Cyan
    },
    "comparison_texts": {
        "line_comparison": "Lines are equal",
        "color_comparison": "Colors are equal",
        "font_comparison": "Fonts are equal",
        "font_size": "Sizes are equal"
    },
    "default_pdfs": {
        "pdf1": "samples/form_en.pdf",
        "pdf2": "samples/form_es.pdf"
    },
    "fallback_layouts": {
        "pdf1": "samples/form_en.json",
        "pdf2": "samples/form_es.json"
    }
}

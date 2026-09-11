from pdfqa.layout.align import process_json_files, remove_types_from_json
from pdfqa.visual.annotate import draw_squares_on_pdf
from pdfqa.visual.cutter import crop_and_save
from pdfqa.config import LAYOUT_SERVICE_URL, MAIN_CONFIG
from pdfqa.constants import *
from pdfqa.layout.json_sorter import *

import pdfqa.visual.lines as isolated_comparison
import pdfqa.visual.fonts as fonts_comparison
import pdfqa.util.cleanup as cleanup_files
import pdfqa.visual.colors as color_palette
import pdfqa.visual.font_sizes as font_sized
import pdfqa.layout.merger as merger

import json
import os
import re
import shutil
import subprocess

os.environ["TOKENIZERS_PARALLELISM"] = "false"


def layout_service_url(port):
    if "LAYOUT_SERVICE_URL" in os.environ:
        return os.environ["LAYOUT_SERVICE_URL"].strip()
    return LAYOUT_SERVICE_URL or f"http://127.0.0.1:{port}"


def send_pdf_to_container(pdf_path, port):
    """POST a PDF to the Huridocs layout service. Returns raw JSON text."""
    url = layout_service_url(port)
    if not url:
        raise RuntimeError("layout service disabled")
    command = ["curl", "-X", "POST", "-F", f"file=@{pdf_path}", url]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "layout service request failed")
    return result.stdout


def _layout_sidecar(pdf_path):
    stem, _ = os.path.splitext(pdf_path)
    return f"{stem}.json"


def extract_layout(pdf_path, json_out, port, fallback_path=None):
    """
    Prefer the Huridocs container.
    If it is down, copy a sidecar JSON next to the PDF, then a configured fallback.
    """
    try:
        raw = send_pdf_to_container(pdf_path, port)
        data = json.loads(raw)
        os.makedirs(os.path.dirname(json_out) or ".", exist_ok=True)
        with open(json_out, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=indent_parameter)
        return
    except (RuntimeError, json.JSONDecodeError, FileNotFoundError, OSError) as exc:
        print(f"Layout service unavailable ({exc}). Using local JSON.")

    for candidate in (_layout_sidecar(pdf_path), fallback_path):
        if candidate and os.path.isfile(candidate):
            os.makedirs(os.path.dirname(json_out) or ".", exist_ok=True)
            shutil.copyfile(candidate, json_out)
            return

    raise FileNotFoundError(
        f"No layout JSON for {pdf_path}. Start the Huridocs container or add {_layout_sidecar(pdf_path)}."
    )


def update_pdf():
    return (
        MAIN_CONFIG[output_file_name][processed_pdf_1],
        MAIN_CONFIG[output_file_name][processed_pdf_2],
    )


def handle_comparison(pdf_1, pdf_2, numbers, comparison_key: str):
    draw_squares_on_pdf(
        MAIN_CONFIG[output_file_name][final_output_1],
        pdf_1,
        MAIN_CONFIG[output_file_name][processed_pdf_1],
        numbers,
        highlight_color=MAIN_CONFIG[highlight_colors][comparison_key],
        custom_text=MAIN_CONFIG[text_comparison][comparison_key]
    )

    draw_squares_on_pdf(
        MAIN_CONFIG[output_file_name][final_output_2],
        pdf_2,
        MAIN_CONFIG[output_file_name][processed_pdf_2],
        numbers,
        highlight_color=MAIN_CONFIG[highlight_colors][comparison_key],
        custom_text=MAIN_CONFIG[text_comparison][comparison_key]
    )


def extract_both(pdf_1, pdf_2):
    fallbacks = MAIN_CONFIG.get("fallback_layouts", {})
    extract_layout(
        pdf_1,
        MAIN_CONFIG[output_file_name][initial_output_1],
        MAIN_CONFIG[container_port],
        fallbacks.get("pdf1"),
    )
    extract_layout(
        pdf_2,
        MAIN_CONFIG[output_file_name][initial_output_2],
        MAIN_CONFIG[container_port],
        fallbacks.get("pdf2"),
    )


def compare_pdfs(pdf_1, pdf_2, line_comparison_check=True, color_comparison_check=True,
                 font_comparison_check=True, font_size_check=True):
    """Run layout extraction, field matching, and visual mismatch annotation."""
    cleanup_files.ensure_clean_folder(output_folder_root)
    cleanup_files.ensure_clean_folder(result_folder_root)

    extract_both(pdf_1, pdf_2)

    sorted_output_aaa = sort_json_notes(MAIN_CONFIG[output_file_name][initial_output_1])
    sorted_output_aae = sort_json_notes(MAIN_CONFIG[output_file_name][initial_output_2])

    with open(MAIN_CONFIG[output_file_name][sorted_output_1], "w", encoding=encoding_format) as output_file_1:
        json.dump(sorted_output_aaa, output_file_1, indent=indent_parameter, ensure_ascii=False)

    with open(MAIN_CONFIG[output_file_name][sorted_output_2], "w", encoding=encoding_format) as output_file_2:
        json.dump(sorted_output_aae, output_file_2, indent=indent_parameter, ensure_ascii=False)

    merger.process_file(MAIN_CONFIG[output_file_name][sorted_output_1],
                        MAIN_CONFIG[output_file_name][final_output_1])
    merger.process_file(MAIN_CONFIG[output_file_name][sorted_output_2],
                        MAIN_CONFIG[output_file_name][final_output_2])

    process_json_files([
        MAIN_CONFIG[output_file_name][final_output_1],
        MAIN_CONFIG[output_file_name][final_output_2]
    ])

    remove_types_from_json(MAIN_CONFIG[output_file_name][final_output_1],
                           MAIN_CONFIG[default_types_to_remove])
    remove_types_from_json(MAIN_CONFIG[output_file_name][final_output_2],
                           MAIN_CONFIG[default_types_to_remove])

    draw_squares_on_pdf(MAIN_CONFIG[output_file_name][removed_output_1],
                        pdf_1, MAIN_CONFIG[output_file_name][processed_pdf_1])
    draw_squares_on_pdf(MAIN_CONFIG[output_file_name][removed_output_2],
                        pdf_2, MAIN_CONFIG[output_file_name][processed_pdf_2])

    merger.copy_json_file(MAIN_CONFIG[output_file_name][removed_output_1],
                          MAIN_CONFIG[output_file_name][final_output_1])
    merger.copy_json_file(MAIN_CONFIG[output_file_name][removed_output_2],
                          MAIN_CONFIG[output_file_name][final_output_2])

    crop_and_save(pdf_1, crop_and_save_filename, MAIN_CONFIG[output_file_name][final_output_1], folder_1)
    crop_and_save(pdf_2, crop_and_save_filename, MAIN_CONFIG[output_file_name][final_output_2], folder_2)

    if line_comparison_check:
        mismatched_files, comparison_eng, comparison_esp = isolated_comparison.main()
        numbers = sorted([int(float(item)) for item in mismatched_files])
        handle_comparison(pdf_1, pdf_2, numbers, line_comparison)
        pdf_1, pdf_2 = update_pdf()

    if color_comparison_check:
        color_palette.main()
        try:
            with open(mismatched_ids_file, "r", encoding=encoding_format) as file:
                wrong_ids = file.read()
            numbers = re.findall(r'\d+\.?\d*', wrong_ids)
            numbers = [int(num) if num.isdigit() else float(num) for num in numbers]
        except (OSError, ValueError):
            numbers = []
        handle_comparison(pdf_1, pdf_2, numbers, color_comparison)

    if font_comparison_check:
        is_same, mismatched_files = fonts_comparison.main_fontique(folder_1, folder_2)
        if not is_same:
            numeric_output = fonts_comparison.convert_fonts_to_numbers(mismatched_files)
            numbers = fonts_comparison.get_mismatched_ids(numeric_output)
            handle_comparison(pdf_1, pdf_2, numbers, font_comparison)
            pdf_1, pdf_2 = update_pdf()

    if font_size_check:
        mismatches = font_sized.compare_font_details()
        font_sized.add_dict_as_page_to_pdf(
            pdf_1,
            mismatches,
            MAIN_CONFIG[output_file_name][processed_pdf_1]
        )
        font_sized.add_dict_as_page_to_pdf(
            pdf_2,
            mismatches,
            MAIN_CONFIG[output_file_name][processed_pdf_2]
        )
        numbers = [int(''.join(filter(str.isdigit, name))) for name in mismatches]
        handle_comparison(pdf_1, pdf_2, numbers, font_size)
        pdf_1, pdf_2 = update_pdf()

    for elem in MAIN_CONFIG[input_folder]:
        cleanup_files.clear_folder(elem, exclude_dirs=[result_folder_root])

    try:
        os.remove(mismatched_ids_file)
    except (OSError, ValueError):
        print("No files were found.")


tiny_tony = compare_pdfs


if __name__ == "__main__":
    compare_pdfs(
        MAIN_CONFIG[default_pdf][pdf_file_1],
        MAIN_CONFIG[default_pdf][pdf_file_2]
    )

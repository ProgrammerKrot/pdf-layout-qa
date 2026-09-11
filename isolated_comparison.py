from config import DIR_CONFIG, PROCESS_CONFIG, MP_CONFIG
from dots import process_pdf_with_dots, compare_files

import multiprocessing
import shutil
import os


def ensure_directories():
    """Create all required directories if they don't exist"""
    os.makedirs(f"{DIR_CONFIG['coords_folder']}/SFE", exist_ok=True)
    os.makedirs(f"{DIR_CONFIG['coords_folder']}/SFS", exist_ok=True)
    os.makedirs(f"{DIR_CONFIG['processed_folder']}/SFE", exist_ok=True)
    os.makedirs(f"{DIR_CONFIG['processed_folder']}/SFS", exist_ok=True)
    for folder in DIR_CONFIG['groop_folders']:
        os.makedirs(folder, exist_ok=True)


def process_and_compare(file_name, mismatched):
    """Process and compare a single PDF file pair"""
    file_sfe = os.path.join(DIR_CONFIG['sfe_folder'], file_name)
    file_sfs = os.path.join(DIR_CONFIG['sfs_folder'], file_name)

    if not os.path.exists(file_sfe) or not os.path.exists(file_sfs):
        print(f"❌ Skipping {file_name}: Missing file in one of the folders.")
        return
    print(f"🔄 Processing {file_name}...")

    # Prepare output paths
    sfe_processed = os.path.join(DIR_CONFIG['processed_folder'], "SFE", f"processed_{file_name}")
    sfs_processed = os.path.join(DIR_CONFIG['processed_folder'], "SFS", f"processed_{file_name}")
    sfe_coords = os.path.join(DIR_CONFIG['coords_folder'], "SFE", f"grouped_dot_coordinates_{file_name}.txt")
    sfs_coords = os.path.join(DIR_CONFIG['coords_folder'], "SFS", f"grouped_dot_coordinates_{file_name}.txt")

    # Copy to GROOP folders
    print(f"🔍 First processing {DIR_CONFIG['groop_folders'][0]}: {file_sfe}")
    print(f"🔍 Second processing {DIR_CONFIG['groop_folders'][1]}: {file_sfs}")
    shutil.copy(file_sfe, DIR_CONFIG['groop_folders'][0])
    shutil.copy(file_sfs, DIR_CONFIG['groop_folders'][1])

    # Process both PDFs
    for input_pdf, output_pdf, coords_file in [
        (file_sfe, sfe_processed, sfe_coords),
        (file_sfs, sfs_processed, sfs_coords)
    ]:
        process_pdf_with_dots(
            input_pdf=input_pdf,
            output_pdf=output_pdf,
            coordinates_file=coords_file,
            y_threshold=PROCESS_CONFIG['y_threshold'],
            dot_color=PROCESS_CONFIG['dot_color'],
            dot_radius=PROCESS_CONFIG['dot_radius']
        )

    # Compare coordinates
    match = compare_files(sfe_coords, sfs_coords, threshold=PROCESS_CONFIG['threshold'])

    if not match:
        mismatched[file_name] = (sfe_coords, sfs_coords)

    print(f"✅ Comparison for {file_name}: {'MATCH' if match else '❌ MISMATCH FOUND'}")


def main():
    """Main processing function with optional multiprocessing"""
    ensure_directories()

    sfe_files = set(os.listdir(DIR_CONFIG['sfe_folder']))
    sfs_files = set(os.listdir(DIR_CONFIG['sfs_folder']))
    common_files = sfe_files.intersection(sfs_files)
    pdf_files = [f for f in common_files if f.endswith(".pdf")]

    manager = multiprocessing.Manager()
    mismatched = manager.dict()

    if MP_CONFIG['enabled']:
        processes = []
        for pdf in pdf_files:
            p = multiprocessing.Process(target=process_and_compare, args=(pdf, mismatched))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()
    else:
        for pdf in pdf_files:
            process_and_compare(pdf, mismatched)

    mismatched = dict(mismatched)
    numbers = []
    coordinates_en = []
    coordinates_es = []

    if mismatched:
        print("\n❌ Mismatched Files Found:")
        for file_name, (sfe_path, sfs_path) in mismatched.items():
            print(f"  - {file_name}:")
            print(f"    SFE Coordinates: {sfe_path}")
            print(f"    SFS Coordinates: {sfs_path}")
            numbers.append(file_name.split('.')[0].split('_')[-1])
            coordinates_es.append(sfe_path)
            coordinates_en.append(sfs_path)
    else:
        print("\n✅ All files matched successfully!")

    return numbers, coordinates_en, coordinates_es

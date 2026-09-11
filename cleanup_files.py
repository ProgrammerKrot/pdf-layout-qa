import shutil
import os

def ensure_clean_folder(folder_path: str) -> None:
    """
    Ensures that the given folder exists and is empty.
    If it already exists and is not empty — deletes and recreates it.

    Args:
        folder_path (str): The path to the folder to ensure.
    """

    if os.path.exists(folder_path):
        if os.listdir(folder_path):
            shutil.rmtree(folder_path)
            os.makedirs(folder_path)
    else:
        os.makedirs(folder_path)



def clear_folder(folder_path: str, exclude_dirs: list[str] = None) -> None:
    """
    Deletes all contents of a folder, then deletes the folder itself,
    unless it's listed in exclude_dirs.

    Args:
        folder_path (str): Path to folder to delete.
        exclude_dirs (list[str], optional): Absolute paths to exclude.

    Raises:
        RuntimeError: If deletion fails.
    """

    exclude_dirs = [os.path.abspath(d) for d in (exclude_dirs or [])]

    abs_folder_path = os.path.abspath(folder_path)

    if abs_folder_path in exclude_dirs:
        return

    if not os.path.exists(folder_path):
        raise RuntimeError(f"Folder '{folder_path}' doesn't exist. Nothing to delete.")

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        abs_item_path = os.path.abspath(item_path)

        if abs_item_path in exclude_dirs:
            continue

        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            raise RuntimeError(f"Failed to delete '{item_path}'. Reason: {e}")

    try:
        os.rmdir(folder_path)
    except Exception as e:
        raise RuntimeError(f"Failed to remove folder '{folder_path}'. Reason: {e}")

import os

def load_context_from_folder(folder_path: str) -> str:
    """
    Loads and concatenates content from all .txt or .md files in the given folder.

    Args:
        folder_path (str): The path to the folder containing text documents.

    Returns:
        str: Combined content from all valid files.
    """
    if not os.path.isdir(folder_path):
        return ""

    context_parts = []

    for fname in os.listdir(folder_path):
        fpath = os.path.join(folder_path, fname)

        if os.path.isfile(fpath) and fname.endswith((".txt", ".md")):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    context_parts.append(f.read())
            except Exception as e:
                context_parts.append(f"⚠️ Error reading {fname}: {e}")

    return "\n\n".join(context_parts).strip()

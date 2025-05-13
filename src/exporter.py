import zipfile
import os

def extract_zip(zip_path):
    extract_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print(f"Extracted {zip_path} to {extract_dir}")
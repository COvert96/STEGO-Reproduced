import os
import random
import shutil
from pathlib import Path
from tqdm import tqdm


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def copy_random_subset(src_dir, dst_dir, subset_ratio=0.1, seed=42, clear_dst=False):
    random.seed(seed)
    src_dir = Path(src_dir)
    dst_dir = Path(dst_dir)

    if clear_dst and os.path.exists(dst_dir):
        shutil.rmtree(dst_dir)

    # Create output directory structure
    for root, dirs, _ in os.walk(src_dir):
        for dir_name in dirs:
            create_dir(dst_dir / Path(root).relative_to(src_dir) / dir_name)

    # Set to keep track of selected files
    selected_files = set()

    # First, select the random subset of files from the 'images' directory
    for root, _, files in os.walk(src_dir):
        if 'images' in str(root):
            if files:
                # Only consider image files
                image_files = [file for file in files if file.endswith(('.jpg', '.jpeg'))]
                num_files_to_copy = int(len(image_files) * subset_ratio)
                files_to_copy = random.sample(image_files, num_files_to_copy)

                selected_files.update(f.split('.')[0] for f in files_to_copy)

                for file in tqdm(files_to_copy, desc=f"Copying files from {root}"):
                    src_file_path = Path(root) / file
                    dst_file_path = dst_dir / Path(root).relative_to(src_dir) / file
                    shutil.copy(src_file_path, dst_file_path)

    # Now copy the corresponding annotation files
    for root, _, files in os.walk(src_dir):
        if 'annotations' in str(root):
            if files:
                annotation_files = [file for file in files if file.split('.')[0] in selected_files]

                for file in tqdm(annotation_files, desc=f"Copying annotation files from {root}"):
                    src_file_path = Path(root) / file
                    dst_file_path = dst_dir / Path(root).relative_to(src_dir) / file
                    shutil.copy(src_file_path, dst_file_path)

    # Filter and copy txt files
    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith('.txt'):
                src_txt_path = Path(root) / file
                dst_txt_path = dst_dir / Path(root).relative_to(src_dir) / file

                # Read the original txt file
                with open(src_txt_path, 'r') as f:
                    lines = f.readlines()

                # Filter the lines
                filtered_lines = [line for line in lines if line.strip() in selected_files]

                # Write the filtered lines to the new txt file
                create_dir(dst_txt_path.parent)
                with open(dst_txt_path, 'w') as f:
                    f.writelines(filtered_lines)


if __name__ == "__main__":
    src_directory = "I:\Datasets\cocostuff"
    dst_directory = "I:\Datasets\cocostuff_small"
    copy_random_subset(src_directory, dst_directory, clear_dst=True)

import os
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import brotli

def compress_file(input_file_path: Path, output: Path):

    #output_file_path = output / (input_file_path.name + '.br')
    output_file_path = output / 'carte-complete-par-bureaux-de-vote-europeennes-2024.html.br'
    
    # Read the input file content
    with input_file_path.open('rb') as input_file:
        file_content = input_file.read()
    
    # Compress the content using Brotli with the highest compression level (11)
    compressed_content = brotli.compress(file_content, quality=11)
    
    # Write the compressed content to the output file
    with output_file_path.open('wb') as output_file:
        output_file.write(compressed_content)
    
    print(f'Compressed {input_file_path} to {output_file_path}')

def compress_html_files(source_dir: str, target_dir: str) -> None:
    source_path = Path(source_dir).expanduser()
    target_path = Path(target_dir).expanduser()
    
    if not source_path.exists():
        print(f"Source directory {source_path} does not exist.")
        return
    
    if not target_path.exists():
        target_path.mkdir(parents=True, exist_ok=True)
    
    tasks = []
    print(list(source_path.glob('**/*.html')))
    with ThreadPoolExecutor(max_workers=10) as executor:
        for file in source_path.glob('**/*.html'):
            relative_path = file.relative_to(source_path)
            target_subdir = target_path / relative_path.parent
            target_subdir.mkdir(parents=True, exist_ok=True)
            tasks.append(executor.submit(compress_file, file, target_subdir))
            print(f"Compressing {file} to {target_subdir}")
        
        for future in as_completed(tasks):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")

import argparse

def main():
    parser = argparse.ArgumentParser(description='Compresser les fichiers HTML.')
    parser.add_argument('-s', '--source', type=str, default='~/workspace/carto_legislatives_2024/maps', help='Répertoire source des fichiers HTML')
    parser.add_argument('-t', '--target', type=str, default='~/workspace/carto_legislatives_2024/compressed_html', help='Répertoire cible pour les fichiers compressés')
    parser.add_argument('-f', '--file', type=str, help='Fichier HTML précis à compresser')
    args = parser.parse_args()

    if args.file:
        source_file = Path(args.source).expanduser() / args.file
        target_dir = Path(args.target).expanduser()
        target_dir.mkdir(parents=True, exist_ok=True)
        compress_file(source_file, target_dir)
    else:
        compress_html_files(args.source, args.target)

if __name__ == "__main__":
    main()
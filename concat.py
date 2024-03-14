import os
import glob
from tqdm import tqdm
import fnmatch

def concatenate_files(start_dir):
    output_file_prefix = 'fullsource'
    output_file_ext = '.txt'
    ignored_files = []
    ignored_dirs = []
    output_file_index = 1
    output_file_content = ''
    max_file_size = 75000  # 75KB in bytes

    total_files = sum(len(files) for _, _, files in os.walk(start_dir))
    processed_files = 0

    with tqdm(total=total_files, unit='file') as pbar:
        for dirpath, dirnames, filenames in os.walk(start_dir):
            # Check if .gitignore file exists in the current directory
            gitignore_path = os.path.join(dirpath, '.gitignore')
            if os.path.isfile(gitignore_path):
                with open(gitignore_path, 'r') as f:
                    patterns = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
                    dir_ignored_dirs = [os.path.normpath(os.path.join(dirpath, pattern)) for pattern in patterns if pattern.endswith('/')]
                    file_ignored_patterns = [pattern for pattern in patterns if not pattern.endswith('/')]
                    dir_ignored_files = [os.path.normpath(os.path.join(dirpath, filename)) for pattern in file_ignored_patterns for filename in filenames if fnmatch.fnmatch(filename, pattern)]
                    ignored_dirs.extend(dir_ignored_dirs)
                    ignored_files.extend(dir_ignored_files)

            # Remove directories that match gitignore patterns
            dirnames[:] = [d for d in dirnames if os.path.normpath(os.path.join(dirpath, d)) not in ignored_dirs]

            for filename in filenames:
                file_path = os.path.normpath(os.path.join(dirpath, filename))
                if file_path not in ignored_files:
                    relative_path = os.path.relpath(file_path, start_dir)
                    _, ext = os.path.splitext(filename)

                    # Only include text-based file types
                    if ext.lower() in ['.txt', '.html', '.css', '.py', '.js', '.scss', '.ts', '.json']:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                file_content = f'\n\n---START OF FILE: {relative_path}---\n\n{infile.read()}\n\n---END OF FILE: {relative_path}---\n\n'
                                file_content_size = len(file_content.encode('utf-8'))

                                if len(output_file_content) + file_content_size > max_file_size:
                                    output_file = f'{output_file_prefix}_{output_file_index}{output_file_ext}'
                                    with open(output_file, 'w', encoding='utf-8') as outfile:
                                        outfile.write(output_file_content)
                                    output_file_index += 1
                                    output_file_content = file_content
                                else:
                                    output_file_content += file_content

                            processed_files += 1
                            pbar.update(1)
                        except UnicodeDecodeError:
                            print(f'Warning: Could not decode {file_path}. Skipping file.')

        # Write the remaining content to the last output file
        if output_file_content:
            output_file = f'{output_file_prefix}_{output_file_index}{output_file_ext}'
            with open(output_file, 'w', encoding='utf-8') as outfile:
                outfile.write(output_file_content)

    print(f'All files have been concatenated into {output_file_prefix}_*.{output_file_ext}')

if __name__ == '__main__':
    start_dir = os.getcwd()  # Change this to the desired starting directory
    concatenate_files(start_dir)
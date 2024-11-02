import os
import zipfile
import pyzipper
import tarfile
from PIL import Image
from pathlib import Path
import curses

def compress_image(image_path, output_path, quality=85):
    """Compress an image and save it."""
    with Image.open(image_path) as img:
        img.save(output_path, optimize=True, quality=quality)

def convert_image(image_path, output_format):
    """Convert an image to the specified format."""
    img = Image.open(image_path)
    output_path = f"{Path(image_path).stem}.{output_format}"
    img.save(output_path, format=output_format)
    return output_path

def compress_files(input_files, output_archive, password=None):
    """Compress multiple files into an archive, supporting zip and tar formats."""
    if output_archive.endswith('.zip'):
        with pyzipper.AESZipFile(output_archive, 'w', compression=zipfile.ZIP_DEFLATED) as zipf:
            if password:
                zipf.setpassword(password.encode('utf-8'))
            for file in input_files:
                zipf.write(file, os.path.basename(file))
    elif output_archive.endswith('.tar'):
        with tarfile.open(output_archive, 'w') as tarf:
            for file in input_files:
                tarf.add(file, arcname=os.path.basename(file))
    elif output_archive.endswith('.tar.gz'):
        with tarfile.open(output_archive, 'w:gz') as tarf:
            for file in input_files:
                tarf.add(file, arcname=os.path.basename(file))
    elif output_archive.endswith('.tar.bz2'):
        with tarfile.open(output_archive, 'w:bz2') as tarf:
            for file in input_files:
                tarf.add(file, arcname=os.path.basename(file))
    elif output_archive.endswith('.tar.xz'):
        with tarfile.open(output_archive, 'w:xz') as tarf:
            for file in input_files:
                tarf.add(file, arcname=os.path.basename(file))

def extract_archive(archive_path, extract_to, password=None):
    """Extract an archive, supporting zip and tar formats."""
    if archive_path.endswith('.zip'):
        with pyzipper.AESZipFile(archive_path) as zipf:
            if password:
                zipf.setpassword(password.encode('utf-8'))
            zipf.extractall(extract_to)
    elif archive_path.endswith('.tar'):
        with tarfile.open(archive_path, 'r') as tarf:
            tarf.extractall(extract_to)
    elif archive_path.endswith('.tar.gz'):
        with tarfile.open(archive_path, 'r:gz') as tarf:
            tarf.extractall(extract_to)
    elif archive_path.endswith('.tar.bz2'):
        with tarfile.open(archive_path, 'r:bz2') as tarf:
            tarf.extractall(extract_to)
    elif archive_path.endswith('.tar.xz'):
        with tarfile.open(archive_path, 'r:xz') as tarf:
            tarf.extractall(extract_to)

def get_file_list(path):
    """Get a list of files and directories in the given path, excluding hidden files."""
    return [os.path.join(path, f) for f in os.listdir(path) if not f.startswith('.')]

def print_ascii_art(stdscr):
    """Splash ASCII load."""
    ascii_art = r"""
//  $$\      $$\ $$$$$$$\   $$$$$$\  $$$$$$$\  $$$$$$$\  $$$$$$$$\ $$$$$$$\  
//  $$ | $\  $$ |$$  __$$\ $$  __$$\ $$  __$$\ $$  __$$\ $$  _____|$$  __$$\ 
//  $$ |$$$\ $$ |$$ |  $$ |$$ /  $$ |$$ |  $$ |$$ |  $$ |$$ |      $$ |  $$ |
//  $$ $$ $$\$$ |$$$$$$$  |$$$$$$$$ |$$$$$$$  |$$$$$$$  |$$$$$\    $$$$$$$  |
//  $$$$  _$$$$ |$$  __$$< $$  __$$ |$$  ____/ $$  ____/ $$  __|   $$  __$$< 
//  $$$  / \$$$ |$$ |  $$ |$$ |  $$ |$$ |      $$ |      $$ |      $$ |  $$ |
//  $$  /   \$$ |$$ |  $$ |$$ |  $$ |$$ |      $$ |      $$$$$$$$\ $$ |  $$ |
//  \__/     \__|\__|  \__|\__|  \__|\__|      \__|      \________|\__|  \__|
//                                                                           
//                                                                           
//                                                - by florwithmriver0
    """
    stdscr.clear()
    stdscr.addstr(ascii_art)
    stdscr.refresh()
    stdscr.getch()  # Wait for user to press a key

def navigate_directory(stdscr, start_dir):
    """Navigate through directories and select files."""
    curses.curs_set(0)
    current_dir = start_dir
    stack = []  # Stack to keep track of navigation
    current_selection = 0

    while True:
        file_list = get_file_list(current_dir)
        stdscr.clear()
        stdscr.addstr(0, 0, f"Current Directory: {current_dir}", curses.A_BOLD)
        stdscr.addstr(1, 0, "Select a file or directory (Press 'Enter' to select, 'b' to go back, 'q' to quit):", curses.A_BOLD)

        for idx, item in enumerate(file_list):
            prefix = "> " if idx == current_selection else "  "
            stdscr.addstr(idx + 2, 0, prefix + os.path.basename(item))

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_selection = (current_selection - 1) % len(file_list)
        elif key == curses.KEY_DOWN:
            current_selection = (current_selection + 1) % len(file_list)
        elif key in {curses.KEY_ENTER, 10, 13}:  # Enter key
            selected_path = file_list[current_selection]
            if os.path.isdir(selected_path):
                stack.append(current_dir)  # Save current directory in stack
                current_dir = selected_path
            else:
                return selected_path
        elif key == ord('b'):  # Go back to previous directory
            if stack:
                current_dir = stack.pop()
        elif key == ord('q'):
            return None

def main(stdscr):
    stdscr.bkgd(' ', curses.color_pair(0))
    print_ascii_art(stdscr)

    home_dir = os.path.expanduser("~")  # OS Support, note that no support for some OS'es may be missing.

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Choose an action: ", curses.A_BOLD)
        stdscr.addstr(1, 0, "1. Compress Files")
        stdscr.addstr(2, 0, "2. Extract Files")
        stdscr.addstr(3, 0, "q. Quit")
        stdscr.refresh()

        key = stdscr.getch()

        if key == ord('1'):
            selected_files = []
            stdscr.addstr(5, 0, "Select files to compress:")
            stdscr.refresh()

            while True:
                file_to_compress = navigate_directory(stdscr, home_dir)
                if file_to_compress:
                    selected_files.append(file_to_compress)
                    stdscr.addstr(6 + len(selected_files), 0, f"Added: {os.path.basename(file_to_compress)}")
                else:
                    break

            if selected_files:
                output_archive = os.path.join(home_dir, "compressed_files.zip")  # Default to zip
                stdscr.addstr(7 + len(selected_files), 0, "Enter output archive name (with extension): ")
                stdscr.refresh()
                curses.echo()  # Enable echoing of typed characters
                output_archive = stdscr.getstr(8 + len(selected_files), 0).decode('utf-8')
                curses.noecho()  # Disable echoing

                compress_files(selected_files, output_archive)
                stdscr.addstr(9 + len(selected_files), 0, f"Compressed to {output_archive}. Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()

        elif key == ord('2'):
            stdscr.addstr(5, 0, "Select an archive file to extract:")
            stdscr.refresh()
            archive_file = navigate_directory(stdscr, home_dir)
            if archive_file:
                extract_to = os.path.join(home_dir, "extracted_files")
                os.makedirs(extract_to, exist_ok=True)
                extract_archive(archive_file, extract_to)
                stdscr.addstr(6, 0, f"Extracted to {extract_to}. Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()

        elif key == ord('q'):
            break

if __name__ == "__main__":
    curses.wrapper(main)


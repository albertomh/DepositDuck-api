#!/usr/bin/env python

# Call the Tika PDF parser to extract text and post text to the `/llm/SourceText` endpoint
#
# Prerequisites: docker, curl
#
# Usage:
#  python pdf_to_sourcetext.py some-file.pdf
#
# (c) 2024 Alberto Morón Hernández

import argparse
import json
import subprocess
import time
import urllib.request
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent


def check_pdf_file(file_path: Path):
    if not file_path.exists():
        print(f"Error: Path '{file_path}' does not exist.")
        return False

    if not file_path.is_file():
        print(f"Error: '{file_path}' is not a file.")
        return False

    if file_path.suffix.lower() != ".pdf":
        print(f"Error: '{file_path}' is not a PDF file.")
        return False

    return True


def check_port(url, max_attempts=10) -> bool:
    attempt = 1
    while attempt <= max_attempts:
        try:
            with urllib.request.urlopen(url) as response:
                if response.getcode() == 200:
                    return True
        except Exception:
            print(".")
            time.sleep(1)
        attempt += 1
    print(f"Failed to connect to {url} after {max_attempts} attempts.")
    return False


def run_tika(version="2.9.1.0", host_port=9998) -> None:
    """
    Apache Tika is a tool to extract text from files.
    Here we use it for its PDF capabilities.
    """
    container_name = "tika"

    subprocess.run(
        f"docker stop {container_name}", shell=True, capture_output=True, text=True
    )

    start_cmd = f"""
    docker run --rm \
      --detach \
      --name {container_name} \
      --publish {host_port}:9998 \
      --platform linux/x86_64 \
      apache/tika:{version}
    """

    result = subprocess.run(start_cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(result.stdout)
    else:
        print("Error executing command:")
        print(result.stderr)


def tika_extract_text(file_path: Path, tika_port=9998) -> str | None:
    tika_cmd = f"""
    curl \
        --upload-file {str(file_path)} \
        http://0.0.0.0:{tika_port}/tika/text \
        --header "Accept: application/json"
    """

    result = subprocess.run(tika_cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        content_key = "X-TIKA:content"
        content = json.loads(result.stdout).get(content_key)
        return content
    else:
        print("Error executing command:")
        print(result.stderr)
    return None


def write_text_to_file(text: str, path: Path):
    with open(path, "w") as file:
        file.write(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check if a file path points to a PDF file."
    )
    parser.add_argument("file_path", type=str, help="Path to the file")
    args = parser.parse_args()

    depositduck_port = 8000
    check_port(f"http://0.0.0.0:{depositduck_port}")

    infile_path = CURRENT_DIR / args.file_path
    if check_pdf_file(infile_path):
        tika_port = 9998
        run_tika(host_port=tika_port)

        check_port(f"http://0.0.0.0:{tika_port}")

        text = tika_extract_text(infile_path)

        if text:
            tmpfile_path = CURRENT_DIR / "sourcetext.tmp"
            write_text_to_file(text, tmpfile_path)

import os
import hashlib
import requests
from time import sleep
from typing import Optional
from requests.exceptions import RequestException, ConnectionError, Timeout
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

DEFAULT_RETRIES = 3
DEFAULT_BACKOFF = 5
DEFAULT_CHUNK_SIZE = 1024 * 1024  # 1 MB
DEFAULT_THREADS = 4


class DownloadError(Exception):
    """Raised when a download fails."""
    pass


def _download_part(url: str, start: int, end: int, part_path: str, retries: int, backoff: int, chunk_size: int):
    """Download a part of the file with retries and exponential backoff."""
    headers = {"Range": f"bytes={start}-{end}"}
    attempt = 0
    downloaded_size = os.path.getsize(part_path) if os.path.exists(part_path) else 0

    while attempt <= retries:
        try:
            with requests.get(url, headers=headers, stream=True, timeout=15) as response:
                if response.status_code not in (200, 206):
                    response.raise_for_status()
                
                mode = "ab" if downloaded_size else "wb"
                with open(part_path, mode) as f:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded_size += len(chunk)
            return part_path
        except (RequestException, ConnectionError, Timeout) as e:
            attempt += 1
            if attempt > retries:
                raise DownloadError(f"Failed to download part {start}-{end}: {e}") from e
            sleep_time = backoff * (2 ** (attempt - 1))
            sleep(sleep_time)


def download_file(
    url: str,
    save_path: str,
    retries: int = DEFAULT_RETRIES,
    backoff: int = DEFAULT_BACKOFF,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    threads: int = DEFAULT_THREADS,
    checksum: Optional[str] = None,
    checksum_algo: str = "md5",
    verbose: bool = True
) -> str:
    """
    Production-grade downloader with multi-threading, resuming, and optional checksum verification.

    Args:
        url (str): URL to download.
        save_path (str): Path to save file.
        retries (int): Number of retries per part.
        backoff (int): Base backoff seconds for retries.
        chunk_size (int): Chunk size for downloads.
        threads (int): Number of parallel download threads.
        checksum (str, optional): MD5 or SHA256 checksum to verify.
        checksum_algo (str): Checksum algorithm ('md5' or 'sha256').
        verbose (bool): If True, prints progress.

    Returns:
        str: Path to the downloaded file.

    Raises:
        DownloadError: If download or checksum verification fails.
    """
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    response = requests.head(url, allow_redirects=True)
    total_size = int(response.headers.get("content-length", 0))
    
    if total_size == 0:
        raise DownloadError("Cannot determine file size.")

    part_size = total_size // threads
    part_paths = [f"{save_path}.part{i}" for i in range(threads)]
    ranges = [(i * part_size, (i + 1) * part_size - 1) for i in range(threads)]
    ranges[-1] = (ranges[-1][0], total_size - 1)  # Last part may be bigger

    if verbose:
        print(f"Downloading {total_size / 1024 / 1024:.2f} MB in {threads} threads...")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(_download_part, url, start, end, part_paths[i], retries, backoff, chunk_size): i
            for i, (start, end) in enumerate(ranges)
        }

        for future in tqdm(as_completed(futures), total=len(futures), desc="Parts"):
            future.result()  # Will raise exception if failed

    # Combine parts
    with open(save_path, "wb") as final_file:
        for part_path in part_paths:
            with open(part_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    final_file.write(chunk)
            os.remove(part_path)

    # Checksum verification
    if checksum:
        hash_func = hashlib.md5() if checksum_algo.lower() == "md5" else hashlib.sha256()
        with open(save_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hash_func.update(chunk)
        if hash_func.hexdigest().lower() != checksum.lower():
            raise DownloadError("Checksum verification failed.")

    if verbose:
        print(f"Download complete: {save_path}")
    return save_path


# Example usage
if __name__ == "__main__":
    url = "https://testfileorg.netwet.net/500MB-CZIPtestfile.org.zip"
    save_path = "500mb.zip"
    download_file(url, save_path, threads=4)

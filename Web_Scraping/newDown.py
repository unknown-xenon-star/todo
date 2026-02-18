import requests
import tqdm


URL = str(input("Enter URL: "))
if not URL.casefold().startswith(("http://", "https://")):
    # URL https,htttp hi honi chahiye
    # baki url support v2 me
    raise ValueError("URL must start with http:// or https://")

r = requests.get(URL, stream=True)
# if r.status_code != requests.codes.ok:
#     # Agar response ka status code 200 (OK) nahi hai, to error raise karo
#     raise Exception("Request failed with status code: {}".format(r.status_code))
r.raise_for_status()

from urllib.parse import urlparse

def get_filename(url):
    # filename extractor
    return urlparse(url).path.split("/")[-1] or "downloaded_file.txt"

def download_file(filename):
    if not filename:
        try:
            # upgrade kar filename logic ko
            filename = get_filename(URL)
        except:
            input("GIVE FILE NAME: ")

    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=128):
            if chunk:
                f.write(chunk)

download_file()

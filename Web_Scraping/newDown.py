import requests
import tqdm


URL = str(input("Enter URL: "))
if not URL.casefold().startswith(("http://", "https://")):
    # URL https,htttp hi honi chahiye
    # baki url support v2 me
    raise ValueError("URL must start with http:// or https://")

r = requests.get(URL)
if not r.status_code != requests.codes.ok:
    # Agar response ka status code 200 (OK) nahi hai, to error raise karo
    raise Exception("Request failed with status code: {}".format(r.status_code))


def download_file(filename):
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)
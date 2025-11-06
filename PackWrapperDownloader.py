from pathlib import Path
import hashlib
import zipfile
import shutil
import ssl

import httpx


file_path = Path(".packwrapper/cache/PackWrapper.zip")
file_path.parent.mkdir(parents = True, exist_ok = True)

def main(version: str = "nightly", verify: ssl.SSLContext | str | bool= True):
    
    global file_path
        
    def get(version: str):
        try:
            response = httpx.get(f"https://api.github.com/repos/7777777-4547/PackWrapper/releases/tags/{version}", verify = verify)
            response.raise_for_status()
            project_info = response.json()
            url = project_info.get("assets",[{}])[0].get("browser_download_url",None)
            digest = project_info.get("assets",[{}])[0].get("digest",None).replace("sha256:","")
            if url is not None:
                return (url, digest)
            else:
                raise Exception("Failed to get PackWrapper download URL")
        except Exception as e:
            raise e

    def download(url, path):
        with httpx.Client(follow_redirects = True, verify = verify) as client:
            with client.stream("GET", url) as response:
                
                try:
                    response.raise_for_status()
                    with open(path, 'wb') as f:
                        for chunk in response.iter_bytes():
                            f.write(chunk)
                    return path
                
                except Exception:
                    raise Exception(f"Failed to download {url}")
                
    def extract(zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall()
        except FileNotFoundError:
            raise FileNotFoundError(f"{zip_path}")
        except zipfile.BadZipFile:
            raise ValueError(f"{zip_path}")
        except Exception as e:
            raise Exception(f"{e}: {zip_path}")
        
    def calculate(file) -> str | None:
        try:
            hash_obj = hashlib.new("sha256")
            with open(file, 'rb') as file:
                for chunk in iter(lambda: file.read(4096), b''):
                    hash_obj.update(chunk)

            return hash_obj.hexdigest()
        except Exception as e:
            raise e


    file_info = get(version)
    file_url = file_info[0]
    file_digest = file_info[1]
    print(f"[Downloader] Downloading PackWrapper from \"{file_url}\"")

    if Path(file_path).exists():
        if calculate(file_path) != file_digest:
            Path(file_path).unlink()
            download(file_url, file_path)
    else:
        download(file_url, file_path)

    if Path("PackWrapper").exists():
        shutil.rmtree("PackWrapper")
            
    extract(file_path)
                
    print("[Downloader] PackWrapper download has finished.")

def clear():
    global file_path
    Path(file_path).unlink

__all__ = [
    "main",
    "clear"
]


if __name__ == "__main__":
    main(verify = False)
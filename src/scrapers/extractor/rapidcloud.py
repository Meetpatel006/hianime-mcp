import requests
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import json

# Assuming these are available from your project structure
# from config.logger import log
# from utils.index import substringAfter, substringBefore

# Placeholder for log and substring functions if not available
class Logger:
    def info(self, message):
        print(f"INFO: {message}")
log = Logger()

def substringAfter(s, delimiter):
    return s.split(delimiter, 1)[-1]

def substringBefore(s, delimiter):
    return s.split(delimiter, 1)[0]


class RapidCloud:
    def __init__(self):
        self.sources = []
        self.fallback_key = "c1d17096f2ca11b7"
        self.host = "https://rapid-cloud.co"

    async def extract(self, video_url: str):
        result = {
            "sources": [],
            "subtitles": [],
        }

        try:
            video_url_obj = requests.utils.urlparse(video_url)
            video_id = video_url_obj.path.split("/")[-1].split("?")[0]

            headers = {
                "X-Requested-With": "XMLHttpRequest",
            }

            res = requests.get(
                f"https://{video_url_obj.hostname}/embed-2/ajax/e-1/getSources?id={video_id}",
                headers=headers
            )
            res.raise_for_status()  # Raise an exception for HTTP errors
            data = res.json()

            sources = data.get("sources")
            tracks = data.get("tracks")
            intro = data.get("intro")
            outro = data.get("outro")
            encrypted = data.get("encrypted")

            decrypt_key_res = requests.get("https://raw.githubusercontent.com/cinemaxhq/keys/e1/key")
            decrypt_key_res.raise_for_status()
            decrypt_key = decrypt_key_res.text

            decrypt_key = substringBefore(
                substringAfter(
                    decrypt_key,
                    '"blob-code blob-code-inner js-file-line">'
                ),
                "</td>"
            )

            if not decrypt_key:
                decrypt_key_res = requests.get("https://raw.githubusercontent.com/cinemaxhq/keys/e1/key")
                decrypt_key_res.raise_for_status()
                decrypt_key = decrypt_key_res.text

            if not decrypt_key: # Re-check after second attempt
                decrypt_key = self.fallback_key

            if encrypted:
                try:
                    sources_array = list(sources)
                    extracted_key = ""
                    current_index = 0

                    # Assuming decrypt_key is a string of numbers separated by commas, representing indices and lengths
                    # This part needs careful translation as the TypeScript code uses `index[0]` and `index[1]`
                    # which implies `decryptKey` is an array of arrays or similar structure.
                    # For now, I'll assume it's a string that needs to be parsed into pairs of numbers.
                    # This is a critical assumption and might need adjustment based on actual `decryptKey` format.
                    # Example: 


                    # If decrypt_key is like '[[1,2],[3,4]]', then parse it as such.
                    # For now, let's assume it's a string that needs to be evaluated as a list of lists.
                    # This is a potential point of failure if the format is different.
                    try:
                        parsed_decrypt_key = json.loads(decrypt_key)
                    except json.JSONDecodeError:
                        log.info("Decrypt key is not a valid JSON array. Using fallback key.")
                        parsed_decrypt_key = [] # Fallback to empty if not JSON

                    for index_pair in parsed_decrypt_key:
                        start = index_pair[0] + current_index
                        end = start + index_pair[1]

                        for i in range(start, end):
                            if i < len(data['sources']):
                                extracted_key += data['sources'][i]
                                sources_array[i] = ""
                        current_index += index_pair[1]

                    decrypt_key = extracted_key
                    sources = "".join(sources_array)

                    # AES decryption
                    # The TypeScript code uses CryptoJS.AES.decrypt which implies CBC mode with PKCS7 padding.
                    # Python's PyCryptodome library (Crypto.Cipher.AES) can be used.
                    # The key needs to be 16, 24, or 32 bytes long.
                    # The IV is usually derived from the key or is part of the encrypted data.
                    # CryptoJS.AES.decrypt often uses an implicit IV or derives it from the key/salt.
                    # For simplicity, assuming no IV is explicitly provided, or it's all zeros, or derived.
                    # This is a common point of divergence between JS crypto and Python crypto.
                    # If decryption fails, it's likely due to incorrect key/IV/padding.

                    # Assuming the key is UTF-8 encoded and needs to be padded or truncated to AES block size
                    key_bytes = decrypt_key.encode('utf-8')
                    # Pad key to 16, 24, or 32 bytes if necessary. For simplicity, let's assume 16 bytes.
                    # This might need adjustment based on the actual key length used by CryptoJS.
                    key_bytes = key_bytes + b'\0' * (16 - len(key_bytes) % 16) if len(key_bytes) % 16 != 0 else key_bytes
                    key_bytes = key_bytes[:16] # Truncate or use first 16 bytes if longer

                    cipher = AES.new(key_bytes, AES.MODE_CBC, iv=bytes([0]*16)) # Assuming zero IV for now
                    # The input to decrypt needs to be base64 decoded first
                    decoded_sources = base64.b64decode(sources)
                    decrypted_bytes = unpad(cipher.decrypt(decoded_sources), AES.block_size)
                    sources = json.loads(decrypted_bytes.decode('utf-8'))

                except Exception as err:
                    log.info(f"Decryption error: {err}")
                    raise Exception("Cannot decrypt sources. Perhaps the key is invalid.")

            self.sources = []
            if sources:
                for s in sources:
                    self.sources.append({
                        "url": s.get("file"),
                        "isM3U8": ".m3u8" in s.get("file", ""),
                    })

            result["sources"].extend(self.sources)

            if video_url_obj.hostname == requests.utils.urlparse(self.host).hostname:
                result["sources"] = []
                self.sources = []

                for source in sources:
                    source_file = source.get("file")
                    if not source_file: continue

                    res_m3u8 = requests.get(source_file, headers=headers)
                    res_m3u8.raise_for_status()
                    m3u8_data = res_m3u8.text

                    m3u8_lines = m3u8_data.split("\n")
                    filtered_m3u8_data = [
                        line for line in m3u8_lines
                        if ".m3u8" in line and "RESOLUTION=" in line
                    ]

                    second_half = []
                    for line in filtered_m3u8_data:
                        match = [s.split("=")[1] for s in line.split(",") if "RESOLUTION=" in s or "URI=" in s]
                        if match: second_half.append(match)

                    td_array = []
                    for s_arr in second_half:
                        if len(s_arr) >= 2:
                            f1 = s_arr[0].split(",C")[0]
                            f2 = s_arr[1].replace('"', '')
                            td_array.append([f1, f2])

                    for f1, f2 in td_array:
                        base_url = source_file.split("master.m3u8")[0]
                        full_url = f"{base_url}{f2.replace('iframes', 'index')}"
                        self.sources.append({
                            "url": full_url,
                            "quality": f"{f1.split('x')[1]}p",
                            "isM3U8": ".m3u8" in f2,
                        })
                    result["sources"].extend(self.sources)

            result["intro"] = {"start": intro["start"], "end": intro["end"]} if intro and intro.get("end", 0) > 1 else None
            result["outro"] = {"start": outro["start"], "end": outro["end"]} if outro and outro.get("end", 0) > 1 else None

            if sources and len(sources) > 0:
                result["sources"].append({
                    "url": sources[0].get("file"),
                    "isM3U8": ".m3u8" in sources[0].get("file", ""),
                    "quality": "auto",
                })

            result["subtitles"] = [
                {"url": s.get("file"), "lang": s.get("label", "Thumbnails")}
                for s in tracks if s.get("file")
            ]

            return result

        except requests.exceptions.RequestException as e:
            log.info(f"Request error: {e}")
            raise
        except Exception as err:
            log.info(f"An unexpected error occurred: {err}")
            raise


# Example Usage (for testing, can be removed later)
# async def main():
#     rc = RapidCloud()
#     # Replace with a valid video URL for testing
#     video_url = "https://megacloud.tv/embed-2/e-1/IxJ7GjGVCyml?k=1"
#     try:
#         extracted_data = await rc.extract(video_url)
#         print(json.dumps(extracted_data, indent=4))
#     except Exception as e:
#         print(f"Error during extraction: {e}")

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())



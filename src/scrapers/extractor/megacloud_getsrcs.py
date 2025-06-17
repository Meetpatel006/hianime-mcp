# import requests
# import re
# import base64
# import json
# from Crypto.Cipher import AES
# from Crypto.Util.Padding import unpad

# # Assuming these are available from your project structure or defined elsewhere
# # from config.logger import log
# # from utils.constants import SRC_BASE_URL, USER_AGENT_HEADER

# # Placeholder for log, SRC_BASE_URL, USER_AGENT_HEADER if not available
# class Logger:
#     def info(self, message):
#         print(f"INFO: {message}")
# log = Logger()

# SRC_BASE_URL = "https://megacloud.tv/"
# USER_AGENT_HEADER = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"

# from megacloud_decodedpng import decoded_png

# embed_url = "https://megacloud.tv/embed-2/e-1/"
# referrer = SRC_BASE_URL
# user_agent = USER_AGENT_HEADER

# def _evp_bytes_to_key(password, salt, key_len, iv_len):
#     password = password.encode("utf-8") if isinstance(password, str) else password
#     salt = salt if isinstance(salt, bytes) else salt.encode("utf-8")

#     key_iv = b''
#     prev = b''
#     while len(key_iv) < key_len + iv_len:
#         prev = hashlib.md5(prev + password + salt).digest()
#         key_iv += prev

#     key = key_iv[:key_len]
#     iv = key_iv[key_len:key_len + iv_len]
#     return key, iv

# def decrypt_data(encrypted_data: str, key: str, iv: str = None):
#     if iv:
#         key_bytes = key.encode("utf-8")
#         iv_bytes = iv.encode("utf-8")
#         contents = base64.b64decode(encrypted_data)
#     else:
#         cypher = base64.b64decode(encrypted_data)
#         salt = cypher[8:16]
#         key_bytes, iv_bytes = _evp_bytes_to_key(key, salt, 32, 16) # 32 bytes for AES-256 key, 16 for IV
#         contents = cypher[16:]

#     cipher = AES.new(key_bytes, AES.MODE_CBC, iv=iv_bytes)
#     decrypted_bytes = cipher.decrypt(contents)
#     return unpad(decrypted_bytes, AES.block_size).decode("utf-8")


# async def getSources(video_id: str):
#     try:
#         headers = {
#             "Accept": "*/*",
#             "X-Requested-With": "XMLHttpRequest",
#             "User-Agent": user_agent,
#             "Referer": referrer,
#         }

#         # First request to get the sources data
#         sources_url = f"https://megacloud.tv/embed-2/ajax/e-1/getSources?id={video_id}"
#         res = requests.get(sources_url, headers=headers)
#         res.raise_for_status()
#         srcs_data = res.json()

#         if not srcs_data:
#             log.info("No sources data found.")
#             return None

#         if not srcs_data.get("encrypted") and isinstance(srcs_data.get("sources"), list):
#             return srcs_data

#         # If encrypted, fetch the script to decrypt
#         script_url = f"https://megacloud.tv/js/player/a/prod/e1-player.min.js?v={requests.utils.time.time() * 1000}"
#         script_res = requests.get(script_url)
#         script_res.raise_for_status()
#         script_text = script_res.text

#         if not script_text:
#             log.info("Couldn't fetch script to decrypt resource.")
#             return None

#         # Extract variables for decryption
#         vars_list = []
#         regex = re.compile(r"case\s*0x[0-9a-f]+:(?![^;]*=partKey)\s*\w+\s*=\s*(\w+)\s*,\s*\w+\s*=\s*(\w+);")
#         for match in regex.finditer(script_text):
#             try:
#                 match_key1 = re.search(r",{}=((?:0x)?([0-9a-fA-F]+))".format(re.escape(match.group(1))), script_text).group(1).replace("0x", "")
#                 match_key2 = re.search(r",{}=((?:0x)?([0-9a-fA-F]+))".format(re.escape(match.group(2))), script_text).group(1).replace("0x", "")
#                 vars_list.append([int(match_key1, 16), int(match_key2, 16)])
#             except AttributeError:
#                 log.info("Failed to match key in script.")
#                 continue

#         if not vars_list:
#             log.info("Can't find variables. Perhaps the extractor is outdated.")
#             return None

#         encrypted_string = srcs_data["sources"]
#         secret = ""
#         encrypted_source_array = list(encrypted_string)
#         current_index = 0

#         for index_pair in vars_list:
#             start = index_pair[0] + current_index
#             end = start + index_pair[1]

#             for i in range(start, end):
#                 if i < len(encrypted_string):
#                     secret += encrypted_string[i]
#                     encrypted_source_array[i] = ""
#             current_index += index_pair[1]

#         encrypted_source = "".join(encrypted_source_array)

#         decrypted = decrypt_data(encrypted_source, secret)
#         sources = json.loads(decrypted)

#         srcs_data["sources"] = sources
#         return srcs_data

#     except requests.exceptions.RequestException as e:
#         log.info(f"Network error: {e}")
#         return None
#     except Exception as e:
#         log.info(f"An error occurred during source extraction: {e}")
#         return None

# # Example Usage (for testing, can be removed later)
# async def main():
#     # Replace with a valid video ID for testing
#     video_id = "dBqCr5BcOhnD"
#     try:
#         extracted_data = await getSources(video_id)
#         if extracted_data:
#             print(json.dumps(extracted_data, indent=4))
#         else:
#             print("Failed to extract sources.")
#     except Exception as e:
#         print(f"Error: {e}")

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(main())


import requests
import re
import base64
import json
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from src.utils.constants import SRC_BASE_URL,USER_AGENT_HEADER


# Assuming these are available from your project structure or defined elsewhere
# from config.logger import log
# from utils.constants import SRC_BASE_URL, USER_AGENT_HEADER

# Placeholder for log, SRC_BASE_URL, USER_AGENT_HEADER if not available
class Logger:
    def info(self, message):
        print(f"INFO: {message}")
log = Logger()

embed_url = "https://megacloud.tv/embed-2/e-1/"
referrer = SRC_BASE_URL
user_agent = USER_AGENT_HEADER

def _evp_bytes_to_key(password, salt, key_len, iv_len):
    password = password.encode("utf-8") if isinstance(password, str) else password
    salt = salt if isinstance(salt, bytes) else salt.encode("utf-8")

    key_iv = b''
    prev = b''
    while len(key_iv) < key_len + iv_len:
        prev = hashlib.md5(prev + password + salt).digest()
        key_iv += prev

    key = key_iv[:key_len]
    iv = key_iv[key_len:key_len + iv_len]
    return key, iv

def decrypt_data(encrypted_data: str, key: str, iv: str = None):
    if iv:
        key_bytes = key.encode("utf-8")
        iv_bytes = iv.encode("utf-8")
        contents = base64.b64decode(encrypted_data)
    else:
        cypher = base64.b64decode(encrypted_data)
        salt = cypher[8:16]
        key_bytes, iv_bytes = _evp_bytes_to_key(key, salt, 32, 16) # 32 bytes for AES-256 key, 16 for IV
        contents = cypher[16:]

    cipher = AES.new(key_bytes, AES.MODE_CBC, iv=iv_bytes)
    decrypted_bytes = cipher.decrypt(contents)
    return unpad(decrypted_bytes, AES.block_size).decode("utf-8")


async def getSources(video_id: str):
    try:
        headers = {
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": user_agent,
            "Referer": referrer,
        }

        # First request to get the sources data
        sources_url = f"https://megacloud.tv/embed-2/ajax/e-1/getSources?id={video_id}"
        res = requests.get(sources_url, headers=headers)
        res.raise_for_status()
        srcs_data = res.json()

        if not srcs_data:
            log.info("No sources data found.")
            return None

        if not srcs_data.get("encrypted") and isinstance(srcs_data.get("sources"), list):
            return srcs_data

        # If encrypted, fetch the script to decrypt
        script_url = f"https://megacloud.tv/js/player/a/prod/e1-player.min.js?v={requests.utils.time.time() * 1000}"
        script_res = requests.get(script_url)
        script_res.raise_for_status()
        script_text = script_res.text

        if not script_text:
            log.info("Couldn't fetch script to decrypt resource.")
            return None

        # Extract variables for decryption
        vars_list = []
        regex = re.compile(r"case\s*0x[0-9a-f]+:(?![^;]*=partKey)\s*\w+\s*=\s*(\w+)\s*,\s*\w+\s*=\s*(\w+);")
        for match in regex.finditer(script_text):
            try:
                match_key1 = re.search(r",{}=((?:0x)?([0-9a-fA-F]+))".format(re.escape(match.group(1))), script_text).group(1).replace("0x", "")
                match_key2 = re.search(r",{}=((?:0x)?([0-9a-fA-F]+))".format(re.escape(match.group(2))), script_text).group(1).replace("0x", "")
                vars_list.append([int(match_key1, 16), int(match_key2, 16)])
            except AttributeError:
                log.info("Failed to match key in script.")
                continue

        if not vars_list:
            log.info("Can't find variables. Perhaps the extractor is outdated.")
            return None

        encrypted_string = srcs_data["sources"]
        secret = ""
        encrypted_source_array = list(encrypted_string)
        current_index = 0

        for index_pair in vars_list:
            start = index_pair[0] + current_index
            end = start + index_pair[1]

            for i in range(start, end):
                if i < len(encrypted_string):
                    secret += encrypted_string[i]
                    encrypted_source_array[i] = ""
            current_index += index_pair[1]

        encrypted_source = "".join(encrypted_source_array)

        decrypted = decrypt_data(encrypted_source, secret)
        sources = json.loads(decrypted)

        srcs_data["sources"] = sources
        return srcs_data

    except requests.exceptions.RequestException as e:
        log.info(f"Network error: {e}")
        return None
    except Exception as e:
        log.info(f"An error occurred during source extraction: {e}")
        return None

# Example Usage (for testing, can be removed later)
async def main():
    # Replace with a valid video ID for testing
    video_id = "dBqCr5BcOhnD"
    try:
        extracted_data = await getSources(video_id)
        if extracted_data:
            print(json.dumps(extracted_data, indent=4))
        else:
            print("Failed to extract sources.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())



import requests
import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import json
import re

class HiAnimeError(Exception):
    def __init__(self, message, context, status_code):
        super().__init__(message)
        self.context = context
        self.status_code = status_code


megacloud_config = {
    "script": "https://megacloud.tv/js/player/a/prod/e1-player.min.js?v=",
    "sources": "https://megacloud.tv/embed-2/ajax/e-1/getSources?id=",
}

class MegaCloud:

    def _evp_bytes_to_key(self, password, salt, key_len, iv_len):
        # Equivalent to OpenSSL's EVP_BytesToKey
        # https://stackoverflow.com/questions/50979241/python-equivalent-of-openssl-evp-bytes-to-key
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

    def decrypt(self, encrypted: str, key_or_secret: str, maybe_iv: str = None):
        try:
            if maybe_iv:
                key = key_or_secret.encode("utf-8")
                iv = maybe_iv.encode("utf-8")
                contents = base64.b64decode(encrypted)
            else:
                cypher = base64.b64decode(encrypted)
                salt = cypher[8:16]
                key, iv = self._evp_bytes_to_key(key_or_secret, salt, 32, 16) # 32 bytes for AES-256 key, 16 for IV
                contents = cypher[16:]
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            decrypted_bytes = cipher.decrypt(contents)
            return unpad(decrypted_bytes, AES.block_size).decode("utf-8")
        except Exception as e:
            if "Padding is incorrect" in str(e):
                raise Exception("Decryption failed due to incorrect padding. The encryption key may have changed or the data is corrupted.")
            else:
                raise Exception(f"Decryption failed: {str(e)}")

    def matchingKey(self, value: str, script: str):
        regex = re.compile(r",{}=((?:0x)?([0-9a-fA-F]+))".format(re.escape(value)))
        match = regex.search(script)
        if match:
            return match.group(1).replace("0x", "")
        else:
            raise Exception("Failed to match the key")

    async def extract3(self, embed_iframe_url: str):
        try:
            # Fetch the key from GitHub
            response = requests.get("https://raw.githubusercontent.com/itzzzme/megacloud-keys/refs/heads/main/key.txt")
            response.raise_for_status()
            key = response.text.strip()

            extracted_data = {
                "tracks": [],
                "intro": {"start": 0, "end": 0},
                "outro": {"start": 0, "end": 0},
                "sources": [],
            }

            # Extract sourceId from embed URL
            match = re.search(r"/([^/?]+)(?:\?|$)", embed_iframe_url)
            source_id = match.group(1) if match else None

            if not source_id:
                raise Exception("Unable to extract sourceId from embed URL")

            megacloud_url = f"https://megacloud.blog/embed-2/v2/e-1/getSources?id={source_id}"
            raw_source_data_res = requests.get(megacloud_url)
            raw_source_data_res.raise_for_status()
            raw_source_data = raw_source_data_res.json()

            encrypted = raw_source_data.get("sources")
            if not encrypted:
                raise Exception("Encrypted source missing in response")

            decrypted = self.decrypt(encrypted, key)

            try:
                decrypted_sources = json.loads(decrypted)
            except json.JSONDecodeError:
                raise Exception("Decrypted data is not valid JSON")

            extracted_data["intro"] = raw_source_data.get("intro", extracted_data["intro"])
            extracted_data["outro"] = raw_source_data.get("outro", extracted_data["outro"])

            extracted_data["tracks"] = [
                {"url": track["file"], "lang": track.get("label", track.get("kind"))}
                for track in raw_source_data.get("tracks", [])
            ]

            extracted_data["sources"] = [
                {"url": s["file"], "isM3U8": s["type"] == "hls", "type": s["type"]}
                for s in decrypted_sources
            ]

            return extracted_data

        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error during extract3: {e}")
        except Exception as err:
            raise err
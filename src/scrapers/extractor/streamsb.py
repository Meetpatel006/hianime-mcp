import requests
import urllib.parse

from src.utils.constants import USER_AGENT_HEADER


class StreamSB:
    def __init__(self):
        self.sources = []
        self.host = "https://watchsb.com/sources50"
        self.host2 = "https://streamsss.net/sources16"

    def PAYLOAD(self, hex_str: str) -> str:
        # The TypeScript payload string is quite long and specific.
        # Directly translating it to Python.
        return f"566d337678566f743674494a7c7c{hex_str}7c7c346b6767586d6934774855537c7c73747265616d7362/6565417268755339773461447c7c346133383438333436313335376136323337373433383634376337633465366534393338373136643732373736343735373237613763376334363733353737303533366236333463353333363534366137633763373337343732363536313664373336327c7c6b586c3163614468645a47617c7c73747265616d7362"

    def extract(self, video_url: str, is_alt: bool = False) -> list:
        headers = {
            "watchsb": "sbstream",
            "Referer": video_url,
            "User-Agent": USER_AGENT_HEADER,
        }

        parsed_url = urllib.parse.urlparse(video_url)
        path_segments = parsed_url.path.split("/")
        video_id = path_segments[-1]

        if ".html" in video_id:
            video_id = video_id.split(".html")[0]

        # Convert ID to hex string as done in TypeScript
        hex_id = video_id.encode("utf-8").hex()

        try:
            target_host = self.host2 if is_alt else self.host
            res = requests.get(f"{target_host}/{self.PAYLOAD(hex_id)}", headers=headers)
            res.raise_for_status()  # Raise an exception for HTTP errors
            data = res.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"No source found. Try a different server. Error: {e}")

        stream_data = data.get("stream_data")
        if not stream_data:
            raise Exception("No source found. Try a different server")

        headers = {
            "User-Agent": USER_AGENT_HEADER,
            "Referer": video_url.split("e/")[0], # This might need adjustment based on actual URL structure
        }

        try:
            m3u8_urls_res = requests.get(stream_data["file"], headers=headers)
            m3u8_urls_res.raise_for_status()
            video_list = m3u8_urls_res.text.split("#EXT-X-STREAM-INF:")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to retrieve M3U8 playlist. Error: {e}")

        self.sources = []
        for video_info in video_list:
            if "m3u8" not in video_info: # Skip if not an m3u8 entry
                continue

            lines = video_info.split("\n")
            if len(lines) < 2: # Ensure there are enough lines for URL and quality
                continue

            url = lines[1].strip()
            quality = "auto"

            # Extract quality from RESOLUTION if available
            resolution_match = [part for part in lines[0].split(",") if "RESOLUTION=" in part]
            if resolution_match:
                try:
                    quality = resolution_match[0].split("=")[1].split("x")[1] + "p"
                except IndexError:
                    pass # Keep quality as 'auto' if parsing fails

            self.sources.append({
                "url": url,
                "quality": quality,
                "isM3U8": True,
            })

        # Add the main stream_data file as an 'auto' quality source
        self.sources.append({
            "url": stream_data["file"],
            "quality": "auto",
            "isM3U8": ".m3u8" in stream_data["file"],
        })

        return self.sources

# Example Usage (for testing, can be removed later)
# if __name__ == "__main__":
#     sb = StreamSB()
#     # Replace with a valid StreamSB video URL for testing
#     video_url = "https://streamsb.net/e/your_video_id.html"
#     try:
#         extracted_data = sb.extract(video_url)
#         import json
#         print(json.dumps(extracted_data, indent=4))
#     except Exception as e:
#         print(f"Error: {e}")



import requests
from bs4 import BeautifulSoup

class StreamTape:
    def __init__(self):
        self.sources = []

    def extract(self, video_url: str):
        try:
            response = requests.get(video_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the script tag containing the robotlink assignment
            script_tag = soup.find('script', string=lambda text: text and 'robotlink' in text)

            if not script_tag:
                raise Exception("Could not find robotlink script.")

            # Extract the relevant part of the script content
            match = script_tag.string.split("robotlink').innerHTML = (")[1].split(");")[0]

            # Split into fh and sh
            fh, sh = match.split(" + ('")

            # Clean up sh and fh
            sh = sh[3:]
            fh = fh.replace("\\\'", "")

            url = f"https:{fh}{sh}"

            self.sources.append({
                "url": url,
                "isM3U8": ".m3u8" in url,
            })

            return self.sources
        except requests.exceptions.RequestException as e:
            raise Exception(f"Video not found or network error: {e}")
        except Exception as err:
            raise Exception(f"Error during extraction: {err}")

# Example Usage (for testing, can be removed later)
# if __name__ == "__main__":
#     st = StreamTape()
#     # Replace with a valid StreamTape video URL for testing
#     video_url = "https://streamtape.com/e/your_video_id"
#     try:
#         extracted_data = st.extract(video_url)
#         print(extracted_data)
#     except Exception as e:
#         print(f"Error: {e}")



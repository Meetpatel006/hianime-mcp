import requests
from .constants import ACCEPT_HEADER, USER_AGENT_HEADER, ACCEPT_ENCODING_HEADER

class Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": ACCEPT_HEADER,
            "User-Agent": USER_AGENT_HEADER,
            "Accept-Encoding": ACCEPT_ENCODING_HEADER
        })
        self.timeout = 8000  # 8 seconds

    def get(self, url: str, **kwargs):
        """Make a GET request with default headers and timeout."""
        kwargs.setdefault("timeout", self.timeout)
        return self.session.get(url, **kwargs)

    def post(self, url: str, **kwargs):
        """Make a POST request with default headers and timeout."""
        kwargs.setdefault("timeout", self.timeout)
        return self.session.post(url, **kwargs)

# Create a singleton client instance
client = Client() 
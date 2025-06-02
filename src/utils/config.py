"""Configuration management for the anime scraper."""

class Config:
    # Scraping settings
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    # Browser emulation
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.234"
    MOBILE = False
    
    # Rate limiting
    RATE_LIMIT = 1  # requests per second
    
    # Debug settings
    DEBUG_MODE = True
    SAVE_HTML = True
    
    # File paths
    LOG_DIR = "logs"
    DEBUG_DIR = "debug"
    
    @classmethod
    def get_headers(cls):
        """Get default headers for requests."""
        return {
            "User-Agent": cls.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

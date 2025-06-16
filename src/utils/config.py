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

    # Logging settings
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 3  # Number of backup files to keep
    LOG_RETENTION_DAYS = 5  # Days to keep old log files
    
    @classmethod
    def get_headers(cls):
        """Get default headers for requests."""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Ch-Ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive',
            'DNT': '1'  # Do Not Track
        }

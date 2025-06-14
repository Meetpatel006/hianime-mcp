import logging
import os
import glob
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler

# Import config, but handle case where it's not available
try:
    from src.utils.config import Config
except ImportError:
    # Fallback config if import fails
    class Config:
        LOG_DIR = "logs"
        LOG_LEVEL = "INFO"
        LOG_MAX_FILE_SIZE = 10 * 1024 * 1024
        LOG_BACKUP_COUNT = 3
        LOG_RETENTION_DAYS = 5

class LogManager:
    _shared_handlers = {}
    _initialized = False
    _log_filename = None

    @classmethod
    def _initialize_shared_handlers(cls):
        """Initialize shared file and console handlers once."""
        if cls._initialized:
            return

        # Create logs directory if it doesn't exist
        os.makedirs(Config.LOG_DIR, exist_ok=True)

        # Clean up old log files
        cls._cleanup_old_logs()

        # Use a fixed log file name for the current day to avoid multiple files per session
        date_str = datetime.now().strftime("%Y%m%d")
        cls._log_filename = f"{Config.LOG_DIR}/anime_scraper_{date_str}.log"

        # Use RotatingFileHandler to prevent single files from getting too large
        file_handler = RotatingFileHandler(
            cls._log_filename,
            maxBytes=Config.LOG_MAX_FILE_SIZE,
            backupCount=Config.LOG_BACKUP_COUNT,
            encoding='utf-8'  # Ensure UTF-8 encoding for file handler
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler with UTF-8 encoding
        import sys
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))

        # Formatting
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Store shared handlers
        cls._shared_handlers['file'] = file_handler
        cls._shared_handlers['console'] = console_handler
        cls._initialized = True

    @classmethod
    def _cleanup_old_logs(cls):
        """Remove log files older than configured retention days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=Config.LOG_RETENTION_DAYS)
            log_pattern = f"{Config.LOG_DIR}/anime_scraper_*.log*"  # Include rotated files
            old_pattern = f"{Config.LOG_DIR}/scraper_*.log"  # Old naming pattern

            for pattern in [log_pattern, old_pattern]:
                for log_file in glob.glob(pattern):
                    try:
                        file_time = datetime.fromtimestamp(os.path.getctime(log_file))
                        if file_time < cutoff_date:
                            os.remove(log_file)
                            print(f"Removed old log file: {log_file}")
                    except (OSError, ValueError):
                        # Skip files we can't process
                        continue
        except Exception as e:
            print(f"Warning: Could not clean up old logs: {e}")

    def __init__(self, name="AnimeScraperLog"):
        # Initialize shared handlers if not done already
        self._initialize_shared_handlers()

        # Get or create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Only add handlers if they haven't been added already
        if not self.logger.handlers:
            self.logger.addHandler(self._shared_handlers['file'])
            self.logger.addHandler(self._shared_handlers['console'])

        # Prevent propagation to avoid duplicate logs
        self.logger.propagate = False

    def get_logger(self):
        return self.logger

# Create default logger instance
default_logger = LogManager().get_logger()

def get_logger(name=None):
    """Get a logger instance. All loggers share the same file handler."""
    if name:
        return LogManager(name).get_logger()
    return default_logger

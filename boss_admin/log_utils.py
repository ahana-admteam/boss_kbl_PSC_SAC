import os
import datetime
import logging
from logging.handlers import BaseRotatingHandler

class DailySizeRotatingFileHandler(BaseRotatingHandler):
    """
    Rotates log files:
    - Daily based on date
    - If file exceeds maxBytes (e.g., 5MB), continues with .1, .2, etc.
    Keeps all files forever (no deletion).
    """

    def __init__(self, base_dir, filename_prefix='django', maxBytes=5*1024*1024, encoding=None):
        self.base_dir = base_dir
        self.filename_prefix = filename_prefix
        self.maxBytes = maxBytes
        self.current_date = datetime.date.today()
        self._ensure_log_directory()

        self.baseFilename = self._get_log_filepath()
        super().__init__(self.baseFilename, 'a', encoding=encoding, delay=False)

    def _get_log_filepath(self, index=None):
        year = self.current_date.strftime('%Y')
        month = self.current_date.strftime('%m')
        day = self.current_date.strftime('%Y-%m-%d')
        filename = f"{self.filename_prefix}_{day}.log"
        if index is not None:
            filename += f".{index}"
        return os.path.join(self.base_dir, year, month, filename)

    def _ensure_log_directory(self):
        path = os.path.join(self.base_dir, self.current_date.strftime('%Y'), self.current_date.strftime('%m'))
        os.makedirs(path, exist_ok=True)

    def shouldRollover(self, record):
        if datetime.date.today() != self.current_date:
            return True  # date changed
        if self.stream is None:
            self.stream = self._open()
        self.stream.flush()
        if self.maxBytes > 0:
            self.stream.seek(0, os.SEEK_END)
            return self.stream.tell() >= self.maxBytes
        return False

    def doRollover(self):
        today = datetime.date.today()
        if today != self.current_date:
            self.current_date = today
            self._ensure_log_directory()
            self.baseFilename = self._get_log_filepath()
            self.stream.close()
            self.stream = self._open()
        else:
            index = 1
            new_path = self._get_log_filepath(index)
            while os.path.exists(new_path):
                index += 1
                new_path = self._get_log_filepath(index)

            self.stream.close()
            os.rename(self.baseFilename, new_path)
            self.stream = self._open()



class StreamToLogger:
    """
    Redirects prints to both logger and original stream (stdout/stderr).
    """
    def __init__(self, logger, level=logging.INFO, stream=None):
        self.logger = logger
        self.level = level
        self.stream = stream

    def write(self, message):
        if message.strip():
            self.logger.log(self.level, message.strip())
        if self.stream:
            self.stream.write(message)
            self.stream.flush()

    def flush(self):
        if self.stream:
            self.stream.flush()


class ExcludeWarningsFilter(logging.Filter):
    def filter(self, record):
        return record.levelno != logging.WARNING



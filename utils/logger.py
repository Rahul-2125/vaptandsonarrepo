import logging
import json
import pytz
from datetime import datetime
from typing import Optional

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

IST = pytz.timezone("Asia/Kolkata")


class Logger:
    COLORS = {
        "info": "\033[97m",
        "warning": "\033[93m",
        "error": "\033[91m",
        "reset": "\033[0m",
    }

    def info(
        self,
        message: Optional[str] = None,
        origin: Optional[str] = None,
        data: Optional[dict] = None,
    ):
        self._log("info", message, origin, data)

    def error(
        self,
        message: Optional[str] = None,
        origin: Optional[str] = None,
        data: Optional[dict] = None,
    ):
        self._log("error", message, origin, data)

    def warning(
        self,
        message: Optional[str] = None,
        origin: Optional[str] = None,
        data: Optional[dict] = None,
    ):
        self._log("warning", message, origin, data)

    def _log(self, level, message, origin, data):
        timestamp = datetime.now(IST).isoformat()
        color = self.COLORS.get(level, self.COLORS["reset"])
        log_message = ""

        if origin:
            log_message += f"Origin: {origin} - "

        log_message += f"{color}{message}{self.COLORS['reset']}"

        if data:
            if isinstance(data, dict):
                log_message += f" - Data: {json.dumps(data, indent=4)}"
            else:
                log_message += f" - Data: {data}"

        getattr(logging, level)(log_message)


logger = Logger()

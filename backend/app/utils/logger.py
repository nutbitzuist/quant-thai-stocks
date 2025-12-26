
import logging
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict

class StructuredLogger(logging.Logger):
    def _log(self, level, msg, args, exc_info=None, extra=None, stack_info=False, stacklevel=1):
        if extra is None:
            extra = {}
        
        # Add timestamp
        if "timestamp" not in extra:
            extra["timestamp"] = datetime.utcnow().isoformat()
            
        # Add log level
        extra["level"] = logging.getLevelName(level)
            
        # Call the original logger
        super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "line": record.lineno,
        }
        
        # Add extra fields but exclude standard logging keys
        standard_keys = [
            "args", "asctime", "created", "exc_info", "exc_text", "filename",
            "funcName", "levelname", "levelno", "lineno", "module",
            "msecs", "message", "msg", "name", "pathname", "process",
            "processName", "relativeCreated", "stack_info", "thread", "threadName"
        ]
        
        for key, value in record.__dict__.items():
            if key not in standard_keys and not key.startswith("_"):
                log_obj[key] = value

        # Exception info
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)

def setup_logger(name: str = "app"):
    logging.setLoggerClass(StructuredLogger)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Check if handler already exists
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        
    return logger

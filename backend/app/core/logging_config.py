"""Structured logging configuration.

In productie (`ENVIRONMENT=production`) loggen we in JSON Lines formaat
zodat log-aggregators (Loki, ELK, CloudWatch, Datadog) de velden direct
kunnen parsen. In development blijft de logging menselijk leesbaar.

Aanroep vanuit app/main.py via `configure_logging()` bij startup.
"""

import json
import logging
import sys
from datetime import datetime, timezone

from app.core.config import settings


class JsonFormatter(logging.Formatter):
    """Formatter die elke log-regel als JSON object schrijft."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        # Voeg extra velden toe die via logger.info(..., extra={...}) zijn gezet
        for key, value in record.__dict__.items():
            if key in payload or key.startswith("_"):
                continue
            if key in (
                "args", "msg", "levelname", "levelno", "pathname", "filename",
                "module", "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "name",
                "exc_info", "exc_text", "stack_info", "taskName",
            ):
                continue
            try:
                json.dumps(value)
                payload[key] = value
            except (TypeError, ValueError):
                payload[key] = str(value)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    """Configureer root logger op basis van ENVIRONMENT.

    Productie -> JSON Lines naar stdout (parseerbaar door log-aggregators).
    Development -> menselijk leesbaar formaat.
    """
    root = logging.getLogger()
    # Vermijd dubbele handlers bij hot-reload / herhaalde import
    for h in list(root.handlers):
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    if settings.ENVIRONMENT == "production":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
        )

    root.addHandler(handler)
    root.setLevel(logging.INFO)

    # Demp third-party loggers die anders veel ruis maken
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

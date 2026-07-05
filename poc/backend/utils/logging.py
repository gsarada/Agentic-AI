import logging
import sys
import time
from contextlib import contextmanager
from typing import Any, Generator

import structlog


def configure_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=level)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)


@contextmanager
def log_duration(logger: Any, event: str, **kwargs: Any) -> Generator[None, None, None]:
    start = time.perf_counter()
    try:
        yield
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(event, duration_ms=round(duration_ms, 2), status="success", **kwargs)
    except Exception as exc:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.error(
            event,
            duration_ms=round(duration_ms, 2),
            status="error",
            error=str(exc),
            **kwargs,
        )
        raise

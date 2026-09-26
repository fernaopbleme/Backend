import logging
import sys

from app.core.config import LOG_LEVEL


def configurar_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-8s %(name)s: %(message)s")
    )

    encoding = getattr(handler.stream, "encoding", None)
    if encoding:
        try:
            "áçõ".encode(encoding)
        except (UnicodeEncodeError, LookupError):
            reconfigure = getattr(handler.stream, "reconfigure", None)
            if reconfigure is not None:
                reconfigure(encoding="utf-8", errors="replace")

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(LOG_LEVEL)

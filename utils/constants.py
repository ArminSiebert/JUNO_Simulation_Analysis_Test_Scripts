import os
from warnings import warn


assert "WORKSPACE" in os.environ

WS_DIR = os.environ["WORKSPACE"]
DATA_DIR = f"{WS_DIR}/data"

JUNOSW_DIR = os.environ.get("JUNOTOP", None)
IS_JUNOSW = os.path.isdir(JUNOSW_DIR)

if not IS_JUNOSW:
    warn("The JUNO software is not installed. Some functions are not available.")

import logging
import sys
import warnings

LOG_PATTERN = (
    "[%(asctime)s]"
    "[%(filename)0s:%(lineno)s]"
    "[%(funcName)0s()][%(levelname)s] | %(message)s "
)
LOG_DATE_PATTERN = "%Y-%m-%d %H:%M:%S%z"


def configure_logs():
    """Method to configure the structure of a log"""

    logging.basicConfig(
        format=LOG_PATTERN,
        level=logging.INFO,
        datefmt=LOG_DATE_PATTERN,
        stream=sys.stdout,
    )


warnings.filterwarnings("ignore")

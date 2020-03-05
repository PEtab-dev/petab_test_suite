import os
import sys
import importlib
import logging
from .C import CASES_DIR

logger = logging.getLogger("petab_test_suite")


def create():
    """Create all test files."""

    case_list = os.scandir(CASES_DIR)
    case_list = sorted(f.name for f in case_list if f.is_dir())

    for case in case_list:
        case_dir = os.path.join(os.getcwd(), 'cases', case)
        logger.info('# ', case, case_dir)

        sys.path.append(case_dir)
        importlib.import_module(case)


def clear():
    """Clear all model folders."""

    case_list = os.scandir(CASES_DIR)
    for case in case_list:
        case_dir = os.path.join(CASES_DIR, case)
        for file_ in os.scandir(case_dir):
            if file_.name.startswith('_') and not file_.is_dir():
                os.remove(file_.path)

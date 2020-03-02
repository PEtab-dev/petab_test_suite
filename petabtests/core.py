import os
import sys
import importlib
import logging

logger = logging.getLogger("petab_test_suite")


def main():
    """Create all test files"""

    case_list = os.scandir('cases')
    case_list = sorted(f.name for f in case_list if f.is_dir())

    for case in case_list:
        case_dir = os.path.join(os.getcwd(), 'cases', case)
        logger.info('# ', case, case_dir)

        sys.path.append(case_dir)
        importlib.import_module(case)

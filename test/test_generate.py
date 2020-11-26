from petabtests.core import create
from petabtests.C import CASES_DIR

import sys
import subprocess


def test_check_cases_up_to_date():
    sys.path.insert(0, CASES_DIR)
    create()
    has_changes = subprocess.run(['git', 'diff', '--quiet',
                                 CASES_DIR]).returncode
    assert not has_changes

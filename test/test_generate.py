from petabtests.core import create
from petabtests.C import CASES_DIR

import sys
import subprocess


def test_check_cases_up_to_date():
    sys.path.insert(0, CASES_DIR)
    create()
    res = subprocess.run(
        ["git", "diff", "--exit-code", CASES_DIR], capture_output=True
    )
    has_changes = res.returncode
    assert not has_changes, res.stdout.decode()

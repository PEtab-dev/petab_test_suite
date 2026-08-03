import subprocess
import sys

from petabtests.C import CASES_DIR
from petabtests.core import create_all, create_case


def test_check_cases_up_to_date():
    sys.path.insert(0, CASES_DIR)
    create_all()
    res = subprocess.run(
        ["git", "diff", "--exit-code", CASES_DIR],
        capture_output=True,
        check=False,
    )
    has_changes = res.returncode
    assert not has_changes, res.stdout.decode()


def test_create_case():
    """Test creating a single test case.

    Mostly for debugging purposes.
    """
    format_ = "sbml"
    version = "v2.0.0"
    id_ = "0022"
    create_case(format_=format_, version=version, id_=id_)

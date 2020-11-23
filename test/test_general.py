import petabtests
import os


def test_cases_dir_exists():
    assert os.path.isdir(petabtests.BASE_DIR)
    assert os.path.isdir(petabtests.CASES_DIR)
    assert os.path.isdir(petabtests.SBML_DIR)
    assert os.path.isdir(petabtests.PYSB_DIR)

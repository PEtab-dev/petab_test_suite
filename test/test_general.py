import petabtests
import os


def test_cases_dir_exists():
    assert os.path.isdir(petabtests.BASE_DIR)
    assert os.path.isdir(petabtests.CASES_DIR)
    assert os.path.isdir(
        petabtests.get_cases_dir(format_="sbml", version="v1.0.0")
    )
    assert os.path.isdir(
        petabtests.get_cases_dir(format_="sbml", version="v2.0.0")
    )
    assert os.path.isdir(
        petabtests.get_cases_dir(format_="pysb", version="v2.0.0")
    )

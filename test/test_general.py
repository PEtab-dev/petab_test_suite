import petabtests
import os
import pytest


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


@pytest.mark.parametrize(
    "format_,version",
    [
        ("sbml", "v2.0.0"),
        ("pysb", "v2.0.0"),
    ],
)
def test_lint_all_v2_cases(format_, version):
    """Regression test: all v2 test cases must pass PEtab linting."""
    from petab.v2.lint import lint_problem

    cases_dir = petabtests.get_cases_dir(format_=format_, version=version)
    cases = sorted(
        f.name
        for f in os.scandir(cases_dir)
        if f.is_dir() and f.name.isdigit()
    )
    assert cases, f"No cases found in {cases_dir}"

    failures = {}
    for case_id in cases:
        yaml_path = cases_dir / case_id / f"_{case_id}.yaml"
        if not yaml_path.exists():
            continue
        results = lint_problem(yaml_path)
        if results:
            failures[case_id] = [str(r) for r in results]

    assert not failures, (
        "Linting failed for the following test cases:\n"
        + "\n".join(
            f"  {case_id}: {'; '.join(errs)}"
            for case_id, errs in sorted(failures.items())
        )
    )

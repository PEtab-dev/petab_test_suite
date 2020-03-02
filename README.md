# PEtab test suite

The PEtab test suite is a collection of test models for the
[PEtab](https://github.com/petab-dev/petab) parameter estimation data format.
It is intended to be used to verify and quantify PEtab-support by developers
of tools for model simulation and parameter estimation.

## Download and install the test suite

The PEtab test suite can be downloaded from GitHub via

    git clone https://github.com/petab-dev/petab_test_suite

The test suite comes with all necessary files pregenerated. 
In the [petabtests](petabtests) subdirectory, it contains a python module for
generating the tests and evaluating results. This can be installed via

    cd petab_test_suite
    pip3 install -e .

## Use the test suite

The [cases](cases) subdirectory contains a collection of enumerated tests.
Each test contains a descriptive `wxyz.md` file, and a script file `wxyz.py`
file that can be used to generate all problem and solution files for the test.
The necessary files are in the same case specific folder, starting with an
underscore. 
In each case folder, there is a file `_wxyz.yaml` containing the parameter
estimation problem description, and a file `_wxyz_solution.yaml` containing
information on the expected results: chi2 value, log-likelihood, simulation
table reference, and tolerances.

After download, all necessary files are already pregenerated.

Further, installation of the petabtests module installs a routine to recreate
the problem and solution files for all test problems. It can be invoked via

    cd petab_test_suite
    petabtests_create

## Evaluate results

To evaluate how a tool performs on a given test problem, three metrics are
employed: Simulations, chi2 value and log-likelihood. A tool can be said to
cover a test problem if any of those values matches the ground truth values
up to some tolerance.

The python module provides convenience functions for evaluation in
[petabtests/evaluate.py](petabtests/evaluate.py).

TODO A table with cases as rows will be created, with a column for each tool,
indicating whether the test case is covered. Additional information if the
tool allows to compute e.g. likelihood, or only chi2 values, is supposed to
be provided.

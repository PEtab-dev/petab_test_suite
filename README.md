# PEtab test suite

The PEtab test suite is a collection of test models for the [PEtab](https://github.com/petab-dev/petab) parameter estimation data format. It is intended to be used to check the extend of tools' coverage of the format.

## Download and install the test suite

The PEtab test suite can be downloaded from GitHub via

    git clone https://github.com/petab-dev/petab_test_suite

The test suite comes with all necessary files pregenerated. In the [petabtests](petabtests) subdirectory, it contains a python module for generating the tests and evaluating results. This can be installed via

    cd petab_test_suite
    pip3 install -e .

## Use the test suite

The [cases](cases) subdirectoy contains a collection of enumerated tests. Each test contains a descriptive wxyz.md file, and a script file wxyz.py file that can be used to generate all problem and solution files for the test. The necessary files are in the same case specific folder, starting with an underscore. After download, all necessary files are already pregenerated.

Further, installation of the petabtests module installs a routine to recreate the problem and solution files for all test problems. It can be invoked via

    cd petab_test_suite
    petabtests_create

# PEtab math expression tests

This directory contains test cases for parsing PEtab math expressions.

`math_tests.yaml` contains a list of test cases under `cases`. 
Each test case consists of a valid PEtab math expression under `expression` and
the expected result of parsing the expression under `expected`.
The expected result may be a numeric value or a symbolic expression.
Booleans are expected to be converted to floats.

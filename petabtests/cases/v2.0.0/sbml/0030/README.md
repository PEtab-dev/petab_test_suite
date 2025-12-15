# PEtab test case 0030

## Objective

This case tests simultaneous re-initialization of compartment size and
contained species when an SBML event triggers at the exact same
time-point as a PEtab condition.

## Model

A species `S`, defined in terms of concentrations, with `dS/dt = p = 1`,
in a compartment `C`. `S` and `C` are changed via the condition table.

There is a PEtab condition triggered at `t=10`, which is triggered
at the exact time as an SBML event that re-initializes the compartment
volume after the condition table is applied.

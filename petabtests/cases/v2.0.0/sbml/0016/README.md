# PEtab test case 0016

## Objective

This case tests simultaneous re-initialization of compartment size and
contained species with state-dependent expressions.

## Model

A species `S`, defined in terms of concentrations, with `dS/dt = p = 1`,
in a compartment `C`. `S` and `C` are changed via the condition table.

There is a PEtab condition triggered at `t=10` which triggers an SBML
event that re-initializes the compartment size that must be executed
after the condition table is applied.

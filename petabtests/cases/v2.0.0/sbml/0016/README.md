# PEtab test case 0016

## Objective

This case tests simultaneous re-initialization of compartment size and
contained species with state-dependent expressions.

## Model

A species `S`, defined in terms of concentrations, with `dS/dt = p = 1`,
in a compartment `C`. `S` and `C` are changed via the condition table.

There is an event triggered at `t=10` that re-initializes the compartment
size that must be executed after the conditions table is applied.

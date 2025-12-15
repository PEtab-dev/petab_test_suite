# PEtab test case 0026

## Objective

This case tests the handling of initial concentrations that are specified
via mathematical expressions (rather than a single value or parameter) in
the conditions table. For species `A`, the initial concentration is given
by an expression containing both parameters to be estimated and parameters
that are not estimated. For species `B`, the initial concentration is
specified via an expression involving only parameters that are not
estimated.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

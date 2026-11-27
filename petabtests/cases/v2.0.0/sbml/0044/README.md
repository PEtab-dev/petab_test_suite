# PEtab test case 0044

## Objective

This case tests the interaction of parameter table entries and
`InitialAssignment`s to model parameters.

* `k2` has the `InitialAssignment` `k2 = 2 * k1`, and is listed in the
  parameter table (estimated). The parameter table value (`0.6`) replaces the
  `InitialAssignment`.
* `a0` has the numeric `InitialAssignment` `a0 = 2 * 3`, and is listed in the
  parameter table (not estimated). The parameter table value (`1`) replaces
  the `InitialAssignment`.
* `b0` has the `InitialAssignment` `b0 = k1 / 4`, and is not listed in the
  parameter table. The `InitialAssignment` is kept, and is evaluated with the
  parameter table value of `k1` (`0.8`), i.e., `b0 = 0.2`.
* `s` is set to `k2` in the condition table at the start of the experiment,
  and `k2` is used as observable parameter override in the measurement table.
  Both refer to the parameter table value of `k2`, i.e., the same value that
  is used in the model.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics, with initial concentrations `a0` and `b0`.

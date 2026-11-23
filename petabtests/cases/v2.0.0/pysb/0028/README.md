# PEtab test case 0028

## Objective

This case tests applying a PEtab condition at a non-initial time point
that does not have any measurements.
The target value depends on the current model state.

At `t=7`, the amount of `A` is increased by `5`.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

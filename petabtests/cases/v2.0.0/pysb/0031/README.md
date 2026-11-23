# PEtab test case 0031

## Objective

This case tests applying two PEtab conditions simultaneously, at a time
point that also has measurements.

At `t=10`, the amount of `A` is increased by `5` and the amount of `B` by
`3`.
The measurements at `t=10` reflect the updated state.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

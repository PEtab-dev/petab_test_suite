# PEtab test case 0018

## Objective

This case tests support for a non-zero simulation start time after
pre-equilibration.

The model is to be simulated for a preequilibration condition and a
simulation condition starting at `t=10`.
For preequilibration, `k1` is set to `0.3`, `A` is initialized with `0`,
and `B` with `2`.
For simulation, `k1` is set to `0.8`, `A` is reinitialized to the value in
the condition table after preequilibration, `B` is not updated.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

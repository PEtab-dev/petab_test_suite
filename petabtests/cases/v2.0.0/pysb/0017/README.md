# PEtab test case 0017

## Objective

This case tests support for partial preequilibration and usage of the
mapping table.

The model is to be simulated for a preequilibration condition and a
simulation condition.
For preequilibration, `A` is initialized with `0` and `B` with `2`.
For simulation, `B` is not changed in the condition table, meaning that it
keeps the result from preequilibration.
`A` is reinitialized to the value in the condition table after
preequilibration.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

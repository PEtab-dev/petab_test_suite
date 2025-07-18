# PEtab test case 0017

## Objective

This case tests support for pre-equilibration with reinitialization of a
species.

The model is to be simulated for a pre-equilibration condition and a
simulation condition.
For pre-equilibration, species `B` is initialized with `2`. For simulation,
`A` is reinitialized to the value in the condition table after
pre-equilibration. `B` is not updated, meaning that it keeps the state from
pre-equilibration.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

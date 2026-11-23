# PEtab test case 0002

## Objective

This case tests support for multiple simulation conditions

The model is to be simulated for two different experimental conditions
(here: different initial amounts of `A`).

`b0` is not changed in the condition table, so the model value of `b0` is
used for either condition.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

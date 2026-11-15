# PEtab test case 0006

## Objective

This case tests support for time-point specific overrides in the measurement
table.

The model is to be simulated for a single experimental condition. The single
model output is scaled by a different parameter at each timepoint, and the
noise parameter differs between timepoints. The noise formula is not just the
noise parameter placeholder, so the numeric override must be substituted into
the noise formula, not used as standard deviation directly.
The noise formula depends on the observable value, so it has to be evaluated
for each timepoint.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

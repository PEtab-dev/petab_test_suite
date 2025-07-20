# PEtab test case 0007

## Objective

This case tests log-normal noise.

The model is to be simulated for a single experimental condition.
Observables `obs_a` and `obs_b` are the same except for the noise distribution.
The noise distributions need to be accounted for when computing chi2 and
likelihood.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

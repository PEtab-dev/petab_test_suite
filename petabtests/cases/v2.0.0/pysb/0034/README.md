# PEtab test case 0034

## Objective

This case tests changing a rate parameter at a non-initial time point
to the value of an estimated parameter.

At `t=0`, `k1` is set to `0.8`. At `t=10`, `k1` is set to the estimated
parameter `k1_new`.
The species are not reinitialized at `t=10`.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

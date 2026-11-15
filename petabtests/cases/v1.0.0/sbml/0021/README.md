# PEtab test case 0021

## Objective

This case tests a single numeric noise parameter override in the measurement
table, with a noise formula that is not just the noise parameter placeholder.
The numeric override must be substituted into the noise formula, not used as
standard deviation directly.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

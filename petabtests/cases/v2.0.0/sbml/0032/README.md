# PEtab test case 0032

## Objective

This case tests handling of parameters to be estimated both assigning
initial concentrations, and appearing in the observable formula.
For species `A`, the initial concentration is estimated, and the parameter
setting the concentration of A appears in the observable formulas. For species
`B`, the initial concentration is specified in the parameters table.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

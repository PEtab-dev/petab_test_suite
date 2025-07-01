# PEtab test case 0020

## Objective

This case tests handling of initial concentrations that are specified
in the conditions table. For species `A`, the initial concentration is
estimated. For species `B`, the initial concentration is specified as
`NaN` in the condition table, thus the SBML model initial value should 
be used.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

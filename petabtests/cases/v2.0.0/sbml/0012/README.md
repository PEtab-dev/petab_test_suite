# PEtab test case 0012

## Objective

This case tests initial compartment sizes in the condition table.

Note that this change will preserve the initial state of the model in terms
of amounts. I.e., the change of the compartment size via the conditions table,
will change the concentrations of all contained species.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

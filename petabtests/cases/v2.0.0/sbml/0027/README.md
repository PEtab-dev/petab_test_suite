# PEtab test case 0027

## Objective

This case tests support for parametric overrides from condition table
via math expressions.

The model is simulated for two different experimental conditions
(here: different initial concentrations). The observable is offset via
a parametric override in the condition table (i.e. the actual value
has to be taken from the parameter table). The formulas in the
condition table are mathematical expressions consisting of
numerical values, parameters to be estimated, and parameters that
are not to be estimated.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

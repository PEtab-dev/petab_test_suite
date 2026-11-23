# PEtab test case 0035

## Objective

This case tests changing a parameter that is used in an `Initial`, in the
first and in a later period.

At `t=0`, `a0` is set to `2`. This is applied before model initialization,
so the initial amount of `A` is `2`.
At `t=10`, `a0` is set to `5`. Since species are not reinitialized
according to their `Initial`s, this does not affect `A`.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.
`a0` is a `pysb.Parameter` that defines the initial amount of `A`.

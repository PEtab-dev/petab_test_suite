# PEtab test case 0036

## Objective

This case tests a compartment size change in the first period, for a model
where the compartment size affects the dynamics.

The compartment size is changed by targeting the compartment ID `cell`.
Experiment `e0` changes the size of `cell` from `2` to `4` at `t=0`.
The species amounts are not changed.
Experiment `e_ref` uses the default compartment size.

## Model

An irreversible bimolecular reaction `A + B -> C` with mass action
kinetics in a compartment `cell` with size `vol = 2`.
Following BioNetGen's volume scaling, and with PySB species being amounts,
`dA/dt = -k1 / size(cell) * A * B`.

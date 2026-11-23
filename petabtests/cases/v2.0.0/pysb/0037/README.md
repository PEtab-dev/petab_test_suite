# PEtab test case 0037

## Objective

This case tests a compartment size change at a non-initial time point,
together with a state-dependent change of a species in that compartment.

At `t=10`, the compartment size parameter `vol` is changed from `2` to `4`,
and the amount of `B` is increased by `2`.
Changing `vol` changes the size of `cell`. PySB species are amounts,
which are not changed by this. Therefore, the amount of `A` is not changed
at `t=10`, and only the volume-dependent reaction rate changes.

## Model

An irreversible bimolecular reaction `A + B -> C` with mass action
kinetics in a compartment `cell` with size `vol = 2`.
Following BioNetGen's volume scaling, and with PySB species being amounts,
`dA/dt = -k1 / vol * A * B`.

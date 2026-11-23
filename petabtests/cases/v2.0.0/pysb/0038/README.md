# PEtab test case 0038

## Objective

This case tests first-period species changes that differ between
experiments, including a change of a species without an `Initial`.

* `e_a3`: `A` is set to `3` at `t=0`.
* `e_a5`: `A` is set to `5` at `t=0`.
* `e_ref`: no changes.
* `e_c2`: `C` is set to `2` at `t=0`. The model has no `Initial` for `C`,
  i.e., its default initial amount is `0`.

## Model

An irreversible bimolecular reaction `A + B -> C` with mass action
kinetics, without compartments.
`dA/dt = dB/dt = -k1 * A * B`, `dC/dt = k1 * A * B`.
`A` and `B` have `Initial`s with amounts `1`, `C` has no `Initial`.

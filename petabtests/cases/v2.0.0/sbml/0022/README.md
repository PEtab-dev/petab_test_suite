# PEtab test case 0022

## Objective

This case tests simultaneous re-initialization of compartment size and
contained species.

## Model

Two simple conversion reactions `A <=> B`, `a <=> b` in a single compartment,
following mass action kinetics.

`A` and `B` are species defined in terms of concentrations, `a` and `b` are
`hasOnlySubstanceUnits=True` species defined in terms of amounts.

The compartment size and the species amounts/concentrations are re-initialized
at time 10. The assigned values are independent of the model state.

At time 10, the conditions table changes:
* The compartment size from 2 to 4.
* The concentration of `A` to `5`. This implies that the amount of
  `A` is changed to `5 * 4 = 20` (concentration * compartment size).
* The amount of `a` to `20`.

This leads to the following model state at time 10:
* The concentration of `A` is the values assigned in the conditions table, `5`.
* The amount of `a` is `20`, unaffected by the compartment size change.
* The concentration of `B` is `(2 * 2) / 4 = 1`
  (previous amount / new volume
  = previous concentration * previous volume / new volume).
* The amount of `b` remains at `4`, unaffected by the compartment size change.

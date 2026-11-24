# PEtab test case 0043

## Objective

This case tests species changes to estimated parameter-dependent values in
and after pre-equilibration.

* `e_preeq_b`: For pre-equilibration, `B` is initialized with `4 * p`,
  with the estimated parameter `p`. The main period starts at `t=0` without
  changes, i.e., from the steady state.
* `e_main_a`: After pre-equilibration without changes, `A` is set to
  `4 * p` at the start of the main period at `t=0`. `B` keeps its
  steady-state value.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

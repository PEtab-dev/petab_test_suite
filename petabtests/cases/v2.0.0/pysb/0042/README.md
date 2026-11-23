# PEtab test case 0042

## Objective

This case tests species changes after the first period whose target value
depends on an estimated parameter, `time`, and another species via the
mapping table.

`A` is set to `p * time / 10 + B_c`, with the estimated parameter `p`,
where `B_c` is mapped to `B`:

* `e_t10`: The experiment starts at `t=0` without changes. At `t=10`,
  `A` is set to `p + B(10)`.
* `e_preeq`: After pre-equilibration without changes, the main period
  starts at `t=5`, where `A` is set to `p / 2 + B_ss`, with `B_ss` the
  steady-state value of `B`.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

# PEtab test case 0039

## Objective

This case tests changes at a non-initial time point whose target values
depend on estimated parameters, targeting a parameter and a species.

* `e_a0`: At `t=10`, the parameter `a0` is set to the estimated parameter
  `a0_new`. `a0` is used both as synthesis rate and in the `Initial` of
  `A`. The synthesis rate changes from `t=10` on, but `A` is not
  reinitialized.
* `e_add`: At `t=10`, the amount of `A` is increased by the estimated
  parameter `p_add`.

## Model

Synthesis and degradation of `A`, without compartments:
`dA/dt = a0 - kdeg * A`, with initial amount `A(0) = a0`.

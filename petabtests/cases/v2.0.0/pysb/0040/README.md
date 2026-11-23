# PEtab test case 0040

## Objective

This case tests a species change at a non-initial time point in a model
with conservation laws.

The model conserves the total amounts of `A` (`A + AB`) and `B`
(`B + AB`). At `t=10`, the amount of free `A` is increased by `1`, which
increases the total amount of `A` by `1`. The total amount of `B` is not
changed.

## Model

A reversible binding reaction `A + B <=> AB` with mass action kinetics,
without compartments, where `A` is free `A_(b=None)`, `B` is free
`B_(a=None)`, and `AB` is the complex `A_(b=1) % B_(a=1)`:
`dAB/dt = kf * A * B - kr * AB`.

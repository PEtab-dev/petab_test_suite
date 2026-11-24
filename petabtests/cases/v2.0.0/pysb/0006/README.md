# PEtab test case 0006

## Objective

This case tests support for time-point specific overrides in the measurement
table.

The model is to be simulated for a single experimental condition. The
noise parameters differ between timepoints for both model outputs:

* `obs_a` is scaled by a different numeric value at each timepoint. Its
  noise formula is not just the noise parameter placeholder, so the numeric
  override must be substituted into the noise formula, not used as standard
  deviation directly.
* `obs_b` has a noise formula that consists only of the noise parameter
  placeholder, so the numeric override is the standard deviation.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

# PEtab test case 0041

## Objective

This case tests `time` in the target value of a species change in the first
period of an experiment with a non-zero start time.

The experiment starts at `t=5`, where `A` is set to `time + p`, with the
estimated parameter `p`, i.e., `A(5) = 5 + p`.

## Model

A simple conversion reaction `A <=> B` in a single compartment, following
mass action kinetics.

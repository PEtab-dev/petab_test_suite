# PEtab test case 0024

## Objective

This case tests events occurring during steady-state simulations.

## Model

A parameter `p` is target of an event assignment that is executed at t = 1000.
Although the model starts with $\dot{x} = 0$, the simulation must still run
until $\dot{x}$ *remains* 0, i.e., the event must still be executed.
This is applies to both the pre-simulation and the simulation for the
steady state measurement.

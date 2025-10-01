# PEtab test case 0023

## Objective

This case tests events occurring during steady-state simulations.

## Model

A parameter `p` is target of an event assignment that is executed at t = 490,
which is also the time point when the steady state is reached.
The event increases `p` by 1000, which is also the value of the observable.
The event must not be executed again after pre-equilibration
(the trigger state is not reinitialized).

from pysb import Model, Monomer, Parameter, Compartment, Rule, Initial

Model()

Compartment('compartment')

Monomer('A')
Monomer('B')

Parameter('a0', 1.0)
Parameter('b0', 1.0)
Parameter('k1', 0.0)
Parameter('k2', 0.0)

Rule('conversion', A() ** compartment | B() ** compartment, k1, k2)

Initial(A() ** compartment, a0)
Initial(B() ** compartment, b0)
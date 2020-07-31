from pysb import Model, Monomer, Parameter, Compartment, Rule, Initial, Observable

Model()

Compartment('compartment')

Monomer('A_')
Monomer('B_')

Parameter('a0', 1.0)
Parameter('b0', 1.0)
Parameter('k1', 0.0)
Parameter('k2', 0.0)

Rule('conversion', A_() ** compartment | B_() ** compartment, k1, k2)

Initial(A_() ** compartment, a0)
Initial(B_() ** compartment, b0)

Observable("A", A_())
Observable("B", B_())

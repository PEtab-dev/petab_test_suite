from pysb import (
    Compartment,
    Initial,
    Model,
    Monomer,
    Observable,
    Parameter,
    Rule,
)

Model()

Parameter("vol", 2.0)
Compartment("cell", size=vol)

Monomer("A_")
Monomer("B_")
Monomer("C_")

Parameter("a0", 2.0)
Parameter("b0", 1.0)
Parameter("k1", 0.5)

Rule("binding", A_() ** cell + B_() ** cell >> C_() ** cell, k1)

Initial(A_() ** cell, a0)
Initial(B_() ** cell, b0)

Observable("A", A_())
Observable("B", B_())
Observable("C", C_())

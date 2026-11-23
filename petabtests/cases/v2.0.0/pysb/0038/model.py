from pysb import (
    Initial,
    Model,
    Monomer,
    Observable,
    Parameter,
    Rule,
)

Model()

Monomer("A_")
Monomer("B_")
Monomer("C_")

Parameter("a0", 1.0)
Parameter("b0", 1.0)
Parameter("k1", 0.5)

Rule("binding", A_() + B_() >> C_(), k1)

# no Initial for C_
Initial(A_(), a0)
Initial(B_(), b0)

Observable("A", A_())
Observable("C", C_())

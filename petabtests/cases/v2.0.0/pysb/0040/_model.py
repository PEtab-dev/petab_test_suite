from pysb import (
    Initial,
    Model,
    Monomer,
    Observable,
    Parameter,
    Rule,
)

Model()

Monomer("A_", ["b"])
Monomer("B_", ["a"])

Parameter("a0", 1.0)
Parameter("b0", 0.5)
Parameter("kf", 1.0)
Parameter("kr", 0.5)

Rule("binding", A_(b=None) + B_(a=None) | A_(b=1) % B_(a=1), kf, kr)

Initial(A_(b=None), a0)
Initial(B_(a=None), b0)

Observable("A", A_(b=None))
Observable("B", B_(a=None))
Observable("AB", A_(b=1) % B_(a=1))

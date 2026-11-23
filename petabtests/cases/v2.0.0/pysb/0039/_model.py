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

Parameter("a0", 1.0)
Parameter("kdeg", 0.5)

# a0 is used both as synthesis rate and as initial amount
Rule("synthesis", None >> A_(), a0)
Rule("degradation", A_() >> None, kdeg)

Initial(A_(), a0)

Observable("A", A_())

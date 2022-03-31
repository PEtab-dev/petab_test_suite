import pandas as pd
import petab
from petab.C import *
from pathlib import Path
from petabtests import *

test_id = 18

skip_formats = {'pysb'}

# problem --------------------------------------------------------------------

model = str(Path(__file__).parent / "model.xml")


def get_model():
    import simplesbml
    model = simplesbml.SbmlModel()
    model.addParameter("a0", 1)
    model.addParameter("b0", 1)
    model.addParameter("k1", 0)
    model.addParameter("k2", 0)
    model.addCompartment(comp_id="compartment")
    model.addSpecies("[A]", 0, comp="compartment")
    model.addParameter("B", 0)
    model.addInitialAssignment("A", "a0")
    model.addInitialAssignment("B", "b0")
    model.addRateRule("A", "compartment * k2 * B - compartment * k1 * A")
    model.addRateRule("B", "- compartment * k2 * B + compartment * k1 * A")
    return model


with open(model, "w") as f:
    f.write(get_model().toSBML())


condition_df = pd.DataFrame(data={
    CONDITION_ID: ['preeq_c0', 'c0'],
    'k1': [0.3, 0.8],
    'B': [2.0, 'NaN'],
    'A': [0, 1],
}).set_index([CONDITION_ID])

measurement_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a', 'obs_a'],
    PREEQUILIBRATION_CONDITION_ID: ['preeq_c0', 'preeq_c0'],
    SIMULATION_CONDITION_ID: ['c0', 'c0'],
    TIME: [1, 10],
    MEASUREMENT: [0.7, 0.1]
})

observable_df = pd.DataFrame(data={
    OBSERVABLE_ID: ['obs_a'],
    OBSERVABLE_FORMULA: ['A'],
    NOISE_FORMULA: [0.5]
}).set_index([OBSERVABLE_ID])

parameter_df = pd.DataFrame(data={
    PARAMETER_ID: ['k2'],
    PARAMETER_SCALE: [LIN],
    LOWER_BOUND: [0],
    UPPER_BOUND: [10],
    NOMINAL_VALUE: [0.6],
    ESTIMATE: [1],
}).set_index(PARAMETER_ID)


# solutions ------------------------------------------------------------------

simulation_df = measurement_df.copy(deep=True).rename(
    columns={MEASUREMENT: SIMULATION})
# simulate for far time point as steady state
steady_state_b = analytical_b(1000, 0, 2.0, 0.3, 0.6)
# use steady state as initial state
simulation_df[SIMULATION] = [
    analytical_a(t, 1, steady_state_b, 0.8, 0.6)
    for t in simulation_df[TIME]]

chi2 = petab.calculate_chi2(
    measurement_df, simulation_df, observable_df, parameter_df)

llh = petab.calculate_llh(
    measurement_df, simulation_df, observable_df, parameter_df)
print(llh)

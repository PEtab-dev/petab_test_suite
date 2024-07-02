"""Antimony -> SBML"""

import antimony as ant
from pathlib import Path


def antimony_to_sbml_str(ant_model: str | Path) -> str:
    """Convert Antimony string to SBML model.

    Arguments:
        ant_str:
            Antimony model as string (model, not filename), or Path to file.

    Returns:
        SBML model as string.
    """

    # Unload everything / free memory
    ant.clearPreviousLoads()
    ant.freeAll()

    if isinstance(ant_model, Path):
        status = ant.loadAntimonyFile(str(ant_model))
    else:
        status = ant.loadAntimonyString(ant_model)
    if status < 0:
        raise RuntimeError(
            f"Antimony model could not be loaded: {ant.getLastError()}"
        )

    if (main_module_name := ant.getMainModuleName()) is None:
        raise AssertionError("There is no Antimony module.")

    sbml_str = ant.getSBMLString(main_module_name)
    if not sbml_str:
        raise ValueError("Antimony model could not be converted to SBML.")

    return sbml_str

from petabtests.antimony import antimony_to_sbml_str
import libsbml
import tempfile
from pathlib import Path


def test_antimony_file_to_sbml_str():
    ant_model = """
        model test
          S1 -> S2; k1*S1
          k1 = 0.1
          S1 = 10
        end
        """

    with tempfile.TemporaryDirectory() as tmpdirname:
        ant_file = Path(tmpdirname, "test.ant")
        ant_file.write_text(ant_model)
        sbml_str = antimony_to_sbml_str(ant_model)

    assert sbml_str == antimony_to_sbml_str(ant_model)
    assert sbml_str.startswith("<?xml ")

    sbml_doc = libsbml.readSBMLFromString(sbml_str)
    sbml_model = sbml_doc.getModel()
    assert sbml_model.getNumSpecies() == 2
    assert sbml_model.getNumReactions() == 1
    assert sbml_model.getNumParameters() == 1

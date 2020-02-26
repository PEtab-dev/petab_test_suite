import numpy as np
from typing import Union, List
import pandas as pd
import petab
import os
from petab.C import *
import yaml
from shutil import copyfile

from .model import *


def yaml_name(_id: Union[int, str]) -> str:
    return test_id_str(_id) + '.yaml'


def test_id_str(_id: str) -> str:
    return f"{_id:0>4}"


def write_files(test_id,
                parameter_df: pd.DataFrame = None,
                condition_dfs: List[pd.DataFrame] = None,
                observable_dfs: List[pd.DataFrame] = None,
                measurement_dfs: List[pd.DataFrame] = None,
                simulation_dfs: pd.DataFrame = None) -> None:
    id_str = test_id_str(test_id)
    # petab yaml
    model_name = 'model.xml'
    yaml_fname = yaml_name(test_id)
    config = {
        FORMAT_VERSION: petab.__format_version__,
        PROBLEMS: [
            {
                SBML_FILES: [model_name],
                CONDITION_FILES: [],
                MEASUREMENT_FILES: [],
                OBSERVABLE_FILES: [],
            },
        ]
    }

    # parameters
    fname = f"parameters.tsv"
    petab.write_parameter_df(parameter_df,
                             os.path.join('cases', id_str, fname))
    config[PARAMETER_FILE] = fname

    # model
    copyfile(os.path.join('petabtests', 'conversion.xml'),
             os.path.join('cases', id_str, model_name))

    # conditions, observables, measurements, simulations
    for name, writer, dfs in zip(
            ['conditions', 'measurements', 'observables', 'simulations'],
            [petab.write_condition_df, petab.write_measurement_df,
             petab.write_observable_df, petab.write_measurement_df],
            [condition_dfs, measurement_dfs, observable_dfs, simulation_dfs]):
        if not dfs:
            continue
        for idx, df in enumerate(dfs):
            if len(dfs) == 1:
                idx = ''
            fname = f"{name}{idx}.tsv"
            writer(df, os.path.join('cases', id_str, fname))
            if name != 'simulations':
                config[PROBLEMS][0][name[0:-1] + '_files'].append(fname)

    # validate petab
    petab.validate(config, path_prefix=os.path.join('cases', id_str))

    # yaml
    with open(os.path.join('cases', id_str, yaml_fname), 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)

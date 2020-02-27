import numpy as np
from typing import Union, List
import pandas as pd
import petab
import os
from petab.C import *
import yaml
from shutil import copyfile

from .model import *

# constant definitions
LLH = 'llh'
CHI2 = 'chi2'
SIMULATION_FILES = 'simulation_files'


def problem_yaml_name(_id: Union[int, str]) -> str:
    return '_' + test_id_str(_id) + '.yaml'


def solution_yaml_name(_id: Union[int, str]) -> str:
    return '_' + test_id_str(_id) + '_solution.yaml'


def test_id_str(_id: str) -> str:
    return f"{_id:0>4}"


def write_problem(test_id,
                  parameter_df: pd.DataFrame,
                  condition_dfs: List[pd.DataFrame],
                  observable_dfs: List[pd.DataFrame],
                  measurement_dfs: List[pd.DataFrame]) -> None:
    id_str = test_id_str(test_id)
    model_name = '_model.xml'  # TODO allow passing a model
    yaml_fname = problem_yaml_name(test_id)

    # petab yaml
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
    fname = f"_parameters.tsv"
    petab.write_parameter_df(parameter_df,
                             os.path.join('cases', id_str, fname))
    config[PARAMETER_FILE] = fname

    # model
    copyfile(os.path.join('petabtests', 'conversion.xml'),
             os.path.join('cases', id_str, model_name))

    # conditions, observables, measurements, simulations
    for name, writer, dfs in zip(
            ['conditions', 'measurements', 'observables'],
            [petab.write_condition_df, petab.write_measurement_df,
             petab.write_observable_df],
            [condition_dfs, measurement_dfs, observable_dfs]):
        _write_dfs_to_files(id_str, name, writer, dfs, config[PROBLEMS][0])

    # validate petab
    petab.validate(config, path_prefix=os.path.join('cases', id_str))

    # yaml
    with open(os.path.join('cases', id_str, yaml_fname), 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)


def write_solution(test_id,
                   simulation_dfs: List[pd.DataFrame],
                   chi2: float, llh: float):
    id_str = test_id_str(test_id)
    yaml_fname = solution_yaml_name(test_id)

    # solution yaml
    config = {
        CHI2: float(chi2),
        LLH: float(llh),
        SIMULATION_FILES: [],
    }

    # simulations
    _write_dfs_to_files(
        id_str, "simulations", petab.write_measurement_df,
        simulation_dfs, config)

    with open(os.path.join('cases', id_str, yaml_fname), 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False)


def _write_dfs_to_files(id_str, name, writer, dfs, config):
    """Write data frames to files and add them to config."""
    for idx, df in enumerate(dfs):
        if len(dfs) == 1:
            idx = ''
        fname = f"_{name}{idx}.tsv"
        writer(df, os.path.join('cases', id_str, fname))
        if config:
            config[name[0:-1] + '_files'].append(fname)

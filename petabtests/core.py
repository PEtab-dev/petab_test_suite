import os
import sys
import importlib
import logging
import re
from .C import CASES_DIR
from .file import write_problem, write_solution

logger = logging.getLogger("petab_test_suite")


def create():
    """Create all test files."""

    case_list = os.scandir(CASES_DIR)
    case_list = sorted(f.name for f in case_list
                       if f.is_dir() and re.match(r'^\d+$', f.name))

    for case in case_list:
        case_dir = os.path.join(CASES_DIR, case)
        logger.info('# ', case, case_dir)

        sys.path.append(case_dir)
        case_module = importlib.import_module(case)
        dfs = dict()
        for df_name in ['parameter', 'condition', 'observable', 'measurement',
                        'simulation']:
            dfs[df_name] = getattr(case_module, f'{df_name}_dfs',
                                   getattr(case_module, f'{df_name}_df'))

        for format in ['sbml', 'pysb']:
            if format == 'sbml':
                model_file = case_module.model
            else:
                model_file = case_module.model.replace('.xml', '_pysb.py')

            write_problem(test_id=case_module.test_id,
                          parameter_df=dfs['parameter'],
                          condition_dfs=dfs['condition'],
                          observable_dfs=dfs['observable'],
                          measurement_dfs=dfs['measurement'],
                          model_files=model_file,
                          format_=format)

            write_solution(test_id=case_module.test_id,
                           chi2=case_module.chi2,
                           llh=case_module.llh,
                           simulation_dfs=dfs['simulation'],
                           format=format)


def clear():
    """Clear all model folders."""

    case_list = os.scandir(CASES_DIR)
    for case in case_list:
        case_dir = os.path.join(CASES_DIR, case)
        for file_ in os.scandir(case_dir):
            if file_.name.startswith('_') and not file_.is_dir():
                os.remove(file_.path)

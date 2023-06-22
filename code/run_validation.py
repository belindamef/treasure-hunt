"""
This script evaluates and visualizes beh_model recovery simulations.

Author: Belinda Fleischmann
"""

import os.path
import time
import argparse
from utilities.config import DirectoryManager, TaskConfigurator
from utilities.simulation_methods import Simulator, SimulationParameters
from utilities.modelling import BayesianModelComps
from utilities.validation_methods import Validator
import numpy as np


def get_arguments():
    """Get arguments from environment, if script is executed from command line
    or with a bash jobwrapper."""
    parser = argparse.ArgumentParser(description='Run model validation.')
    parser.add_argument('--parallel_computing', action="store_true")
    parser.add_argument('--repetition', type=int, nargs='+')
    parser.add_argument('--agent_model', type=str, nargs='+')
    parser.add_argument('--tau_value', type=float, nargs='+')
    parser.add_argument('--lambda_value', type=float, nargs='+')
    parser.add_argument('--participant', type=int, nargs='+')
    args = parser.parse_args()
    return args


def define_simulation_parameters() -> SimulationParameters:
    sim_parameters = SimulationParameters()

    if arguments.parallel_computing:
        sim_parameters.get_params_from_args(arguments)

    else:  # Define parameters for local tests, i.e. not parallel computing
        # note to myself: this overwrites default class attributes
        sim_parameters.agent_space_gen = ["A3"]
        sim_parameters.tau_space_gen = np.linspace(0.1, 2., 5)
        sim_parameters.tau_gen_space_if_fixed = [0.1]
        sim_parameters.n_participants = 10
        sim_parameters.lambda_gen_space = np.linspace(0.1, 0.9, 5)
    return sim_parameters


def decrease_total_trial_numbers(task_configuration_object: object):
    task_configuration_object.params.n_blocks = TEST_N_BLOCKS
    task_configuration_object.params.n_rounds = TEST_N_ROUNDS
    task_configuration_object.params.n_trials = TEST_N_TRIALS


def main():
    dir_mgr = DirectoryManager()
    dir_mgr.create_val_out_dir(out_dir_label=OUT_DIR_LABEL, version=VERSION_NO)

    task_config = TaskConfigurator(dir_mgr.paths).get_config(TASK_CONFIG_LABEL)
    bayesian_comps = BayesianModelComps(task_config.params).get_comps()

    sim_params = define_simulation_parameters()
    simulator = Simulator(task_config, bayesian_comps, sim_params)

    if QUICK_TEST:
        decrease_total_trial_numbers(task_config)

    validator = Validator(sim_params, simulator, dir_mgr)

    validator.start_simulation_and_estimation_routine()


if __name__ == "__main__":
    start = time.time()
    arguments = get_arguments()

    TASK_CONFIG_LABEL = "exp_msc"
    OUT_DIR_LABEL = "tests_Test"
    VERSION_NO = "1"

    QUICK_TEST = True
    TEST_N_BLOCKS = 1
    TEST_N_ROUNDS = 2
    TEST_N_TRIALS = 4

    main()
    end = time.time()
    print(f"Total time for beh_model validation: "
          f"{round((end-start), ndigits=2)} sec.")

"""
This script contains classes and methods for model validation analyses.

Author: Belinda Fleischmann
"""

from utilities.simulation_methods import Simulator, SimulationParameters
from utilities.estimation_methods import Estimator
from utilities.config import DirectoryManager
import pandas as pd
import time


class Validator:
    data_dic: dict
    estimator: Estimator = Estimator()

    def __init__(self, sim_params: SimulationParameters,
                 simulator: Simulator, dir_mgr: DirectoryManager):
        self.sim_params: SimulationParameters = sim_params
        self.simulator: Simulator = simulator
        self.dir_mgr: DirectoryManager = dir_mgr

    def init_data_dic(self):
        self.data_dic = {
            "agent": [], "participant": [],
            "tau_gen": [], "tau_mle": [],
            "lambda_gen": [], "lambda_mle": []}

        for agent in self.estimator.est_params.agent_candidate_space:
            self.data_dic[f"BIC_{agent}"] = []

    def record_data_generating_sim_params(self):
        # TODO: more elegant solution please...
        self.data_dic["agent"].extend(
            [self.simulator.sim_params.current_agent_gen
             ] * self.simulator.sim_params.n_participants)
        self.data_dic["tau_gen"].extend(
            [self.simulator.sim_params.current_tau_gen
             ] * self.simulator.sim_params.n_participants)
        self.data_dic["lambda_gen"].extend(
            [self.simulator.sim_params.current_lambda_gen
             ] * self.simulator.sim_params.n_participants)

    def record_participant_number(self):
        self.data_dic["participant"].append(self.sim_params.current_part)

    def record_tau_estimate(self, tau_estimate):
        self.data_dic["tau_mle"].append(tau_estimate)

    def record_lambda_estimate(self, lambda_estimate):
        self.data_dic["lambda_mle"].append(lambda_estimate)

    def record_bics(self, bics: dict):
        for agent in self.estimator.est_params.agent_candidate_space:
            self.data_dic[f"BIC_{agent}"].append(bics[f"BIC_{agent}"])

    def save_results(self):
        self.dir_mgr.create_agent_sub_id(self.sim_params)
        self.dir_mgr.define_val_results_filename()

        mle_df = pd.DataFrame(self.data_dic)

        with open(f"{self.dir_mgr.paths.this_sub_val_result_fn}.tsv",
                  "w", encoding="utf8") as tsv_file:
            tsv_file.write(mle_df.to_csv(sep="\t", na_rep="nan", index=False))

    def estimate_parameter_values(self):

        self.estimator.estimate_parameters(
            data=self.simulator.data,
            method="brute_force",
            candidate_agent=self.sim_params.current_agent_gen,
            task_configs=self.simulator.task_configs,
            bayesian_comps=self.simulator.bayesian_comps,
            sim_params=self.sim_params)

        mle_tau_est = self.estimator.tau_est_result_gen_agent
        mle_lambda_est = self.estimator.lambda_est_result_gen_agent

        self.record_tau_estimate(mle_tau_est)
        self.record_lambda_estimate(mle_lambda_est)

    def evaluate_model_recovery_performance(self):
        bics = self.estimator.evaluate_bic_s(est_method="brute_force",
                                             data=self.simulator.data,
                                             data_type="sim")
        self.record_bics(bics)

    def run_param_model_recovery_routine(self):
        """For each participant, simulate behavioral data, estimate parameter
        values and evaluate model recovery performance"""

        self.init_data_dic()
        self.record_data_generating_sim_params()
        self.record_participant_number()

        self.simulator.simulate_beh_data()

        start = time.time()
        self.estimate_parameter_values()
        end = time.time()
        print("time needed for ML parameter estimation with "
              f"{self.sim_params.current_agent_gen} as generating agent: "
              f"{round((end-start), ndigits=2)} sec.")

        start = time.time()
        self.evaluate_model_recovery_performance()
        end = time.time()
        print(
            "time needed for evaluatung mordel recovery performance for data",
            f" from {self.sim_params.current_agent_gen} as generating agent: ",
            f"{round((end-start), ndigits=2)} sec.")

        self.save_results()

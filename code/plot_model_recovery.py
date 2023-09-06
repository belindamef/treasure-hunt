#!/usr/bin/env python3
"""This script plots model recovery performance results: BICs"""
import math
import numpy as np
from matplotlib import pyplot
from utilities.config import DirectoryManager, DataHandler
from utilities.very_plotter_new import VeryPlotter, PlotCustomParams


def plot_model_recov_results(
        exp_label: str, vers: str, save_file: bool = True,
        plt_params: PlotCustomParams = PlotCustomParams()):
    """_summary_

    Args:
        exp_label (str): _description_
        vers (str): _description_
        save_file (bool, optional): _description_. Defaults to True.
        plt_params (PlotCustomParams, optional): _description_. Defaults to PlotCustomParams().
    """    

    # Get and Prepare data
    dir_mgr = DirectoryManager()
    dir_mgr.define_model_recov_results_path(exp_label=exp_label,
                                            version=vers)
    data_loader = DataHandler(dir_mgr.paths, exp_label=exp_label)
    all_val_results_df = data_loader.load_data_in_one_folder(
        folder_path=dir_mgr.paths.this_model_recov_results_dir
        )

    agent_gen_models = all_val_results_df.agent.unique().tolist()
    agent_gen_models.sort()

    control_gen_agents = [agent for agent in agent_gen_models if "C" in agent]
    Bayesian_gen_agents = [agent for agent in agent_gen_models if "A" in agent]

    bic_of_analizing_models = [
        col_name for col_name in all_val_results_df.columns if "BIC" in col_name]
    analyzing_models = [
        bic_model[-2:] for bic_model in bic_of_analizing_models
        ]
    group_averages_df = all_val_results_df.groupby(
        ["agent", "tau_gen", "lambda_gen"],
        dropna=False)[bic_of_analizing_models].agg(
            ["mean", "std"])

    bic_min_for_yaxis = int(math.floor(
        np.nanmin(group_averages_df.loc[:]/ 100.0)) * 100)
    bic_max_for_yaxis = int(math.ceil(
        np.nanmax(group_averages_df.loc[:]/ 100.0)) * 100)
    bic_y_ticks = np.round(np.linspace(bic_min_for_yaxis, bic_max_for_yaxis, 5),
                          decimals=2)
    pep_y_ticks = np.round(np.linspace(0, 1, 5), decimals=2)
    y_ticks = {"BIC": bic_y_ticks,
               "PEP": pep_y_ticks}

    # Prepare figure
    plotter = VeryPlotter(paths=dir_mgr.paths)
    plt = pyplot
    color_dict = plotter.get_agent_colors(control_color="grey")

    rc_params = plotter.define_run_commands()
    plt = pyplot
    plt.rcParams.update(rc_params)
    n_colums = 6
    fig, axs = plt.subplots(nrows=4, ncols=n_colums,
                            figsize=(22, 12),
                            layout="constrained")

    # Adjust axis parameters
    lambda_gen_values = np.delete(
        all_val_results_df["lambda_gen"].unique(),
        np.where(np.isnan(all_val_results_df.lambda_gen.unique())))
    lambda_gen_values.sort()

    if len(lambda_gen_values) > n_colums:
        number_of_elements_wanted = n_colums
    else:
        number_of_elements_wanted = len(lambda_gen_values)
    indices_lambda_selection = np.round(np.linspace(
        0, len(lambda_gen_values) - 1, number_of_elements_wanted)
        ).astype(int)
    lambdas_for_plot = lambda_gen_values[indices_lambda_selection]

    if any("PEP" in col_name for col_name in all_val_results_df.columns):
        measure_list = ["BIC", "PEP"]
    else: 
        measure_list = ["BIC"]


    for measure in measure_list:
# ------ Figure A: C1, C2, C3, A1, A2 --------------------------------
        row = 0
        column = 0

        for gen_agent in control_gen_agents:
            this_ax = axs[row, column]

            x_ticks = range(1, len(analyzing_models)+1)
            x_tick_labels = []
            colors = []

            j = 0
            for analyzing_model in analyzing_models:

                x_tick_labels.append(analyzing_model)

                colors.append(color_dict[analyzing_model])
                this_ax.errorbar(
                    x=j+1,
                    y=np.mean(group_averages_df.loc[gen_agent][
                            f"{measure}_{analyzing_model}", "mean"]),
                    yerr=np.mean(group_averages_df.loc[
                        gen_agent][
                            f"{measure}_{analyzing_model}", "std"]),
                    fmt=plt_params.marker_shape,
                    alpha=plt_params.transp_lvl, markersize=plt_params.marker_sz,
                    color=color_dict[analyzing_model],
                    label=analyzing_model
                    )
                j += 1

            plotter.config_axes(
                this_ax,
                title=f"{gen_agent}",
                title_color=color_dict[f"{gen_agent}"],
                y_label=f"{measure}",
                x_label="Analyzing agent",
                axix_label_size=plt_params.axis_label_fs,
                ticksize=plt_params.axis_tick_fs,
                xticks=x_ticks,
                title_font=plt_params.axis_title_fs,
                xticklabels=x_tick_labels,
                yticks=y_ticks[measure],
                ytickslabels=y_ticks[measure]
                )

            column += 1

        # ------Figure A: A1 and A2

        tau_gen_values = np.delete(  # TODO: redundant?
            all_val_results_df.tau_gen.unique(),
            np.where(np.isnan(all_val_results_df.tau_gen.unique())))

        for gen_agent in [agent for agent in Bayesian_gen_agents if agent != "A3"]:
            this_ax = axs[row, column]
            tau_gen_values = np.array(
                group_averages_df.loc[gen_agent].index.get_level_values("tau_gen")
                )

            for analyzing_model in analyzing_models:

                mean_this_analyzing_agent = group_averages_df.loc[
                    gen_agent][f"{measure}_{analyzing_model}", "mean"]

                stds = (np.mean(group_averages_df.loc[
                            gen_agent][f"{measure}_{analyzing_model}", "std"])
                        )

                this_ax.errorbar(
                    x=tau_gen_values,
                    y=mean_this_analyzing_agent,
                    yerr=stds,
                    fmt=plt_params.marker_shape,
                    alpha=plt_params.transp_lvl, markersize=plt_params.marker_sz,
                    linestyle=plt_params.err_bar_linestyle,
                    linewidth=plt_params.err_bar_linewidth,
                    color=color_dict[analyzing_model],
                    label=analyzing_model
                    )

            plotter.config_axes(
                ax=this_ax,
                title=f"{gen_agent}",
                title_font=plt_params.axis_title_fs,
                title_color=color_dict[f"{gen_agent}"],
                axix_label_size=plt_params.axis_label_fs,
                y_label=f"{measure}",
                x_label=r"$\tau$",
                xticks=plt_params.tau_ticks,
                xticklabels=plt_params.tau_ticks,
                yticks=y_ticks[measure],
                ytickslabels=y_ticks[measure],
                ticksize=plt_params.axis_tick_fs
                )

            column += 1

        this_ax.legend(loc="lower right", fontsize=plt_params.legend_fs)

    # ------ Figure B: A3-------------------------------------------------

        row += 1
        column = 0
        if "A3" in group_averages_df.index.get_level_values("agent"):
            for lambda_gen in lambdas_for_plot:
                this_ax = axs[row, column]
                tau_gen_values = np.array(
                    group_averages_df.loc[
                        "A3", :, lambda_gen].index.get_level_values("tau_gen"))

                for analyzing_model in analyzing_models:
                    
                    mean_this_analyzing_agent = group_averages_df.loc[
                        "A3", :, lambda_gen][f"{measure}_{analyzing_model}", "mean"]

                    stds = (np.mean(group_averages_df.loc[
                                "A3"][f"{measure}_{analyzing_model}", "std"])
                            )

                    this_ax.errorbar(
                        x=tau_gen_values,
                        y=mean_this_analyzing_agent,
                        yerr=stds,
                        fmt=plt_params.marker_shape,
                        alpha=plt_params.transp_lvl, markersize=plt_params.marker_sz,
                        linestyle=plt_params.err_bar_linestyle,
                        linewidth=plt_params.err_bar_linewidth,
                        color=color_dict[analyzing_model],
                        label=analyzing_model
                        )

                plotter.config_axes(
                    ax=this_ax,
                    title=r"A3 $\lambda= $" + f"{lambda_gen}",
                    title_font=plt_params.axis_title_fs,
                    title_color=color_dict["A3"],
                    axix_label_size=plt_params.axis_label_fs,
                    y_label=f"{measure}",
                    x_label=r"$\tau$",
                    xticks=plt_params.tau_ticks,
                    xticklabels=plt_params.tau_ticks,
                    yticks=y_ticks[measure],
                    ytickslabels=y_ticks[measure],
                    ticksize=plt_params.axis_tick_fs
                    )
                column += 1

    #fig.align_ylabels(axs=axs)

    # Print subject level descriptive figure
    if save_file:
        plotter.save_figure(fig=fig, figure_filename=FIGURE_FILENAME)


if __name__ == "__main__":

    EXP_LABEL = "exp_msc"
    #VERSION_NO = "test_parallel_1"
    VERSION_NO = "test_hr"
    FIGURE_FILENAME = f"figure_model_recov_{VERSION_NO}_debug"

    plot_model_recov_results(exp_label=EXP_LABEL, vers=VERSION_NO, save_file=True)

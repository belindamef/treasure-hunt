import numpy as np
import matplotlib.pyplot as plt
# from matplotlib import cm
import matplotlib.ticker as mticker
import matplotlib.gridspec as gridspec
import wesanderson
import pandas as pd
import os
import glob

from utilities.data_class import Data
from utilities.data_analyses import DescrStats
from utilities.data_analyses import GroupStats
# from utilities.plot_colormap import plot_colormap
import utilities.very_plotter as very_plotter


"""This script plots figure 1"""

# Specify task configuration
exp_label = 'main'
sim_label = 'main_bu'
dim = 5
n_blocks = 3

# Specify directories and filenames
working_dir = os.getcwd()
project_dir = os.sep.join(working_dir.split(os.sep)[:4])  # Should be Users/<{$USER}>/<{$PROJECTFOLDER}>
data_dir = os.path.join(project_dir, 'data')
results_dir = os.path.join(project_dir, 'results')
descr_stats_dir = os.path.join(results_dir, 'descr_stats')
figures_dir = os.path.join(project_dir, 'figures')

exp_data_dir = os.path.join(data_dir, 'rawdata', 'exp', f'{exp_label}')
sim_data_dir = os.path.join(data_dir, 'rawdata', 'sim', f'{exp_label}')
exp_proc_data_dir = os.path.join(data_dir, 'processed_data', 'exp', f'{exp_label}')
sim_proc_data_dir = os.path.join(data_dir, 'processed_data', 'sim', f'{exp_label}')
sim_100_proc_data_dir = os.path.join(data_dir, 'processed_data', 'sim', f'{exp_label}_sim_100')

ev_exp_fn = os.path.join(exp_proc_data_dir, 'sub-all_task-th_run-all_beh')
ev_sim_fn = os.path.join(sim_proc_data_dir, 'sub-all_task-th_run-all_beh')
ev_exp_run_fn = os.path.join(exp_proc_data_dir, 'sub-all_task-th_run-')
ev_sim_run_fn = os.path.join(sim_proc_data_dir, 'sub-all_task-th_run-')

ds_exp_fn = os.path.join(descr_stats_dir, 'exp', f'{exp_label}', 'descr_stats')
ds_sim_fn = os.path.join(descr_stats_dir, 'sim', f'{exp_label}', 'descr_stats')
ds_sim_100_fn = os.path.join(descr_stats_dir, 'sim', f'{exp_label}_sim_100', 'descr_stats')
grp_stats_exp_fn = os.path.join(descr_stats_dir, 'exp', f'{exp_label}', 'grp_lvl_stats')
grp_stats_sim_fn = os.path.join(descr_stats_dir, 'sim', f'{exp_label}', 'grp_lvl_stats')
grp_stats_sim_100_fn = os.path.join(descr_stats_dir, 'sim', f'{exp_label}_sim_100', 'grp_lvl_stats')
tw_exp_fn = os.path.join(descr_stats_dir, 'exp', f'{exp_label}', 't_wise_stats')
tw_sim_fn = os.path.join(descr_stats_dir, 'sim', f'{exp_label}', 't_wise_stats')
tw_sim_100_fn = os.path.join(descr_stats_dir, 'sim', f'{exp_label}_sim_100', 't_wise_stats')

# ----------------------------------------------------------
#       Load data
# ----------------------------------------------------------

# ------Overall data---------------------
# Experimental data
exp_ev_all_subs_df = pd.read_pickle(f'{ev_exp_fn}.pkl')

# Simulation 100 data
grp_lvl_stats_sim_100 = pd.read_pickle(f'{grp_stats_sim_100_fn}.pkl')
grp_lvl_stats_sim_100_A = grp_lvl_stats_sim_100[grp_lvl_stats_sim_100['sub_id'].isin(['Agent A1', 'Agent A2', 'Agent A3'])]
grp_lvl_stats_sim_100_C = grp_lvl_stats_sim_100[grp_lvl_stats_sim_100['sub_id'].isin(['Agent C1', 'Agent C2', 'Agent C3'])]
tw_sim_100_aw = {} # trialwise stats each agent over all blocks
for agent in ['A1', 'A2', 'A3']:
    tw_sim_100_aw[agent] = pd.read_pickle(f'{tw_sim_100_fn}_agent-Agent {agent}.pkl')

# ------Blockwise data------------------
# Experimental data
descr_stats_exp_bw = {}
tw_exp_bw = {}
descr_stats_all_subs_bw_exp = {}
grp_lvl_stats_bw_exp = {}

# Simulation main data
ev_sim_bw = {}
grp_lvl_stats_bw_sim = {}
grp_lvl_stats_bw_sim_A = {}
grp_lvl_stats_bw_sim_C = {}

for block_ in range(n_blocks):
    this_block = block_ + 1

    # Experimental data
    descr_stats_exp_bw[this_block] = pd.read_pickle(f'{ds_exp_fn}_run-{this_block:02d}.pkl')
    tw_exp_bw[this_block] = pd.read_pickle(f'{tw_exp_fn}_run-{this_block:02d}.pkl')
    descr_stats_all_subs_bw_exp[this_block] = pd.read_pickle(f'{ds_exp_fn}_run-{this_block:02d}.pkl')
    grp_lvl_stats_bw_exp_both_rows = pd.read_pickle(f'{grp_stats_exp_fn}_run-{this_block:02d}.pkl')
    grp_lvl_stats_bw_exp[this_block] = grp_lvl_stats_bw_exp_both_rows[grp_lvl_stats_bw_exp_both_rows['sub_id'].isin(['experiment'])]

    # Simulation main data
    ev_sim_bw[this_block] = pd.read_pickle(f'{ev_sim_run_fn}{this_block:02d}_beh.pkl')
    grp_lvl_stats_bw_sim[this_block] = pd.read_pickle(f'{grp_stats_sim_fn}_run-{this_block:02d}.pkl')
    grp_lvl_stats_bw_sim_A[this_block] = grp_lvl_stats_bw_sim[this_block][
        grp_lvl_stats_bw_sim[this_block]['sub_id'].isin(['Agent A1', 'Agent A2', 'Agent A3'])]
    grp_lvl_stats_bw_sim_C[this_block] = grp_lvl_stats_bw_sim[this_block][
        grp_lvl_stats_bw_sim[this_block]['sub_id'].isin(['Agent C1', 'Agent C2', 'Agent C3'])]

# ----------------------------------------------------------
#       Prepare figure
# ----------------------------------------------------------
# Create general figure components
sub_label_beh = [s_dir[(s_dir.find('sub-') + 4):] for s_dir in glob.glob(exp_data_dir + '/sub-*')]
sub_label_sim = [s_dir[(s_dir.find('sub-') + 4):] for s_dir in glob.glob(sim_data_dir + '/sub-*')]
sub_label_beh.sort()
sub_label_sim.sort()

# Extract task configuration-specific model components
n_blocks = np.max(exp_ev_all_subs_df['block'])
n_rounds = np.max(exp_ev_all_subs_df['round'])
n_trials = np.max(exp_ev_all_subs_df['trial']) - 1
n_tr_max = int(n_blocks * n_rounds)
n_tr_b = n_rounds

# Initialize figure
fig_fn = os.path.join(figures_dir, 'figure_1.png')
plt, col_exp, col_A, col_C = very_plotter.get_fig_template(plt)
ax = {}
fig = plt.figure(figsize=(16, 10))
gs = gridspec.GridSpec(4, 10)
bar_width = 0.6
half_bar_width = bar_width / 3
s = 14
agent_colors = col_A + col_C  # Specify agent colors

# fig, big_axes = plt.subplots(figsize=(16, 10), nrows=4, ncols=1, sharey=True)
#
# big_axes[0].set_title("Experimental task configurations", fontsize=16)
# big_axes[0].tick_params(labelcolor=(1.,1.,1., 0.0), top='off', bottom='off', left='off', right='off')
# big_axes[0]._frameon = False

# for row, big_ax in enumerate(big_axes, start=1):
#     big_ax.set_title("Subplot row %s \n" % row, fontsize=16)
#
#     # Turn off axis lines and ticks of the big subplot
#     # obs alpha is 0 in RGBA string!
#     big_ax.tick_params(labelcolor=(1.,1.,1., 0.0), top='off', bottom='off', left='off', right='off')
#     # removes the white frame
#     big_ax._frameon = False

# -----------------------------------------------------------------
#       Blockwise plots Experimental and main Simulation data
# -----------------------------------------------------------------
# ------Treasure discovery----------------------------------------???
for block_ in range(n_blocks):
    ax[block_] = plt.subplot(gs[block_, 0:2])
    this_ax = ax[block_]
    block = block_ + 1

    # Experimental group
    very_plotter.plot_bar(ax=this_ax, x=0,  height=grp_lvl_stats_bw_exp[block]['mean_tr_over_subs'],
                          colors=col_exp[0],
                          yerr=grp_lvl_stats_bw_exp[block]['std_tr_over_subs'])
    very_plotter.plot_bar_scatter(this_ax, descr_stats_exp_bw[block]['n_tr'], color=col_exp[1], bar_width=bar_width)

    # Bayesian agents
    very_plotter.plot_bar(ax=this_ax, x=[1, 1.5, 2], height=grp_lvl_stats_bw_sim_A[block]['mean_tr_over_subs'].values,
                          colors=col_A, bar_width=half_bar_width)

    # Control agents
    very_plotter.plot_bar(ax=this_ax, x=[2.5, 3, 3.5], height=grp_lvl_stats_bw_sim_C[block]['mean_tr_over_subs'].values,
                          colors=col_C, bar_width=half_bar_width,
                          yerr=grp_lvl_stats_bw_sim_C[block]['std_tr_over_subs'], errorbar_size=3)

    # Configure axis
    very_plotter.config_axes(this_ax,
                             y_label="Number of Treasures", y_lim=[0, n_tr_b],
                             xticks=[0, 1, 1.5, 2, 2.5, 3, 3.5],
                             xticklabels=['Part.', 'A1', 'A2', 'A3', 'C1', 'C2', 'C3'],
                             yticks=np.linspace(0, n_tr_b, 6),
                             #ytickslabels=np.around(np.linspace(0, n_tr_b, 6), 2))
                             ytickslabels=[0, 2, 4, 6, 8, 10])

# Add letter and title
very_plotter.config_axes(ax[0], title="Task performance\n " + r"\textit{exp. run 1}")
very_plotter.config_axes(ax[1], title=" \n " + r"\textit{exp. run 2}")
very_plotter.config_axes(ax[2], title=" \n " + r"\textit{exp. run 3}")
#very_plotter.add_letters({0: ax[0]})
ax[0].text(-0.15, 1.25, 'a',
                   transform=ax[0].transAxes,
                   size=32, weight='bold')



# ------Average choice rates--------------------------------------------
for block in range(n_blocks):
    ax[block] = plt.subplot(gs[block, 2:4])
    this_ax = ax[block]
    block += 1

    # Experimental Group
    very_plotter.plot_bar(ax=this_ax, x=0,  height=grp_lvl_stats_bw_exp[block]['mean_drills_over_subs'],
                          colors=col_exp[0],
                          yerr=grp_lvl_stats_bw_exp[block]['std_drills_over_subs'])
    very_plotter.plot_bar_scatter(this_ax, descr_stats_all_subs_bw_exp[block]['mean_drills'], color=col_exp[1],
                                  bar_width=bar_width)

    # Bayesian agents
    very_plotter.plot_bar(ax=this_ax, x=[1, 1.5, 2],
                          height=grp_lvl_stats_bw_sim_A[block]['mean_drills_over_subs'].values,
                          colors=col_A, bar_width=half_bar_width)
    # Control agents
    very_plotter.plot_bar(ax=this_ax, x=[2.5, 3, 3.5],
                          height=grp_lvl_stats_bw_sim_C[block]['mean_drills_over_subs'].values,
                          colors=col_C, bar_width=half_bar_width,
                          yerr=grp_lvl_stats_bw_sim_C[block]['std_drills_over_subs'].values, errorbar_size=3)

    # Configure axis
    very_plotter.config_axes(this_ax,
                             y_label="\%", y_lim=[0, 1],
                             xticks=[0, 1, 1.5, 2, 2.5, 3, 3.5],
                             xticklabels=['Part.', 'A1', 'A2', 'A3', 'C1', 'C2', 'C3'],
                             yticks=np.linspace(0, 1, 6),
                             #ytickslabels=int(np.linspace(0, 100, 6), 0))
                             #ytickslabels=np.linspace(0, 100, 6))
                             ytickslabels=[0, 20, 40, 60, 80, 100])
    #this_ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))

# Add letter and title
very_plotter.config_axes(ax[0], title="Informative choice rates\n " + r"\textit{exp. run 1}")
very_plotter.config_axes(ax[1], title="\n " + r"\textit{exp. run 2}")
very_plotter.config_axes(ax[2], title="\n " + r"\textit{exp. run 3}")
#very_plotter.add_letters({1: ax[0]})
ax[0].text(-0.25, 1.25, 'b',
                   transform=ax[0].transAxes,
                   size=32, weight='bold')

# ------Trial-by-trial/round-wise average choice rates--------------------------------------------
for block in range(n_blocks):
    block += 1
    ax[block] = plt.subplot(gs[block - 1, 4:10])

    # Experimental group trial-by-trial choices
    this_ax = ax[block]
    x = tw_exp_bw[block].trial.values
    y = tw_exp_bw[block].mean_drill.values
    this_ax.scatter(x, y, alpha=0.2, s=s, color=col_exp[1], clip_on=False,
                    label="Participants' group \n trial-by-trial choices") #facecolors='none', edgecolors=col_exp[1])

    # Experimental group round-by-round choices
    tw_exp_run_grpby_round = tw_exp_bw[block].groupby('round')
    x = [((round_ * 12) - 5.5) for round_, tw_exp_run_thisround in tw_exp_run_grpby_round]
    y = [np.mean(tw_exp_run_thisround['mean_drill']) for round_, tw_exp_run_thisround in tw_exp_run_grpby_round]
    e = [np.std(tw_exp_run_thisround['mean_drill']) for round_, tw_exp_run_thisround in tw_exp_run_grpby_round]
    this_ax.errorbar(x, y, alpha=0.7, markersize=4, color=col_exp[1], fmt='o', linestyle='-', linewidth=0.8,
                     label="Participants' group \n round average", clip_on=False,
                     yerr=e)

    # Bayesian agents
    i = 0
    for agent, ev_thisagent_df in ev_sim_bw[block].groupby('sub_id'):
        if 'C' in agent:  # Scip control agents
            continue
        ev_thisagent_gbround = ev_thisagent_df.groupby('round')
        vlines = [(round_ * 12 - 11) for round_, ev_df in ev_thisagent_gbround]
        x = [((round_ * 12) - 5.5) for round_, ev_df in ev_thisagent_gbround]
        y = [np.mean(ev_df['action_type_num']) for round_, ev_df in ev_thisagent_gbround]
        e = [np.std(ev_df['action_type_num']) for round_, ev_df in ev_thisagent_gbround]
        this_ax.errorbar(x, y, alpha=0.7, markersize=4, color=agent_colors[i], fmt='o', linestyle='-',
                         linewidth=0.8, clip_on=False, label=f"{agent}'s round average")
        i += 1

    # Configure axis
    this_ax.vlines(vlines, colors=[.9, .9, .9], linewidth=.4, ymin=0, ymax=1)  # Add vertical lines
    vlines.append(120)  # Add last boundary, to have 12 xticklabels
    very_plotter.config_axes(this_ax,
                             x_lim=[0, 120], x_label='Trial', xticks=vlines,
                             xticklabels=np.around((np.linspace(1, 120, 11))).astype(int),
                             y_label="\%", y_lim=[0, 1],
                             yticks=np.linspace(0, 1.0, 6),
                             #ytickslabels=np.around(np.linspace(0, 1.0, 6), 2))
                             ytickslabels=[0, 20, 40, 60, 80, 100])

# Add letter, title and legend
# ax[2].legend(loc='upper right', fontsize=13)
ax[1].legend(bbox_to_anchor=(1.30, 1), loc='upper right', borderaxespad=0, fontsize=13)

very_plotter.config_axes(ax[1], title="Trial-by-trial/roundwise informative choice rates\n " + r"\textit{exp. run 1}")
very_plotter.config_axes(ax[2], title="\n " + r"\textit{exp. run 2}")
very_plotter.config_axes(ax[3], title="\n " + r"\textit{exp. run 3}")
# Add letter
#very_plotter.add_letters({2: ax[1]})
ax[1].text(-0.01, 1.25, 'c',
                   transform=ax[1].transAxes,
                   size=32, weight='bold')

# -----------------------------------------------------------------
#       Simulation 100 data plots
# -----------------------------------------------------------------
# ------Treasure discovery----------------------------------------???
ax[4] = plt.subplot(gs[3, 0:2])
this_ax = ax[4]
block += 1

# Bayesian agents
very_plotter.plot_bar(ax=this_ax, x=[1, 1.5, 2], height=grp_lvl_stats_sim_100_A['mean_tr_over_b'].values,
                      yerr=grp_lvl_stats_sim_100_A['std_tr_over_b'], errorbar_size=3,
                      colors=col_A, bar_width=half_bar_width)

# Control agents
very_plotter.plot_bar(ax=this_ax, x=[2.5, 3, 3.5], height=grp_lvl_stats_sim_100_C['mean_tr_over_b'].values,
                      yerr=grp_lvl_stats_sim_100_C['std_tr_over_b'], colors=col_C, bar_width=half_bar_width,
                      errorbar_size=3)

# Configure axis
very_plotter.config_axes(this_ax,
                         title="Task performance\n " + r"\textit{sim 100}",
                         #title=r"\textit{100 task configurations}",
                         y_label="Number of Treasures", y_lim=[0, n_tr_b],
                         xticks=[1, 1.5, 2, 2.5, 3, 3.5],
                         xticklabels=['A1', 'A2', 'A3', 'C1', 'C2', 'C3'],
                         yticks=np.linspace(0, n_tr_b, 6),
                         #ytickslabels=np.around(np.linspace(0, n_tr_b, 6), 2))
                         ytickslabels=[0, 2, 4, 6, 8, 10])

# Add letter
#very_plotter.add_letters({3: ax[4]})
ax[4].text(-0.15, 1.25, 'd',
                   transform=ax[4].transAxes,
                   size=32, weight='bold')

# ------Average choice rates--------------------------------------------
ax[5] = plt.subplot(gs[3, 2:4])
this_ax = ax[5]

# Bayesian agents
very_plotter.plot_bar(ax=this_ax, x=[1, 1.5, 2], height=grp_lvl_stats_sim_100_A['mean_drills_over_b'].values,
                      colors=col_A, bar_width=half_bar_width,
                      yerr=grp_lvl_stats_sim_100_A['std_drills_over_b'], errorbar_size=3)

# Control agents
very_plotter.plot_bar(ax=this_ax, x=[2.5, 3, 3.5], height=grp_lvl_stats_sim_100_C['mean_drills_over_b'].values,
                     colors=col_C, bar_width=half_bar_width,
                     yerr=grp_lvl_stats_sim_100_C['std_drills_over_b'].values, errorbar_size=3)

# Configure axis
very_plotter.config_axes(this_ax,
                         title="Informative choice rates\n " + r"\textit{sim 100}",
                         #title=r"\textit{100 task configurations}",
                         y_label="\%", y_lim=[0, 1],
                         xticks=[1, 1.5, 2, 2.5, 3, 3.5],
                         xticklabels=['A1', 'A2', 'A3', 'C1', 'C2', 'C3'],
                         yticks=np.linspace(0, 1.0, 6),
                         #ytickslabels=np.around(np.linspace(0, 1.0, 6), 2))
                         ytickslabels=[0, 20, 40, 60, 80, 100])

# Roundwise action choices
s = 14
ax[6] = plt.subplot(gs[3, 4:10])
this_ax = ax[6]
x = tw_exp_bw[1].trial.values

# ------Trial-by-trial/round-wise average choice rates--------------------------------------------
i = 0
for agent, agent_tw_df in tw_sim_100_aw.items():

    ev_thisagent_gbround = agent_tw_df.groupby('round')
    vlines = [(round_ * 12 - 11) for round_, ev_df in ev_thisagent_gbround]
    x = [((round_ * 12) - 5.5) for round_, ev_df in ev_thisagent_gbround]
    y = [np.nanmean(ev_df['p_drills']) for round_, ev_df in ev_thisagent_gbround]
    e = [np.nanstd(ev_df['p_drills']) for round_, ev_df in ev_thisagent_gbround]
    this_ax.errorbar(x, y, alpha=0.7, markersize=4, color=agent_colors[i], fmt='o', linestyle='-',
                     linewidth=0.8, clip_on=False, label=f"{agent} round average", yerr=e)
    this_ax.vlines(vlines, colors=[.9, .9, .9], linewidth=.4, ymin=0, ymax=1)
    i += 1

# Configure axis
this_ax.vlines(vlines, colors=[.9, .9, .9], linewidth=.4, ymin=0, ymax=1)  # Add vertical lines
vlines.append(120)  # Add last boundary, to have 12 xticklabels
very_plotter.config_axes(this_ax,
                         title="Roundwise informative choice rates\n " + r"\textit{sim 100}",
                         #title=r"\textit{100 task configurations}",
                         x_lim=[0, 120], x_label='Trial', xticks=vlines,
                         xticklabels=np.around((np.linspace(1, 120, 11))).astype(int),
                         y_label="\%", y_lim=[0, 1],
                         yticks=np.linspace(0, 1.0, 6),
                         #ytickslabels=np.around(np.linspace(0, 1.0, 6), 2))
                         ytickslabels=[0, 20, 40, 60, 80, 100])

#this_ax.legend(loc='center right', fontsize=11)

# Print subject level descriptive figure
fig.tight_layout()
fig.savefig(fig_fn, dpi=200, format='png')

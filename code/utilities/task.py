"""_This module contains the treasure hunt task class to simulate agent
task interaction."""
import os
import json
import numpy as np
from utilities.config import TaskConfigurator, TaskDesignParameters
from .config import Paths


class Task:
    """A class used to represent the treasure hunt task

    A task object can interact with an agent object within an
    agent-based behavioral modelling framework.
    """

    def __init__(self, task_configs):
        """A class to represent the tresaure hunt task

        Args:
            task_configs (TaskConfigurator): configuration e.g. hiding spots,
                treasure location, starting nodes etc
        """

        self.task_configs: TaskConfigurator = task_configs
        self.task_params = TaskDesignParameters()

        self.current_trial: int = 0
        self.current_round: int = 0
        self.moves: int = self.task_configs.params.n_trials

        # Initialize task beh_model components
        self.s1_t: int = -999
        self.s2_t = np.full(self.task_params.n_nodes, 0)
        self.s3_c = np.full(1, np.nan)
        self.s4_b = np.full(self.task_params.n_nodes, 0)
        self.a_set = np.array(
            [0, -self.task_params.dim, 1, self.task_params.dim, -1])
        self.o_t = np.full(1, np.nan)

        # Initialize variables for computations
        self.r_t = 0  # treasure discovery at s1 initial value: 0
        self.hides_loc = np.full(  # hiding spots of current block/task
            self.task_params.n_hides, np.nan)
        self.n_black = self.task_params.n_nodes
        self.n_blue = 0
        self.n_grey = 0
        self.drill_finding = np.nan
        self.tr_found_on_blue = np.nan

        # Get the shortest distances between two nodes from json or evaluate
        # save to json if not existent
        # ---------------------------------------------------------------------
        # Initialize dictionary with the shortest distances
        self.shortest_dist_dic = {}

        # Specify path for shortest_distances storage file
        paths = Paths()
        short_dist_fn = os.path.join(
            paths.code, 'utilities',
            f'shortest_dist_dim-{self.task_params.dim}.json')
        # Read in json file as dic if existent for given dimensionality
        if os.path.exists(short_dist_fn):
            with open(short_dist_fn, encoding="utf8") as json_file:
                self.shortest_dist_dic = json.load(json_file)
        # Create new json file if not yet existent and
        else:
            self.eval_shortest_distances()
            with open(short_dist_fn, 'w', encoding="utf8") as json_file:
                json.dump(self.shortest_dist_dic, json_file, indent=4)

    def eval_shortest_distances(self):
        """Evaluate the shortest distance between all nodes in grid world with
        dimension dim given all available actions in a_set.
        The shortest path is expressed in numbers of steps needed to
        reach the end node when standing on a given start node
        """
        # ------Initialize variables / objects--------------------------------
        n_nodes = self.task_params.n_nodes  # number of nodes in the graph
        dim = self.task_params.dim  # dimension of the grid world
        moves = self.a_set[:4]  # possible moves / actions

        # ------Create adjacency matrix---------------------------------------
        adj_matrix = []  # Initialize adjacency matrix
        # Iterate over all fields and create row with ones for adjacent fields
        for i in range(n_nodes):
            row = np.full(n_nodes, 0)  # Initialize row with all zeros
            for move in moves:
                if ((i + move) >= 0) and ((i + move) < n_nodes):
                    if ((i % dim != 0) and move == -1) or \
                            ((((i + 1) % dim) != 0) and (move == 1)) or \
                            (move == self.task_params.dim
                             or move == -self.task_params.dim):
                        row[i + move] = 1
            adj_matrix.append(list(row))

        # ------Create adjacency list (dictionary)----------------------------
        adj_list = {}  # Initialize adjacency dictionary
        # Iterate over all fields and create dict. entry with adjacent fields
        for i in range(n_nodes):
            row_list = []
            for move in moves:
                if ((i + move) >= 0) and ((i + move) < n_nodes):
                    if ((i % dim != 0) and move == -1) or \
                            ((((i + 1) % dim) != 0) and (move == 1)) or \
                            (move in [self.task_params.dim,
                                      -self.task_params.dim]):
                        row_list.append(i + move)
                        row_list.sort()
            adj_list.update({i: row_list})

        # -------Iterate through starting nodes:-------
        for start_node in range(n_nodes):

            # ------Iterate through ending nodes:------
            for end_node in range(n_nodes):

                # Return zero if start_node equals end_node
                if start_node == end_node:
                    self.shortest_dist_dic[f'{start_node}_to_{end_node}'] = 0
                    self.shortest_dist_dic[f'{end_node}_to_{start_node}'] = 0

                else:
                    # Keep track of all visited nodes of a graph
                    explored = []
                    # keep track of all the paths to be checked
                    queue = [[start_node]]

                    # Keep looping until queue is empty
                    while queue:
                        # Pop the first path from the queue
                        path = queue.pop(0)
                        # Get the last node from path
                        node = path[-1]

                        if node not in explored:
                            neighbours = adj_list[node]

                            # Go through all neighbouring nodes, construct new
                            # path and push into queue
                            for neighbour in neighbours:
                                new_path = list(path)
                                new_path.append(neighbour)
                                queue.append(new_path)

                                # Return path if neighbour is end node
                                if neighbour == end_node:

                                    shortest_path = new_path
                                    shortest_distance = len(shortest_path)-1

                                    # Add the shortest path to dictionary
                                    self.shortest_dist_dic[
                                        f'{start_node}_to_{end_node}'
                                    ] = shortest_distance
                                    self.shortest_dist_dic[
                                        f'{end_node}_to_{start_node}'
                                    ] = shortest_distance
                                    queue = []
                                    break

                            # Mark node as explored
                            explored.append(node)

    def eval_s_4(self):
        """Evaluate s_4 values according to hides_loc"""
        for node in self.hides_loc:
            self.s4_b[node] = 1

    def start_new_block(self, block_number):
        """Start new block with new task_configuration

        Parameters
        ----------
        task_config : TaskConfigurator
        """
        self.hides_loc = self.task_configs.states["hides"][block_number]
        self.eval_s_4()

    def start_new_round(self, block_number, round_number: int):
        """Fetch configuration-specific initial task states and reset
        dynamic states to initial values for a new round"""
        self.current_round = round_number
        self.moves = self.task_configs.params.n_trials
        self.s1_t = self.task_configs.states["s_1"][block_number, round_number]
        self.s3_c = self.task_configs.states["s_3"][block_number, round_number]
        self.r_t = 0  # reward
        self.tr_found_on_blue = np.nan

    def start_new_trial(self, current_trial: int):
        """Reset dynamic states to initial values for a new trial"""
        self.current_trial = current_trial
        self.moves -= 1
        self.drill_finding = np.nan

    def return_observation(self):
        """Return observation, i.e. each node current status (color) and
        treasure disc (yes/no). This function maps action, reward and states
        s3 and s4 onto observation o_t, as specified in g
        """
        # If node color black and no treasure
        if (self.s2_t[self.s1_t] == 0) and (self.r_t == 0):
            self.o_t = 0

        # If node color = grey (always no treasure found)
        elif self.s2_t[self.s1_t] == 1:
            self.o_t = 1

        # If node color = blue and no treasure
        elif (self.s2_t[self.s1_t] == 2) and (self.r_t == 0):
            self.o_t = 2

        # If treasure found
        elif self.r_t == 1:
            self.o_t = 3

    def perform_state_transition_f(self, action_t):
        """Perform the state transition function f. """
        # Move to new position (transition s_1)
        self.s1_t += int(action_t)

        # After informative actions
        if action_t == 0:

            # Change node colors (transition s_2)
            if self.s4_b[self.s1_t] == 0:  # If s_1 not hiding spot
                if self.s2_t[self.s1_t] == 0:  # If node is (was) black
                    self.drill_finding = 0
                else:
                    # Drill finding = 3, if drilled on unveiled spot
                    # (i.e. not black)
                    self.drill_finding = 3
                    # Change color to grey (not a hiding spot)
                self.s2_t[self.s1_t] = 1
            elif self.s4_b[self.s1_t] == 1:  # Elif s_1 is hiding spot
                if self.s2_t[self.s1_t] == 0:  # If node is (was) black
                    self.drill_finding = 1
                else:
                    # Drill finding = 3, if drilled on unveiled spot
                    # (i.e. not black)
                    self.drill_finding = 3
                self.s2_t[self.s1_t] = 2  # Change color to blue (hiding spot)

    def eval_whether_treasure(self):
        """Evaluate whether new current position is the treasure location"""
        if self.s1_t == self.s3_c:  # if s1 equals treasure location
            self.r_t = 1

            # Evaluate whether found on hide
            if self.s2_t[self.s1_t] == 2:
                self.tr_found_on_blue = 1
            elif self.s2_t[self.s1_t] == 0:
                self.tr_found_on_blue = 0
        else:
            self.r_t = 0

    def eval_action(self, action_t):
        """Evaluate beh_model action and update affected task states"""

        self.perform_state_transition_f(action_t)

        # If participant decides to take a step
        # -----------------------------------------------------
        if action_t != 0:

            # Evaluate whether new position is treasure location
            self.eval_whether_treasure()

        # If participant decides to drill (a == 0)
        # -----------------------------------------------------
        else:

            # Update number of node colors
            self.n_black = np.count_nonzero(self.s2_t == 0)
            self.n_grey = np.count_nonzero(self.s2_t == 1)
            self.n_blue = np.count_nonzero(self.s2_t == 2)

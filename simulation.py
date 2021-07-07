import numpy as np
import pandas as pd
import random
timepoint_num = 101


def get_next_state(current_labels, nodes, rules, graph_as_edgelist, states):
    fastes_firing_time = 10000000.0  # dummy
    firing_rule = None
    firing_node = None
    firing_edge = None

    # iterate over nodes
    for node in nodes:
        current_state = current_labels[node]
        for rule in rules:
            if 'tuple' in str(type(rule[0])):
                # is contact rule
                continue
            if current_state == rule[0]:
                current_fireing_time = np.random.exponential(1.0 / rule[2])
                if current_fireing_time < fastes_firing_time:
                    fastes_firing_time = current_fireing_time
                    firing_rule = rule
                    firing_node = node
                    firing_edge = None

    # iterate over edges:
    for edge in graph_as_edgelist:
        node1, node2 = edge
        current_state1 = current_labels[node1]
        current_state2 = current_labels[node2]
        for rule in rules:
            if 'str' in str(type(rule[0])):
                # is spont. rule
                continue
            if (current_state1 == rule[0][0] and current_state2 == rule[0][1]) or (
                    current_state2 == rule[0][0] and current_state1 == rule[0][1]):
                current_fireing_time = np.random.exponential(1.0 / rule[2])
                if current_fireing_time < fastes_firing_time:
                    fastes_firing_time = current_fireing_time
                    firing_rule = rule
                    firing_node = None
                    firing_edge = edge

    if firing_rule is None:
        # no rule could fire
        return None, fastes_firing_time  # would happen anyway but still

    # apply rule
    new_labels = list(current_labels)  # copy

    if firing_node is not None:
        new_labels[firing_node] = firing_rule[1]
        return new_labels, fastes_firing_time

    assert (firing_edge is not None)
    change_node1 = firing_edge[0]
    change_node2 = firing_edge[1]
    # we have to check which node changes in which direction
    if new_labels[change_node1] == firing_rule[0][0] and new_labels[change_node2] == firing_rule[0][1]:
        new_labels[change_node1] = firing_rule[1][0]
        new_labels[change_node2] = firing_rule[1][1]
    else:
        new_labels[change_node1] = firing_rule[1][1]
        new_labels[change_node2] = firing_rule[1][0]

    return new_labels, fastes_firing_time


def count_states(current_labels, states):
    counter = [0 for _ in states]
    for label in current_labels:
        index = states.index(label)
        counter[index] += 1
    return counter



def run_simulation(G, states, rules, init, horizon):
    nodes = G.nodes()
    timepoints_samples = np.linspace(0.0, horizon, timepoint_num)
    timepoints_samples_static = np.linspace(0.0, horizon, timepoint_num)

    initial_labels = list()
    for s in states:
        initial_labels += [s]*init[s]
    random.shuffle(initial_labels)
    current_labels = initial_labels
    global_clock = 0.0
    labels = list()
    timepoints = list()
    state_counts = list()
    graph_as_edgelist = list(G.edges())


    # simulate
    while len(timepoints_samples) > 0:
        new_labels, time_passed = get_next_state(current_labels, nodes, rules, graph_as_edgelist, states)
        global_clock += time_passed
        while len(timepoints_samples) > 0 and global_clock > timepoints_samples[0]:
            labels.append(list(current_labels))
            state_counts.append(count_states(current_labels, states))
            timepoints_samples = timepoints_samples[1:]
        current_labels = new_labels


    print(random.random())

    df = dict()
    for i, s in enumerate(states):
        df[s] = [s[i] for s in state_counts]
    df['time'] = timepoints_samples_static
    df = pd.DataFrame.from_dict(df)
    df.set_index('time', inplace=True)
    return df, labels
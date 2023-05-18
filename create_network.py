import math
import networkx as nx
import json
from itertools import combinations
import random


def read_file(label):
    with open(label, 'r') as file:
        data = json.load(file)
    return data


def construct_network(this_parameterization, number_of_nodes):
    # print('********\nBuilding non-sharded network.. HOLD..')
    constructed_network, connected = create_selected_network_type(this_parameterization, number_of_nodes)
    # print('connected?: ' + str(connected))
    # print('[SUCCESS] Network is built')
    # print(constructed_network.name)
    return constructed_network


def create_selected_network_type(this_parameterization, number_of_nodes):
    constructed_network = None
    connected = False
    target_number_of_adversary_nodes = math.floor(number_of_nodes * this_parameterization.actual_adversary_fraction)
    while not connected:
        if this_parameterization.network_model == 1:
            constructed_network = construct_ER_network(this_parameterization, number_of_nodes)
        if this_parameterization.network_model == 2:
            constructed_network = construct_BA_network(this_parameterization, number_of_nodes)
        connected = nx.is_connected(constructed_network)
    final_network = initiate_adversary_status(constructed_network, number_of_nodes, target_number_of_adversary_nodes)
    return final_network, connected


def construct_ER_network(this_parameterization, number_of_nodes):
    network = nx.Graph()
    network.name = 'Erdös – Rényi(ER)'
    for i in range(number_of_nodes):
        network.add_node(i)
        network.nodes[i]['shard'] = None
    for u, v in combinations(network, 2):
        if random.random() < float(this_parameterization.parameter):
            if u != v:
                network.add_edge(u, v, weight=random.randint(this_parameterization.min_edge_weight, this_parameterization.max_edge_weight))
    return network


def construct_BA_network(this_parameterization, number_of_nodes):
    network = nx.barabasi_albert_graph(number_of_nodes, int(this_parameterization.parameter))
    network.name = 'Barabási – Albert(BA)'
    for u, v in combinations(network, 2):
        if network.has_edge(u, v) and 'weight' not in network.edges[u, v]:
            network.edges[u, v]['weight'] = random.randint(this_parameterization.min_edge_weight, this_parameterization.max_edge_weight)
    return network


def initiate_adversary_status(network, number_of_nodes, target_number_of_adversary_nodes):
    edges = sorted(network.edges(data=True), key=lambda t: t[2].get('weight', 1))
    index_of_edge = 0
    processed_nodes = set()
    while len(processed_nodes) < target_number_of_adversary_nodes:
        node_1 = edges[index_of_edge][0]
        node_2 = edges[index_of_edge][1]
        network.nodes[node_1]['is_adversary'] = True
        network.nodes[node_2]['is_adversary'] = True
        processed_nodes.add(node_1)
        processed_nodes.add(node_2)
        index_of_edge += 1
    for i in range(number_of_nodes):
        if i not in processed_nodes:
            network.nodes[i]['is_adversary'] = False
    return network

import copy
import hashlib
from itertools import combinations
import random
from math import floor
import networkx as nx
import shard_network
import test_diameter


def fitness(list_of_lists_shard, parameterizationdata, non_sharded_network, dict_of_shortest_paths):
    intra_shard_weight_importance = parameterizationdata.intra_shard_weight_importance
    inter_shard_cost = 0
    intra_shard_cost = test_diameter.get_diameters_of_shards(list_of_lists_shard, dict_of_shortest_paths)
    inter_shard_bridge_counter = 0
    for (u, v) in non_sharded_network.edges:
        for shard in list_of_lists_shard:
            if u in shard and v not in shard:
                inter_shard_cost += non_sharded_network.edges[u, v]["weight"]
                inter_shard_bridge_counter += 1
                break
    avg_inter_shard_bridge_weight = inter_shard_cost / inter_shard_bridge_counter
    tot_cost = intra_shard_weight_importance * intra_shard_cost + (1 - intra_shard_weight_importance) * avg_inter_shard_bridge_weight
    return tot_cost, list_of_lists_shard


def mutation(list_of_lists_shard, parameterization, full_network):
    mutated_shards = []
    min_num_nodes_per_shard = parameterization.min_num_nodes_per_shard
    percentage_of_nodes_to_be_mutated = parameterization.percentage_of_nodes_to_be_mutated
    # iterations = floor(num_shards / 2)
    number_of_nodes_to_be_mutated = floor(min_num_nodes_per_shard * percentage_of_nodes_to_be_mutated)
    if number_of_nodes_to_be_mutated < 1:
        number_of_nodes_to_be_mutated = 1
    for it in range(0, len(list_of_lists_shard), 2):
        original_shard1 = copy.deepcopy(list_of_lists_shard[it])
        try:
            original_shard2 = copy.deepcopy(list_of_lists_shard[it + 1])
            for i in range(len(full_network.nodes)):
                elements_to_be_exchanged_from_shard_1 = random.sample(original_shard1, number_of_nodes_to_be_mutated)
                elements_to_be_exchanged_from_shard_2 = random.sample(original_shard2, number_of_nodes_to_be_mutated)
                temp_shard_1 = copy.deepcopy(original_shard1)
                temp_shard_2 = copy.deepcopy(original_shard2)
                temp_shard_1.extend(elements_to_be_exchanged_from_shard_2)
                temp_shard_2.extend(elements_to_be_exchanged_from_shard_1)
                for e in elements_to_be_exchanged_from_shard_1:
                    temp_shard_1.remove(e)
                    temp_shard_1 = sorted(temp_shard_1)
                for e in elements_to_be_exchanged_from_shard_2:
                    temp_shard_2.remove(e)
                    temp_shard_2 = sorted(temp_shard_2)
                if (check_if_subgraph_connected(full_network, temp_shard_1)) and (
                check_if_subgraph_connected(full_network, temp_shard_2)):
                    mutated_shards.append(temp_shard_1)
                    mutated_shards.append(temp_shard_2)
                    break
        except Exception as e:
            mutated_shards.append(original_shard1)
            break
    if all_nodes_in_new_distribution(full_network.nodes, mutated_shards):
        return mutated_shards
    else:
        return list_of_lists_shard


def all_nodes_in_new_distribution(nodes_in_full_network, list_of_lists_shards):
    list_of_nodes = list(nodes_in_full_network)
    for shard in list_of_lists_shards:
        for node in shard:
            list_of_nodes.remove(node)
    if len(list_of_nodes) == 0:
        return True
    else:
        return False


def get_individual_best_solution(sharded_networks_dict, parameterizationdata, non_sharded_network,
                                 dict_of_shortest_paths):
    rankedsolutions = []
    i = 0
    for sharded_network in sharded_networks_dict:
        tot_cost, list_of_lists_shard = fitness(sharded_networks_dict[sharded_network], parameterizationdata,
                                                non_sharded_network, dict_of_shortest_paths)
        rankedsolutions.append([tot_cost, i])
        i += 1
    rankedsolutions.sort()
    # get the best 50 solutions
    best_solutions = rankedsolutions[:50]
    best_fitness = rankedsolutions[0][0]
    best_solution = sharded_networks_dict[rankedsolutions[0][1]]
    return best_fitness, best_solution, best_solutions


# compute fitness for each solution and rank the solutions
def get_best_solution(current_population, this_parameterization, non_sharded_network_graph, dict_of_shortest_paths):
    best_fitness, best_solution, best_solutions = get_individual_best_solution(current_population,
                                                                               this_parameterization,
                                                                               non_sharded_network_graph,
                                                                               dict_of_shortest_paths)
    new_gen = {}
    for bs in range(0, len(best_solutions)):
        new_gen[bs] = mutation(current_population[bs], this_parameterization, non_sharded_network_graph)
    return new_gen, best_solution, best_fitness


def return_first_population(non_sharded_network, parameterizationdata):
    dictionary_of_sharded_network_versions = {}
    for i in range(parameterizationdata.population_size):
        received_non_sharded_network, sharded_network_list_of_lists = shard_network.random_shard(non_sharded_network, parameterizationdata)
        dictionary_of_sharded_network_versions[i] = sharded_network_list_of_lists
    return dictionary_of_sharded_network_versions


def shard_network_GA(non_sharded_network_graph, this_parameterization, dict_of_shortest_paths):
    min_nodes_per_shard = floor(len(non_sharded_network_graph) / this_parameterization.number_of_shards)
    current_population = return_first_population(non_sharded_network_graph, this_parameterization)
    # print('Generation: 0')
    new_gen, current_best_solution, current_best_fitness = get_best_solution(current_population,
                                                                             this_parameterization,
                                                                             non_sharded_network_graph,
                                                                             dict_of_shortest_paths)
    new_best_fitness, new_best_solution, new_best_solutions = get_individual_best_solution(new_gen,
                                                                                           this_parameterization,
                                                                                           non_sharded_network_graph,
                                                                                           dict_of_shortest_paths)

    previous_solutions = {}
    for i in range(this_parameterization.number_of_GA_generations):
        if new_best_fitness < current_best_fitness:
            current_best_fitness = new_best_fitness
            current_best_solution = new_best_solution
            current_population = new_gen
            hash_of_solution = hashing_function(new_best_solution)
            try:
                previous_solutions[hash_of_solution]['Appearances'] += 1
            except Exception as e:
                previous_solutions[hash_of_solution] = {'Appearances': 1}
            if previous_solutions[hash_of_solution]['Appearances'] >= this_parameterization.allowed_repetitions:
                break
            else:
                new_gen, new_best_solution, new_best_fitness = get_best_solution(current_population, this_parameterization, non_sharded_network_graph, dict_of_shortest_paths)
    modified_version_of_non_sharded_network = copy.deepcopy(non_sharded_network_graph)
    for i in range(len(current_best_solution)):
        shard_name = 'shard_' + str(i)
        for node in range(len(modified_version_of_non_sharded_network.nodes)):
            if node in current_best_solution[i]:
                modified_version_of_non_sharded_network.nodes[node]['shard'] = shard_name
    return current_best_solution, modified_version_of_non_sharded_network


def check_if_subgraph_connected(full_network, list_of_nodes):
    # make a new empty subgraph
    subgraph = nx.Graph()
    # add the nodes to the new subgraph
    for node in list_of_nodes:
        subgraph.add_node(node)
    # find the node in the original graph
    for node, neighbour_node in combinations(list_of_nodes, 2):
        if full_network.has_edge(node, neighbour_node):
            subgraph.add_edge(node, neighbour_node)
    return nx.is_connected(subgraph)


def hashing_function(entity):
    h = hashlib.sha256()
    h.update(str(entity).encode(encoding='UTF-8'))
    return h.hexdigest()

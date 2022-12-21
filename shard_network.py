import copy
import create_network
import pymetis

from networkx import *
import random
import sys



# def random_shard(original_received_non_sharded_network):
#     print('********\nBuilding Randomly-Sharded network.. HOLD..')
#     received_non_sharded_network = copy.deepcopy(original_received_non_sharded_network)
#     sharded_network_dict = {}
#     used_nodes = []
#     for i in range(parameterization.number_of_shards):
#         new_label = 'shard_' + str(i + 1)
#         sharded_network_dict[new_label] = []
#         for j in range(parameterization.max_num_nodes_per_shard):
#             found = False
#             randomly_selected_node = None
#             while not found:
#                 randomly_selected_node = random.randint(1, parameterization.number_of_nodes)
#                 if randomly_selected_node not in used_nodes:
#                     used_nodes.append(randomly_selected_node)
#                     found = True
#             sharded_network_dict[new_label].append(randomly_selected_node)
#     for node in range(len(received_non_sharded_network)):
#         for shard in sharded_network_dict:
#             if node+1 in sharded_network_dict[shard]:
#                 received_non_sharded_network.nodes[node]['shard'] = shard
#                 break
#     return received_non_sharded_network, sharded_network_dict


def refine_network(network, sharded_representation):
    new_network = copy.deepcopy(network)
    try:
        for shard in sharded_representation:
            for node in sharded_representation[shard]:
                new_network.nodes[node]['shard'] = shard
        return new_network
    except Exception as e:
        print(e)


def metis_shard(non_sharded_network, num_of_shards):
    print('********\nBuilding Randomly-Sharded network using METIS .. HOLD..')
    cut, parts = pymetis.part_graph(num_of_shards, non_sharded_network)
    sharded_network_dict = {}
    for i in range(num_of_shards):
        new_label = 'shard_' + str(i + 1)
        sharded_network_dict[new_label] = []
    copy_of_non_sharded_network = copy.deepcopy(non_sharded_network)
    for i in range(len(parts)):
        shard_name = 'shard_' + str(parts[i] + 1)
        copy_of_non_sharded_network.nodes[i]['shard'] = shard_name
        sharded_network_dict[shard_name].append(i + 1)
    return copy_of_non_sharded_network, sharded_network_dict


    # boss_sharded_network = {}
    # for i in range(parameterization.number_of_shards):
    #     title_of_shard = 'shard_' + str(i + 1)
    #     boss_sharded_network[title_of_shard] = {}
    # # add ahmad's code here
    # return boss_sharded_network


# def build_optimum_shard(dict_of_shortest_paths, sorted_distances, original_network):
#     number_of_nodes_per_shard = parameterization.max_num_nodes_per_shard
#     nodes_in_optimum_shard = set()
#     for distance in sorted_distances:
#         for key in dict_of_shortest_paths:
#             if dict_of_shortest_paths[key]['distance'] == distance:
#                 diameter_of_optimum_shard = distance
#                 for node in dict_of_shortest_paths[key]['path']:
#                     nodes_in_optimum_shard.add(node)
#                 while len(nodes_in_optimum_shard) < number_of_nodes_per_shard:
#                     list_of_adjacent_nodes = original_network.neighbors(random.choice(list(nodes_in_optimum_shard)))
#                     for node in list_of_adjacent_nodes:
#                         list_of_adjacent_nodes = original_network.neighbors(node)
#
#
#
#
#                     return nodes_in_optimum_shard, diameter_of_optimum_shard

def build_optimum_shard(dict_of_shortest_paths, sorted_distances):
    number_of_nodes_per_shard = parameterization.min_num_nodes_per_shard
    checked_distances = set()

    # to be optimized
    found_optimum_number_of_nodes = 0
    diameter_of_optimum_shard = sys.maxsize
    nodes_in_optimum_shard = set()

    # search:
    for distance in sorted_distances:
        if distance not in checked_distances:
            for key in dict_of_shortest_paths:
                this_distance = dict_of_shortest_paths[key]['distance']
                if this_distance == distance:
                    if this_distance < diameter_of_optimum_shard:
                        this_path = dict_of_shortest_paths[key]['path']
                        len_this_path = len(this_path)
                        condition1 = len_this_path > found_optimum_number_of_nodes
                        condition2 = len_this_path > number_of_nodes_per_shard
                        if condition1 and condition2:
                            found_optimum_number_of_nodes = len_this_path
                            diameter_of_optimum_shard = this_distance
                            nodes_in_optimum_shard = set(this_path)
    return nodes_in_optimum_shard, diameter_of_optimum_shard, found_optimum_number_of_nodes

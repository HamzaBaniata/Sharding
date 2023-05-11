import copy
import random

import pymetis
import sys


def random_shard(original_received_non_sharded_network, min_num_nodes_per_shard, max_num_nodes_per_shard):
    received_non_sharded_network = copy.deepcopy(original_received_non_sharded_network)
    sharded_network_list_of_lists = []
    used_nodes = []
    unused_nodes = [number for number in range(len(original_received_non_sharded_network))]
    while len(unused_nodes) > 0:
        shard = []
        # 0 for min 1 for max
        min_or_max = random.choice([0, 1])
        if min_or_max == 1 and len(unused_nodes) > min_num_nodes_per_shard:
            the_range = max_num_nodes_per_shard
        if min_or_max == 0 or len(unused_nodes) == min_num_nodes_per_shard:
            the_range = min_num_nodes_per_shard
        try:
            for j in range(the_range):
                randomly_selected_node = random.choice(unused_nodes)
                while randomly_selected_node in used_nodes:
                    randomly_selected_node = random.choice(unused_nodes)
                used_nodes.append(randomly_selected_node)
                unused_nodes.remove(randomly_selected_node)
                shard.append(randomly_selected_node)
        except:
            pass
        sharded_network_list_of_lists.append(shard)
    for node in used_nodes:
        for shard_index in range(len(sharded_network_list_of_lists)):
            if node in sharded_network_list_of_lists[shard_index]:
                received_non_sharded_network.nodes[node]['shard'] = "shard_" + str(shard_index)
                break
    return received_non_sharded_network, sharded_network_list_of_lists


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
    cut, shard_distribution = pymetis.part_graph(num_of_shards, non_sharded_network)
    sharded_network_list_of_lists = []
    for i in range(num_of_shards):
        sharded_network_list_of_lists.append([])
    copy_of_non_sharded_network = copy.deepcopy(non_sharded_network)
    for i in range(len(shard_distribution)):
        shard_name = 'shard_' + str(shard_distribution[i])
        copy_of_non_sharded_network.nodes[i]['shard'] = shard_name
        sharded_network_list_of_lists[shard_distribution[i]].append(i)
    return copy_of_non_sharded_network, sharded_network_list_of_lists


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

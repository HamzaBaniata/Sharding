import copy
import random
import pymetis


def random_shard(original_received_non_sharded_network, parameterization):
    min_num_nodes_per_shard = parameterization.min_num_nodes_per_shard
    max_num_nodes_per_shard = parameterization.max_num_nodes_per_shard
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


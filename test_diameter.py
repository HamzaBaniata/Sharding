from itertools import combinations
import sys
import floyd

inf = sys.maxsize


def get_diameter(sent_graph):
    dict_of_shortest_paths = floyd.floyd_algorthim(sent_graph, len(sent_graph))
    diameter_of_this_network = 0
    for element in dict_of_shortest_paths:
        if inf > dict_of_shortest_paths[element]['distance'] > diameter_of_this_network:
            diameter_of_this_network = dict_of_shortest_paths[element]['distance']
    # print('Diameter of ' + sent_graph.name + ' = ' + str(diameter_of_this_network))
    return dict_of_shortest_paths, diameter_of_this_network


def get_diameters_of_shards(shards_representation, dict_of_shortest_paths):
    accumulated_diameters = 0
    for i in range(len(shards_representation)):
        shard_name = 'shard_' + str(i)
        diameter_of_this_shard = 0
        try:
            nodes_in_shard = shards_representation[shard_name]
        except Exception as e:
            nodes_in_shard = shards_representation[i]
        for node, neighbour_node in combinations(nodes_in_shard, 2):
            path_length = dict_of_shortest_paths[str(node) + "_" + str(neighbour_node)]["distance"]
            if inf > path_length > diameter_of_this_shard:
                diameter_of_this_shard = path_length
        # print('Diameter of ' + shard_name + ' = ' + str(diameter_of_this_shard))
        accumulated_diameters += diameter_of_this_shard

    return accumulated_diameters/len(shards_representation)


import math
# import Hamza
import create_network
import shard_network
import test_diameter
import test_security
import copy
import math
import os
import random
import time
from pandas import DataFrame


class ParameterizationData:
    def __init__(self, number_of_nodes):
        self.data = create_network.read_file('simulation_parameters.json')
        # self.number_of_nodes = self.data['number_of_nodes (N)']
        self.network_model = self.data['network_model(1:ER,2:BA)']
        if self.network_model == '1':
            self.parameter = 0.5
        else:
            self.parameter = number_of_nodes - 1
        # self.parameter = self.data['parameter (ER:0<p<=1,BA:1<=m<n)']
        self.maximum_adversary_fraction = self.data['upper_bound_adversary_fraction (0 <= Psi <= 1)']
        self.actual_adversary_fraction = self.data['actual_adversary_fraction_to_be_tested (K/N <= Psi)']
        self.number_of_shards = self.data["num_of_shards"]
        self.target_number_of_adversary_nodes = math.floor(self.actual_adversary_fraction * number_of_nodes)
        self.max_num_nodes_per_shard = math.ceil(number_of_nodes / self.number_of_shards)
        self.min_num_nodes_per_shard = math.floor(number_of_nodes / self.number_of_shards)
        # self.gap = self.data["gap"]
        # self.uncertainty = self.data["uncertainty"]
        self.min_edge_weight = self.data["min_edge_weight"]
        self.max_edge_weight = self.data["max_edge_weight"]


# def output_results(non_sharded_result, randomly_sharded_result):
def output_results(non_sharded_result, randomly_sharded_result):
    print('*******\nEND OF SIMULATION\nRESULTS: \n')
    print("Non Sharded Network is secure: " + str(non_sharded_result))
    print("Randomly Sharded Network is secure: " + str(randomly_sharded_result))
    # print("Ahmad's Sharded Network is secure: " + str(boss_sharded_network_is_secure))


# def calculate_u_factor(minimum, maximum):
#     middle_point = (minimum + maximum)/2
#     return math.ceil(middle_point / 10)


def test(this_parameterization, num_of_nodes, no_of_shards):
    non_sharded_network = create_network.construct_network(this_parameterization, num_of_nodes)
    non_sharded_network_is_secure = test_security.test_non_sharded(non_sharded_network, this_parameterization, num_of_nodes)
    dict_of_shortest_paths, sorted_distances, diam_of_non_sharded = test_diameter.get_diameter(non_sharded_network)
    # nodes_in_optimum_shard, diameter_of_optimum_shard, found_optimum_number_of_nodes = shard_network.build_optimum_shard(
    #     dict_of_shortest_paths, sorted_distances)
    # print('Diameter of optimum shard = ' + str(diameter_of_optimum_shard))
    print('Diameter of non_sharded = ' + str(diam_of_non_sharded))
    # average_diameter = (diameter_of_optimum_shard + diameter_of_non_sharded) / 2
    # u_factor = calculate_u_factor(diameter_of_optimum_shard, diameter_of_non_sharded)
    copy_of_non_sharded_network, metis_network_dict = shard_network.metis_shard(non_sharded_network, no_of_shards)
    avg_shard_diameter = test_diameter.get_diameters_of_shards(metis_network_dict, dict_of_shortest_paths)
    randomly_sharded_network_is_secure, num_of_non_secure_shards = test_security.test_sharded(copy_of_non_sharded_network, metis_network_dict, this_parameterization)
    #
    # output_of_ahmads = Hamza.sharding(non_sharded_network, parameterization.number_of_shards,
    #                                   parameterization.min_num_nodes_per_shard, average_diameter, parameterization.gap)
    # refined_network = shard_network.refine_network(non_sharded_network, output_of_ahmads)
    # test_diameter.get_diameters_of_ahmads_shards(output_of_ahmads, dict_of_shortest_paths)
    #
    # optimum_is_secure = test_security.test_sharded(refined_network, output_of_ahmads)
    # print(non_sharded_network.edges.data())
    # boss_sharded_network_is_secure = test_security.test_sharded(boss_sharded_network)
    output_results(non_sharded_network_is_secure, randomly_sharded_network_is_secure)
    # output_results(non_sharded_network_is_secure, randomly_sharded_network_is_secure)
    return diam_of_non_sharded,  avg_shard_diameter, num_of_non_secure_shards


if __name__ == "__main__":
    network_sizes = []
    numbers_of_shards = []
    scalability_measures = []
    security_measures = []
    for net_size in range(100, 500, 50):
        parameterization = ParameterizationData(net_size)
        num_of_shards = parameterization.number_of_shards
        diameter_of_non_sharded,  average_shard_diameter, number_of_non_secure_shards = test(parameterization, net_size, num_of_shards)
        network_sizes.append(net_size)
        numbers_of_shards.append(num_of_shards)
        scalability_measures.append((1 - (average_shard_diameter/diameter_of_non_sharded)) * num_of_shards)
        security_measures.append(1 - (number_of_non_secure_shards/num_of_shards))
    name_of_file = 'results' + str(num_of_shards) + '.xlsx'
    df = DataFrame({'Network Size': network_sizes,
                    'Number of Shards': numbers_of_shards,
                    'Scalability': scalability_measures,
                    'Security': security_measures})
    df.to_excel(name_of_file, sheet_name='sheet1', index=False)

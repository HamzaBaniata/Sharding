import create_network
import shard_network
import test_diameter
import test_security
import math
import sharding_gentic
from pandas import DataFrame


class ParameterizationData:
    def __init__(self, number_of_nodes):
        self.data = create_network.read_file('simulation_parameters.json')
        # self.number_of_nodes = self.data['number_of_nodes (N)']
        # self.number_of_shards = self.data["num_of_shards"]
        self.number_of_shards = int(math.ceil(number_of_nodes * 0.1))
        self.network_model = self.data['network_model(1:ER,2:BA)']
        if self.network_model == '1':
            self.parameter = 0.5
        else:
            self.parameter = int(math.ceil(number_of_nodes / self.number_of_shards))
        # self.parameter = self.data['parameter (ER:0<p<=1,BA:1<=m<n)']
        self.maximum_adversary_fraction = self.data['upper_bound_adversary_fraction (0 <= Psi <= 1)']
        self.actual_adversary_fraction = self.data['actual_adversary_fraction_to_be_tested (K/N <= Psi)']

        self.target_number_of_adversary_nodes = math.floor(self.actual_adversary_fraction * number_of_nodes)
        self.max_num_nodes_per_shard = math.ceil(number_of_nodes / self.number_of_shards)
        self.min_num_nodes_per_shard = math.floor(number_of_nodes / self.number_of_shards)
        # self.gap = self.data["gap"]
        # self.uncertainty = self.data["uncertainty"]
        self.min_edge_weight = self.data["min_edge_weight"]
        self.max_edge_weight = self.data["max_edge_weight"]
        self.intra_shard_weight_importance = self.data["intra_shard_weight_importance"]
        self.number_of_GA_generations = self.data["number_of_GA_generations"]
        self.percentage_of_nodes_to_be_mutated = self.data["percentage_of_nodes_to_be_mutated"]
        self.population_size = self.data["GA_population_size"]
        self.allowed_repetitions = self.data["Tolerable_number_of_GA_solution_repetitions"]


def output_results(non_sharded_result, randomly_sharded_result, ga_sharded_result):
    print('*******\nEND OF SIMULATION\nRESULTS: \n')
    print("Non Sharded Network is secure: " + str(non_sharded_result))
    print("Randomly Sharded Network is secure: " + str(randomly_sharded_result))
    print("GA-based Sharded Network is secure: " + str(ga_sharded_result))


def test(this_parameterization, num_of_nodes, no_of_shards):
    population_size = this_parameterization.population_size
    non_sharded_network_graph = create_network.construct_network(this_parameterization, num_of_nodes)
    non_sharded_network_is_secure = test_security.test_non_sharded(non_sharded_network_graph, this_parameterization, num_of_nodes)
    dict_of_shortest_paths, diam_of_non_sharded = test_diameter.get_diameter(non_sharded_network_graph)
    # nodes_in_optimum_shard, diameter_of_optimum_shard, found_optimum_number_of_nodes = shard_network.build_optimum_shard(
    #     dict_of_shortest_paths, sorted_distances)
    # print('Diameter of optimum shard = ' + str(diameter_of_optimum_shard))
    print('Diameter of non_sharded = ' + str(diam_of_non_sharded))
    # average_diameter = (diameter_of_optimum_shard + diameter_of_non_sharded) / 2
    # u_factor = calculate_u_factor(diameter_of_optimum_shard, diameter_of_non_sharded)
    copy_of_non_sharded_network, list_of_lists_sharded_network_randomly = shard_network.metis_shard(non_sharded_network_graph, no_of_shards)
    avg_shard_diameter_random = test_diameter.get_diameters_of_shards(list_of_lists_sharded_network_randomly, dict_of_shortest_paths)
    randomly_sharded_network_is_secure = test_security.test_sharded(copy_of_non_sharded_network, list_of_lists_sharded_network_randomly, this_parameterization)
    ga_based_solution, modified_non_sharded_network = sharding_gentic.shard_network_GA(non_sharded_network_graph,
                                                         this_parameterization.intra_shard_weight_importance,
                                                         no_of_shards, this_parameterization.number_of_GA_generations,
                                                         this_parameterization.percentage_of_nodes_to_be_mutated,
                                                         population_size, this_parameterization.min_num_nodes_per_shard,
                                                         this_parameterization.max_num_nodes_per_shard, parameterization.allowed_repetitions, dict_of_shortest_paths)

    GA_avg_shard_diameter = test_diameter.get_diameters_of_shards(ga_based_solution, dict_of_shortest_paths)
    GA_based_is_secure = test_security.test_sharded(modified_non_sharded_network, ga_based_solution, this_parameterization)
    output_results(non_sharded_network_is_secure, randomly_sharded_network_is_secure[0], GA_based_is_secure[0])
    return diam_of_non_sharded, avg_shard_diameter_random, randomly_sharded_network_is_secure[1], GA_avg_shard_diameter, GA_based_is_secure[1]


if __name__ == "__main__":
    network_sizes = []
    numbers_of_shards = []
    scalability_measures_random = []
    scalability_measures_ga = []
    security_measures_random = []
    security_measures_ga = []
    # for net_size in range(5, 20, 2):
    for net_size in range(100, 250, 5):
        parameterization = ParameterizationData(net_size)
        num_of_shards = parameterization.number_of_shards
        diameter_of_non_sharded, average_shard_diameter_random, number_of_non_secure_shards_random, average_shard_diameter_ga, number_of_non_secure_shards_ga = test(
            parameterization, net_size, num_of_shards)
        network_sizes.append(net_size)
        numbers_of_shards.append(num_of_shards)
        scalability_measures_random.append(100 * ((1 - (average_shard_diameter_random/diameter_of_non_sharded)) * num_of_shards))
        security_measures_random.append(100 * (1 - (number_of_non_secure_shards_random/num_of_shards)))
        scalability_measures_ga.append(100 * (
            (1 - (average_shard_diameter_ga / diameter_of_non_sharded)) * num_of_shards))
        security_measures_ga.append(100 * (1 - (number_of_non_secure_shards_ga / num_of_shards)))
    name_of_file = 'results' + str(num_of_shards) + '.xlsx'
    df = DataFrame({'Network Size': network_sizes,
                    'Number of Shards': numbers_of_shards,
                    'Scalability_of_random(%)': scalability_measures_random,
                    'Security_of_random(%)': security_measures_random,
                    'Scalability_of_GA(%)': scalability_measures_ga,
                    'Security_of_GA(%)': security_measures_ga})
    df.to_excel(name_of_file, sheet_name='sheet1', index=False)


# test for different net sizes (y-axis: scalability and security)
# test for different number of shards (y-axis: scalability and security)
# test for different adversary fraction
# test for different intra_shard importance values
# test for different number of generations
# test for different percentage of nodes per shard to be mutated
# test for different populatin sizes


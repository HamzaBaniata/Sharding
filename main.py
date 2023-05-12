import create_network
import shard_network
import test_diameter
import test_security
import sharding_gentic
from pandas import DataFrame
import classes
import output


def test(this_parameterization, num_of_nodes, no_of_shards):
    population_size = this_parameterization.population_size
    non_sharded_network_graph = create_network.construct_network(this_parameterization, num_of_nodes)
    non_sharded_network_is_secure = test_security.test_non_sharded(non_sharded_network_graph, this_parameterization, num_of_nodes)
    dict_of_shortest_paths, diam_of_non_sharded = test_diameter.get_diameter(non_sharded_network_graph)
    print('Diameter of non_sharded = ' + str(diam_of_non_sharded))
    copy_of_non_sharded_network, list_of_lists_sharded_network_randomly = shard_network.random_shard(non_sharded_network_graph, this_parameterization)
    avg_shard_diameter_random = test_diameter.get_diameters_of_shards(list_of_lists_sharded_network_randomly, dict_of_shortest_paths)
    randomly_sharded_network_is_secure = test_security.test_sharded(copy_of_non_sharded_network, list_of_lists_sharded_network_randomly, this_parameterization)
    ga_based_solution, modified_non_sharded_network = sharding_gentic.shard_network_GA(non_sharded_network_graph,
                                                                                       this_parameterization, dict_of_shortest_paths)

    ga_avg_shard_diameter = test_diameter.get_diameters_of_shards(ga_based_solution, dict_of_shortest_paths)
    ga_based_is_secure = test_security.test_sharded(modified_non_sharded_network, ga_based_solution, this_parameterization)
    output.output_results(non_sharded_network_is_secure, randomly_sharded_network_is_secure[0], ga_based_is_secure[0])
    return diam_of_non_sharded, avg_shard_diameter_random, randomly_sharded_network_is_secure[1], ga_avg_shard_diameter, ga_based_is_secure[1]


if __name__ == "__main__":
    ParameterizationData = classes.ParameterizationData()
    simulation_data = classes.TestedData()
    keep_simulating, net_size = ParameterizationData.get_number_of_nodes()
    while keep_simulating:
        num_of_shards = ParameterizationData.number_of_shards
        diameter_of_non_sharded, average_shard_diameter_random, number_of_non_secure_shards_random,\
            average_shard_diameter_ga, number_of_non_secure_shards_ga \
            = test(ParameterizationData, net_size, num_of_shards)
        simulation_data.append_new_data(net_size, num_of_shards,
                                        100 * ((1 - (average_shard_diameter_random/diameter_of_non_sharded)) * num_of_shards),
                                        100 * (1 - (number_of_non_secure_shards_random/num_of_shards)),
                                        100 * (1 - (average_shard_diameter_ga / diameter_of_non_sharded)) * num_of_shards,
                                        100 * (1 - (number_of_non_secure_shards_ga / num_of_shards)))
        keep_simulating, net_size = ParameterizationData.get_number_of_nodes()
    output.save_simulation_data(simulation_data)



# test for different net sizes (y-axis: scalability and security)
# test for different number of shards (y-axis: scalability and security)
# test for different adversary fraction
# test for different intra_shard importance values
# test for different number of generations
# test for different percentage of nodes per shard to be mutated
# test for different populatin sizes


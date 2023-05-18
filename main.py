import math

import create_network
import shard_network
import test_diameter
import test_security
import sharding_gentic
import classes
import output


def test(this_parameterization, num_of_nodes):
    non_sharded_network_graph = create_network.construct_network(this_parameterization, num_of_nodes)
    non_sharded_network_is_secure = test_security.test_non_sharded(non_sharded_network_graph, this_parameterization, num_of_nodes)
    dict_of_shortest_paths, diam_of_non_sharded = test_diameter.get_diameter(non_sharded_network_graph)
    # print('Diameter of non_sharded = ' + str(diam_of_non_sharded))
    copy_of_non_sharded_network, list_of_lists_sharded_network_randomly = shard_network.random_shard(non_sharded_network_graph, this_parameterization)
    avg_shard_diameter_random = test_diameter.get_diameters_of_shards(list_of_lists_sharded_network_randomly, dict_of_shortest_paths)
    randomly_sharded_network_is_secure = test_security.test_sharded(copy_of_non_sharded_network, list_of_lists_sharded_network_randomly, this_parameterization)
    ga_based_solution, modified_non_sharded_network = sharding_gentic.shard_network_GA(non_sharded_network_graph,
                                                                                       this_parameterization, dict_of_shortest_paths)

    ga_avg_shard_diameter = test_diameter.get_diameters_of_shards(ga_based_solution, dict_of_shortest_paths)
    ga_based_is_secure = test_security.test_sharded(modified_non_sharded_network, ga_based_solution, this_parameterization)
    # output.output_results(non_sharded_network_is_secure, randomly_sharded_network_is_secure[0], ga_based_is_secure[0])
    return diam_of_non_sharded, avg_shard_diameter_random, randomly_sharded_network_is_secure[1], ga_avg_shard_diameter, ga_based_is_secure[1]


if __name__ == "__main__":
    ParameterizationData = classes.ParameterizationData()
    simulation_data = classes.TestedData()
    keep_simulating, net_size = ParameterizationData.get_number_of_nodes()
    while keep_simulating:
        # change adversary fractions
        adversary_fraction, stop1, step1 = ParameterizationData.get_parameters_adversary_fraction()
        print("Net_size:" + str(net_size))
        while adversary_fraction < stop1:
            print("adversary_fraction:" + str(adversary_fraction))
            ParameterizationData.actual_adversary_fraction = adversary_fraction
            ParameterizationData.target_number_of_adversary_nodes = math.floor(adversary_fraction * net_size)
            intra_shard_importance, stop2, step2 = ParameterizationData.get_parameters_intra_shard_weight_importance()
            # change shard importance
            while intra_shard_importance < stop2:
                print("intra_shard_importance:" + str(intra_shard_importance))
                ParameterizationData.intra_shard_weight_importance = intra_shard_importance
                no_GA_generation, stop3, step3 = ParameterizationData.get_parameters_number_of_GA_generations()
                # change number of GA generations
                while no_GA_generation < stop3:
                    print("no_GA_generation:" + str(no_GA_generation))
                    ParameterizationData.number_of_GA_generations = no_GA_generation
                    percentage, stop4, step4 = ParameterizationData.get_parameters_percentage_of_nodes_to_be_mutated()
                    # change percentage of nodes to be mutated
                    while percentage < stop4:
                        print("percentage_of_nodes_to_be_mutated:" + str(percentage))
                        ParameterizationData.percentage_of_nodes_to_be_mutated = percentage
                        this_population_size, stop5, step5 = ParameterizationData.get_parameters_GA_population_size()
                        # change GA population size
                        while this_population_size < stop5:
                            print("population_size:" + str(this_population_size))
                            ParameterizationData.population_size = this_population_size
                            tolerable_repetitions, stop6, step6 = ParameterizationData.get_parameters_GA_solution_repetitions()
                            # change GA tolerable number of repetitions
                            while tolerable_repetitions < stop6:
                                print("allowed_repetitions:" + str(tolerable_repetitions))
                                ParameterizationData.allowed_repetitions = tolerable_repetitions
                                num_of_shards = ParameterizationData.number_of_shards
                                diameter_of_non_sharded, average_shard_diameter_random, number_of_non_secure_shards_random,\
                                    average_shard_diameter_ga, number_of_non_secure_shards_ga \
                                    = test(ParameterizationData, net_size)
                                simulation_data.append_new_data(net_size, num_of_shards, adversary_fraction, intra_shard_importance, no_GA_generation, percentage, this_population_size, tolerable_repetitions,
                                                                100 * ((1 - (average_shard_diameter_random/diameter_of_non_sharded)) * num_of_shards),
                                                                100 * (1 - (number_of_non_secure_shards_random/num_of_shards)),
                                                                100 * (1 - (average_shard_diameter_ga / diameter_of_non_sharded)) * num_of_shards,
                                                                100 * (1 - (number_of_non_secure_shards_ga / num_of_shards)))
                                tolerable_repetitions += step6
                            this_population_size += step5
                        percentage += step4
                    no_GA_generation += step3
                intra_shard_importance += step2
            adversary_fraction += step1
        keep_simulating, net_size = ParameterizationData.get_number_of_nodes()

    output.save_simulation_data(simulation_data)

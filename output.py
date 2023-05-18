from pandas import DataFrame
from os import system, name


def save_simulation_data(simulation_data):
    total_sec = 0
    total_sca = 0
    Zero_Sca_dif = 0
    Zero_Sec_dif = 0
    Neg_Sca_dif = 0
    Neg_Sec_dif = 0
    positive_Sca_dif = 0
    positive_Sec_dif= 0
    for num in simulation_data.scalability_difference:
        if num > 0:
            positive_Sca_dif += 1
        elif num < 0:
            Neg_Sca_dif += 1
        else:
            Zero_Sca_dif += 1
        total_sca += num
    avg_scalability_different = total_sca / (positive_Sca_dif+Neg_Sca_dif+Zero_Sca_dif)
    for num in simulation_data.security_difference:
        if num > 0:
            positive_Sec_dif += 1
        elif num < 0:
            Neg_Sec_dif += 1
        else:
            Zero_Sec_dif += 1
        total_sec += num
    avg_security_difference = total_sec/(positive_Sec_dif+Neg_Sec_dif+Zero_Sec_dif)
    output_results(positive_Sca_dif+Neg_Sca_dif+Zero_Sca_dif, avg_security_difference, avg_scalability_different, simulation_data)
    name_of_file = 'results.xlsx'
    df = DataFrame({'Network Size': simulation_data.network_sizes,
                    'Number of Shards': simulation_data.numbers_of_shards,
                    "adversary_fraction": simulation_data.adversary_fraction,
                    "intra_shard_importance": simulation_data.intra_shard_importance,
                    "no_GA_generation": simulation_data.no_GA_generation,
                    "percentage": simulation_data.percentage,
                    "this_population_size": simulation_data.this_population_size,
                    "tolerable_repetitions": simulation_data.tolerable_repetitions,
                    'Scalability_of_random(%)': simulation_data.scalability_measures_random,
                    'Security_of_random(%)': simulation_data.security_measures_random,
                    'Scalability_of_GA(%)': simulation_data.scalability_measures_ga,
                    'Security_of_GA(%)': simulation_data.security_measures_ga,
                    'Difference in Scalability': simulation_data.scalability_difference,
                    'Difference in Security': simulation_data.security_difference})

    df.to_excel(name_of_file, sheet_name='sheet1', index=False)


def output_results(number_of_tests, avg_security_difference, avg_scalability_different, simulation_data):
    print('*******\nEND OF SIMULATION\nRESULTS: \n')
    print("Total number of tested cases: " + str(number_of_tests))
    print("Tested Network Sizes: " + str(min(simulation_data.network_sizes)) + " to " + str(max(simulation_data.network_sizes)))
    print("Tested Shard Numbers: " + str(min(simulation_data.numbers_of_shards)) + " to " + str(max(simulation_data.numbers_of_shards)))
    print("Tested Adversary Fraction: " + str(min(simulation_data.adversary_fraction)) + " to " + str(max(simulation_data.adversary_fraction)))
    print("Tested Intra-Shard Importance: " + str(min(simulation_data.intra_shard_importance)) + " to " + str(max(simulation_data.intra_shard_importance)))
    print("Tested number of GA generations: " + str(min(simulation_data.no_GA_generation)) + " to " + str(max(simulation_data.no_GA_generation)))
    print("Tested percentage_of_nodes_to_be_mutated: " + str(min(simulation_data.percentage)) + " to " + str(max(simulation_data.percentage)))
    print("Tested GA_population_size:" + str(min(simulation_data.this_population_size)) + " to " + str(max(simulation_data.this_population_size)))
    print("Tested Tolerable_number_of_GA_solution_repetitions:" + str(min(simulation_data.tolerable_repetitions)) + " to " + str(max(simulation_data.tolerable_repetitions)))
    print("Average Security Difference: " + str(avg_security_difference))
    print("Average Scalability Difference: " + str(avg_scalability_different))


def print_on_screen(net_size, num_shards, adversary_fraction, intra_shard_importance, no_GA_generation, percentage, this_population_size, tolerable_repetitions):
    try:
        # for windows
        if name == 'nt':
            _ = system('cls')
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = system('clear')
    except Exception as e:
        print(e)
    print("Net_size:" + str(net_size))
    print("Number of Shards:" + str(num_shards))
    print("adversary_fraction:" + str(adversary_fraction))
    print("intra_shard_importance:" + str(intra_shard_importance))
    print("no_GA_generation:" + str(no_GA_generation))
    print("percentage_of_nodes_to_be_mutated:" + str(percentage))
    print("population_size:" + str(this_population_size))
    print("allowed_repetitions:" + str(tolerable_repetitions))

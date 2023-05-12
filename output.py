from pandas import DataFrame


def save_simulation_data(simulation_data):
    name_of_file = 'results.xlsx'
    df = DataFrame({'Network Size': simulation_data.network_sizes,
                    'Number of Shards': simulation_data.numbers_of_shards,
                    'Scalability_of_random(%)': simulation_data.scalability_measures_random,
                    'Security_of_random(%)': simulation_data.security_measures_random,
                    'Scalability_of_GA(%)': simulation_data.scalability_measures_ga,
                    'Security_of_GA(%)': simulation_data.security_measures_ga,
                    'Difference in Scalability': simulation_data.scalability_difference,
                    'Difference in Security': simulation_data.security_difference})

    df.to_excel(name_of_file, sheet_name='sheet1', index=False)


def output_results(non_sharded_result, randomly_sharded_result, ga_sharded_result):
    print('*******\nEND OF SIMULATION\nRESULTS: \n')
    print("Non Sharded Network is secure: " + str(non_sharded_result))
    print("Randomly Sharded Network is secure: " + str(randomly_sharded_result))
    print("GA-based Sharded Network is secure: " + str(ga_sharded_result))
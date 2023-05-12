import create_network
import math


class ParameterizationData:
    def __init__(self):
        self.min_num_nodes_per_shard = None
        self.max_num_nodes_per_shard = None
        self.target_number_of_adversary_nodes = None
        self.parameter = None
        self.number_of_shards = None
        self.data = create_network.read_file('simulation_parameters.json')
        self.step_in_net_size_change_till_max_is_tested = self.data['step_in_net_size_change_till_max_is_tested']
        self.number_of_nodes = self.data['min_net_size_to_be_tested'] - self.step_in_net_size_change_till_max_is_tested
        self.max_net_size_to_be_tested = self.data['max_net_size_to_be_tested']
        self.network_model = self.data['network_model(1:ER,2:BA)']
        self.maximum_adversary_fraction = self.data['upper_bound_adversary_fraction (0 <= Psi <= 1)']
        self.actual_adversary_fraction = self.data['actual_adversary_fraction_to_be_tested (K/N <= Psi)']
        self.min_edge_weight = self.data["min_edge_weight"]
        self.max_edge_weight = self.data["max_edge_weight"]
        self.intra_shard_weight_importance = self.data["intra_shard_weight_importance"]
        self.number_of_GA_generations = self.data["number_of_GA_generations"]
        self.percentage_of_nodes_to_be_mutated = self.data["percentage_of_nodes_to_be_mutated"]
        self.population_size = self.data["GA_population_size"]
        self.allowed_repetitions = self.data["Tolerable_number_of_GA_solution_repetitions"]

    def get_number_of_nodes(self):
        self.number_of_nodes = self.number_of_nodes + self.step_in_net_size_change_till_max_is_tested
        if self.number_of_nodes > self.max_net_size_to_be_tested:
            return False, 0
        else:
            self.number_of_shards = int(math.ceil(self.number_of_nodes * 0.1))
            if self.number_of_shards <= 1: self.number_of_shards += 1
            if self.network_model == 1:
                self.parameter = 0.5
            else:
                self.parameter = int(math.ceil(self.number_of_nodes / self.number_of_shards)) - 1
            self.target_number_of_adversary_nodes = math.floor(self.actual_adversary_fraction * self.number_of_nodes)
            self.max_num_nodes_per_shard = math.ceil(self.number_of_nodes / self.number_of_shards)
            self.min_num_nodes_per_shard = math.floor(self.number_of_nodes / self.number_of_shards)
            return True, self.number_of_nodes


class TestedData:
    def __init__(self):
        self.network_sizes = []
        self.numbers_of_shards = []
        self.scalability_measures_random = []
        self.scalability_measures_ga = []
        self.security_measures_random = []
        self.security_measures_ga = []
        self.security_difference = []
        self.scalability_difference = []

    def append_new_data(self, network_size, numbers_of_shards, scalability_measure_random, security_measure_random, scalability_measure_ga, security_measure_ga):
        self.network_sizes.append(network_size)
        self.numbers_of_shards.append(numbers_of_shards)
        self.scalability_measures_random.append(scalability_measure_random)
        self.scalability_measures_ga.append(scalability_measure_ga)
        self.security_measures_random.append(security_measure_random)
        self.security_measures_ga.append(security_measure_ga)
        self.security_difference.append(security_measure_ga - security_measure_random)
        self.scalability_difference.append(scalability_measure_ga - scalability_measure_random)

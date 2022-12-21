import networkx as nx
import create_network
import test_diameter


def test_non_sharded(network, this_parameterization, num_of_nodes):
    number_of_adversary_nodes, number_of_honest_nodes = test_nodes_individually(network)
    actual_adversarial_fraction = number_of_adversary_nodes/num_of_nodes
    print('actual_adversarial_fraction of <' + network.name + '> : ' + str(actual_adversarial_fraction))

    if actual_adversarial_fraction <= this_parameterization.maximum_adversary_fraction:
        print("\nSecurity Status: ==SECURE==\n**********\n")
        return True
    else:
        print("\nSecurity Status: |++|++|++| INSECURE +|++|++|++|\n**********\n")
        return False


def test_sharded(full_network, shards_representation, parameterization):
    is_secure = True
    dictionary_of_node_states = {}
    num_of_non_secure_shards = 0
    try:
        for shard_name in shards_representation:
            dictionary_of_node_states[shard_name] = {'Honest Nodes': 0,
                                                     'Adversary Nodes': 0,
                                                     'Is_Secure': True}
        for node in range(len(full_network)):
            is_adversary = full_network.nodes[node]['is_adversary']
            shard_name = full_network.nodes[node]['shard']
            if is_adversary:
                dictionary_of_node_states[shard_name]['Adversary Nodes'] += 1
            else:
                dictionary_of_node_states[shard_name]['Honest Nodes'] += 1
        for shard in dictionary_of_node_states:
            actual_adversarial_fraction = dictionary_of_node_states[shard]['Adversary Nodes'] / (dictionary_of_node_states[shard]['Honest Nodes'] + dictionary_of_node_states[shard]['Adversary Nodes'])
            print('actual_adversarial_fraction of <' + shard + '> :' + str(actual_adversarial_fraction))
            if actual_adversarial_fraction <= parameterization.maximum_adversary_fraction:
                print("\nSecurity Status: ==SECURE==\n**********\n")
            else:
                print("\nSecurity Status: |++|++|++| INSECURE +|++|++|++|\n**********\n")
                dictionary_of_node_states[shard]['Is_Secure'] = False
                is_secure = False
                num_of_non_secure_shards += 1
        return is_secure, num_of_non_secure_shards
    except Exception as e:
        print(e)


def make_dict_network(sent_dict):
    network = nx.Graph()
    for key in sent_dict:
        network.add_node(key)
        network.nodes[key]['is_adversary'] = sent_dict[key]['is_adversary']
    return network


def make_network_dictionary(sent_network):
    network_as_dictionary = {}
    for node in sent_network:
        network_as_dictionary[node] = sent_network.nodes[node]
    return network_as_dictionary


def test_nodes_individually(network):
    number_of_adversary_nodes = 0
    number_of_honest_nodes = 0
    for node in network:
        if network.nodes[node]['is_adversary']:
            number_of_adversary_nodes += 1
        else:
            number_of_honest_nodes += 1
    return number_of_adversary_nodes, number_of_honest_nodes

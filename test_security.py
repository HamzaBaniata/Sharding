import networkx as nx


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
        if type(shards_representation) == list:
            for i in range(len(shards_representation)):
                dictionary_of_node_states['shard_' + str(i)] = {'Honest Nodes': 0,
                                                                'Adversary Nodes': 0,
                                                                'Is_Secure': True}
        else:
            for shard_name in shards_representation:
                dictionary_of_node_states[shard_name] = {'Honest Nodes': 0,
                                                         'Adversary Nodes': 0,
                                                         'Is_Secure': True}
        for i in range(len(shards_representation)):
            shard_name = 'shard_' + str(i)
            for node in range(len(full_network.nodes)):
                if node in shards_representation[i]:
                    full_network.nodes[node]['shard'] = shard_name
                    is_adversary = full_network.nodes[node]['is_adversary']
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


def test_nodes_individually(network):
    number_of_adversary_nodes = 0
    number_of_honest_nodes = 0
    for node in network:
        if network.nodes[node]['is_adversary']:
            number_of_adversary_nodes += 1
        else:
            number_of_honest_nodes += 1
    return number_of_adversary_nodes, number_of_honest_nodes

from gurobipy import *
from networkx import *
import numpy as np

import create_network

parameterization = create_network.parameterization


def sharding(send_graph, num_partitions, lower_bound, opt_avg_dia, gap):
    N = len(send_graph)
    M = len(send_graph.edges())
    graph_edges, weights = graph_to_input(send_graph)
    n = N
    m = M

    V = list(range(n))
    A = graph_edges

    # weights on the edges
    d = weights
    B = [(j, i) for (i, j) in d.keys()]

    # number of partitions
    c = num_partitions
    C = tuplelist(range(c))
    # minimum number of nodes in each partition
    a = lower_bound

    VV = tuplelist(range(n, n + c))
    AA = []
    for i in VV:
        for j in V:
            AA.append((i, j))
    E = A + AA

    outgoing = {i: [(j, k) for (k, j) in A if j == i] + [(k, j) for (k, j) in A if k == i] for i in V}
    incoming = {i: [(j, k) for (j, k) in A + AA if k == i] + [(j, k) for (k, j) in A + AA if k == i] for i in V}

    part_model = Model()

    # Variables
    x = part_model.addVars(E, vtype=GRB.BINARY, name="x", lb=0)
    y = part_model.addVars(V, C, vtype=GRB.BINARY, name="y", lb=0)
    f = part_model.addVars(E + B, vtype=GRB.CONTINUOUS, name="f", lb=0)

    obj = quicksum(x[i, j] * d[i, j] for (i, j) in A)
    part_model.setObjective(obj, GRB.MINIMIZE)

    for i in V:
        part_model.addConstr(quicksum(y[i, k] for k in C) == 1, name="con_1" + str(i))

    cont1 = 0
    for k in C:
        for (i, j) in A:
            cont1 += 1
            part_model.addConstr(y[i, k] + y[j, k] - x[i, j] <= 1, name="con_2" + str(cont1))

    cont2 = 0
    for k in C:
        for l in C:
            for (i, j) in A:
                if k != l:
                    cont2 += 1
                    part_model.addConstr(y[i, k] + y[j, l] + x[i, j] <= 2, name="con_3" + str(cont2))

    cont3 = 0
    for k in VV:
        cont3 += 1
        part_model.addConstr(quicksum(x[k, i] for i in V) == 1, name="con_4" + str(cont3))

    cont4 = 0
    for k in C:
        cont4 += 1
        part_model.addConstr(quicksum(f[k + n, i] for i in V) == quicksum(y[i, k] for i in V),
                             name="con_5" + str(cont4))

    cont5 = 0
    for j in V:
        cont5 += 1
        part_model.addConstr(
            quicksum(f[i, l] for (i, l) in incoming[j]) - quicksum(f[l, i] for (l, i) in outgoing[j]) == 1,
            name="con_6" + str(cont5))

    cont6 = 0
    for (i, j) in A:
        cont6 += 1
        part_model.addConstr(f[i, j] + f[j, i] <= (n - (c - 1) * a) * x[i, j], name="con_7" + str(cont5))

    cont7 = 0
    for (k, i) in AA:
        cont7 += 1
        part_model.addConstr(a * x[k, i] <= f[k, i], name="con_8" + str(cont6))

    cont8 = 0
    for (k, i) in AA:
        cont8 += 1
        part_model.addConstr(f[k, i] <= (n - (c - 1) * a) * x[k, i], name="con_9" + str(cont8))

    part_model.setParam(GRB.Param.MIPGap, gap)
    # optimize the model
    part_model.optimize()
    # how many solutions to collect
    part_model.setParam(GRB.Param.PoolSolutions, 100)
    #  setting a gap for the worst possible solution that will be accepted
    part_model.setParam(GRB.Param.PoolGap, gap)
    part_model.setParam(GRB.Param.PoolSearchMode, 2)

    # save problem
    part_model.write('poolsearch.lp')

    # Optimize
    part_model.optimize()

    part_model.setParam(GRB.Param.OutputFlag, 0)

    # Status checking
    status = part_model.Status
    if status in (GRB.INF_OR_UNBD, GRB.INFEASIBLE, GRB.UNBOUNDED):
        print('The model is infeasible or unbounded')
        sys.exit(1)
    elif status != GRB.OPTIMAL:
        print('Optimization was stopped with status ' + str(status))
        sys.exit(1)

    # Print number of solutions stored
    nSolutions = part_model.SolCount
    print('Number of solutions found: ' + str(nSolutions))

    # Print objective values of solutions
    for e in range(nSolutions):
        part_model.setParam(GRB.Param.SolutionNumber, e)
        print('%g ' % part_model.PoolObjVal, end='')
        if e % 15 == 14:
            print('')
    print('')

    # the possible solutions
    for num_sol in range(nSolutions):
        part_model.setParam(GRB.Param.SolutionNumber, num_sol)
        G_Dict = {}
        G = nx.Graph()
        for (i, j) in A:
            if x[i, j].Xn > 0.9:
                G.add_edge(i, j, weight=d[i, j])
                G_Dict[(i, j)] = d[i, j]
        # find the connected components of the solution (shards)
        S = [G.subgraph(c).copy() for c in nx.connected_components(G)]
        dia = 0
        for l in range(len(S)):
            # floyd to find all shortest path
            diam = floyd_warshall(S[l], weight='weight')
            new_out = {}
            for new_k, new_v in diam.items():
                count_new = 0
                for element in new_v.values():
                    if element > count_new:
                        count_new = element
                new_out[new_k] = count_new
            # find the diameter for each shard
            key = max(new_out, key=new_out.get)
            # sum the diameters of the shards
            dia += new_out[key]
        # find the average diameter of the shards
        avg_dia = (dia / c)
        print(opt_avg_dia)
        print(avg_dia)
        uncertainty_level = opt_avg_dia * parameterization.uncertainty
        # if the avg diameter fulfill the condition, break and return the solution
        condition1 = opt_avg_dia - uncertainty_level <= avg_dia
        condition2 = avg_dia <= opt_avg_dia + uncertainty_level
        if condition1 and condition2:
            return prepare_ahmad_output(G)
        else:
            print('Cannot find optimum solution for this network')
            sys.exit(1)


def prepare_ahmad_output(ahmads_solution):
    sharded_network_dict = {}
    components_new = []
    try:
        i = 0
        for element in nx.connected_components(ahmads_solution):
            components_new.append(element)
            new_label = 'shard_' + str(i + 1)
            sharded_network_dict[new_label] = element
            i += 1
        return sharded_network_dict
    except Exception as e:
        print(e)
# G = nx.dense_gnm_random_graph(10, 20)
# V = G.nodes
# A = G.edges
#
# W = np.random.randint(1, 10, len(A))
#
# for i, e in enumerate(A()):
#     G[e[0]][e[1]]['weight'] = W[i]



def graph_to_input(network):
    edges = []
    weights = {}
    for edge in network.edges.data():
        new_key = (edge[0], edge[1])
        edges.append(new_key)
        new_value = edge[2]['weight']
        weights[new_key] = new_value
    return edges, weights


# best_solution = sharding(10, 20, G, 2, 5, 10, 0.55)
# print("best solution:")
# print(best_solution)



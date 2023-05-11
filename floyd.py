import sys
from itertools import combinations

import create_network

inf = sys.maxsize


def floyd_algorthim(Gra, length):
    dist = {}
    adjacency_matrix = turn_graph_into_adjacency_matrix(Gra, length)
    for row in range ( len(Gra) ):
        for column in range ( len(Gra) ):
            if row != column:
                label = str(row) + "_" + str(column)
                entry = {"distance": adjacency_matrix[row][column],
                         'path': [row, column]}
                dist[label] = entry

    for k in range(len(Gra)):
        for t in range(len(Gra)):
            for f in range(len(Gra)):
                if t != f and f != k and t != k:
                    label = str ( t ) + "_" + str ( f )
                    label_2 = str ( t ) + "_" + str ( k )
                    label_3 = str ( k ) + "_" + str ( f )
                    direct_dist = dist[label]["distance"]
                    undirected_dist = dist[label_2]["distance"] + dist[label_3]["distance"]
                    if direct_dist > undirected_dist:
                        distance = undirected_dist
                        new_path = dist[label_2]["path"] + dist[label_3]["path"]
                        dist[label]['path'] = new_path
                        dist[label]['distance'] = distance

    sorted_list_of_distances = []
    for key in dist:
        if dist[key]['distance'] < sys.maxsize:
            new_path = []
            for entity in dist[key]['path']:
                if entity not in new_path:
                    new_path.append ( entity )
            dist[key]['path'] = new_path
            sorted_list_of_distances.append(dist[key]['distance'])
            # bisect.insort(sorted_list_of_distances, dist[key]['distance'])
    sorted_list_of_distances = sorted(sorted_list_of_distances, reverse=True)
    # print(sorted_list_of_distances)
    return dist


def get_best_choice(list_of_paths, loc_I_S, excepted_paths):
    maxcard = 0
    best_path = []
    for path in list_of_paths:
        if path not in excepted_paths:
            diff3 = find_largest_difference(loc_I_S, path)
            if diff3 > maxcard:
                # and (path[0] in ultimate_S or path[-1] in ultimate_S):
                maxcard = diff3
                best_path = path
    return best_path


def find_largest_difference(list1, list2):
    number_of_uncommon_elements = 0
    for element in list1:
        if element not in list2:
            number_of_uncommon_elements += 1
    return number_of_uncommon_elements


def turn_graph_into_adjacency_matrix(graph, number_of_nodes):
    adjacency_matrix_size = number_of_nodes
    adjacency_matrix = [[inf for column in range(adjacency_matrix_size)] for row in range(adjacency_matrix_size)]
    for x, y in combinations(graph, 2):
        if graph.has_edge(x, y):
            if graph.edges[x, y]["weight"] < inf:
                adjacency_matrix[x][y] = graph.edges[x, y]["weight"]
                adjacency_matrix[y][x] = graph.edges[x, y]["weight"]
    return adjacency_matrix

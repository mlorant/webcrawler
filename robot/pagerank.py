# -*- coding: utf-8 -*-

# Part of this file is produced by:
# Copyright (c) 2010 Pedro Matiello <pmatiello@gmail.com>
#                    Juarez Bochi <jbochi@gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

"""
PageRank algorithm

@sort: pagerank
"""

from models import Link


class Digraph(object):
    def __init__(self):
        self.node_neighbors = {}     # Pairing: Node -> Neighbors
        self.node_incidence = {}     # Pairing: Node -> Incident nodes
        self.node_attrs = {}

    def nodes(self):
        return list(self.node_neighbors.keys())

    def neighbors(self, node):
        """
        Return all nodes that are directly accessible from given node.
        """
        return self.node_neighbors[node]

    def incidents(self, node):
        """
        Return all nodes that are incident to the given node.
        """
        return self.node_incidence[node]

    def edges(self):
        """
        Return all edges in the graph.
        """
        return [a for a in self._edges()]

    def _edges(self):
        for n, neighbors in self.node_neighbors.items():
            for neighbor in neighbors:
                yield (n, neighbor)

    def has_node(self, node):
        return node in self.node_neighbors

    def add_node(self, node, attrs={}):
        if attrs is None:
            attrs = []
        if (node not in self.node_neighbors):
            self.node_neighbors[node] = []
            self.node_incidence[node] = []
            self.node_attrs[node] = attrs
        else:
            raise AdditionError("Node %s already in digraph" % node)

    def add_edge(self, edge, wt=1, label=""):
        """
        Add an directed edge to the graph connecting two nodes.

        An edge, here, is a pair of nodes like C{(n, m)}.
        """
        u, v = edge
        for n in [u, v]:
            if not n in self.node_neighbors:
                raise AdditionError("%s is missing from the node_neighbors" % n)
            if not n in self.node_incidence:
                raise AdditionError("%s is missing from the node_incidence" % n)

        if v in self.node_neighbors[u] and u in self.node_incidence[v]:
            return
        else:
            self.node_neighbors[u].append(v)
            self.node_incidence[v].append(u)

    def node_order(self, node):
        """
        Return the order of the given node.

        @rtype:  number
        @return: Order of the given node.
        """
        return len(self.neighbors(node))

    def __str__(self):
        return "\n".join(
            "(%s, %s)" % (k, v)
            for k, v in self.node_neighbors.items() if v)


def pagerank(graph, dumping_factor=0.85, max_iter=100, min_delta=0.00001):
    """
    Compute and return the PageRank in an directed graph.

    @type  graph: digraph
    @param graph: Digraph.

    @type  dumping_factor: number
    @param dumping_factor: PageRank dumping factor.

    @type  max_iter: number
    @param max_iter: Maximum number of iterations.

    @type  min_delta: number
    @param min_delta: Smallest variation required to have a new iteration.

    @rtype:  Dict
    @return: Dict containing all the nodes PageRank.
    """

    nodes = graph.nodes()
    graph_size = len(nodes)
    if graph_size == 0:
        return {}
    min_value = (1.0-dumping_factor)/graph_size  # value for nodes without inbound links

    # itialize the page rank dict with 1/N for all nodes
    pagerank = dict.fromkeys(nodes, 1.0/graph_size)

    for i in range(max_iter):
        diff = 0  # total difference compared to last iteraction
        # computes each node PageRank based on inbound links
        for node in nodes:
            rank = min_value
            for referring_page in graph.incidents(node):
                rank += dumping_factor * pagerank[referring_page] / len(graph.neighbors(referring_page))

            diff += abs(pagerank[node] - rank)
            pagerank[node] = rank

        #stop if PageRank has converged
        if diff < min_delta:
            break

    return pagerank


def generate_graph():
    """ Generate the directional graph needed to compute pageranks """
    graph = Digraph()
    links = Link.select()
    for link in links:
        if not graph.has_node(link.inbound.id):
            graph.add_node(link.inbound.id, link.inbound)
        if not graph.has_node(link.target.id):
            graph.add_node(link.target.id, link.target)

        graph.add_edge((link.inbound.id, link.target.id))

    return graph


def compute_pagerank():
    """ Compute and write the pagerank ranking into a file """
    g = generate_graph()

    import operator
    pages = sorted(pagerank(g).iteritems(),
                   key=operator.itemgetter(1), reverse=True)

    with open('logs/pagerank.txt', 'w') as f:
        for idx, elem in enumerate(pages):
            f.write(
                ("%6s & %s - %s\n" %
                    (idx, elem, g.node_attrs[elem[0]].url)).encode('utf8'))

#!/usr/bin/env python3
import os
import csv
import pygraphviz

def main():
    nodes = {}
    graphfile = open("graph.csv", "r")
    graph_csv = csv.reader(graphfile)
    for row in graph_csv:
        if ("Node" not in row[0]):
            i = 0
            while (i < len(row)):
                if (i == 0):
                    nodes[row[0]] = Node(row[0])
                    i = i+1
                else:
                    nodes[row[0]].add_remote(remotenode(row[i], row[i+1], row[i+2]))
                    i = i + 3
    G=pygraphviz.AGraph(strict=False,directed=True)
    for node in nodes:
        for rnode in nodes[node].remote:
            if (G.has_edge(rnode.hostname,nodes[node].hostname)):
                G.get_edge(rnode.hostname,nodes[node].hostname).attr['dir']="both"

            else:
                label = '%s:%s' % (rnode.localinterface,rnode.remoteinterface)
                G.add_edge(nodes[node].hostname,rnode.hostname, label = label)
    G.layout(prog='dot')
    G.draw('topology.png',prog='dot')





class Node(object):
    """docstring for Node."""

    def __init__(self, hostname):
        super(Node, self).__init__()
        self.hostname = hostname
        self.remote = []

    def add_remote(self, remote_node):
        self.remote.append(remote_node)

class remotenode(object):
    """docstring for remotenode."""

    def __init__(self, hostname, localinterface, remoteinterface):
        super(remotenode, self).__init__()
        self.hostname = hostname
        self.localinterface = localinterface
        self.remoteinterface = remoteinterface

main()

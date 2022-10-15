#!/usr/bin/env python3
from typing import List
from collections import namedtuple
from dataclasses import make_dataclass
from os.path import dirname
from os.path import join as path_join

LEVELS_DIR = path_join(dirname(__file__), "resources", "data")

Coords = namedtuple("Coords", "x y")
Node = make_dataclass(
    "Node",
    [
        "node_index",
        "coords",
        "pill_index",
        "power_pill_index",
        "neighbors",
        "num_neighbors",
    ],
)


def new_node(
    node_index: int,
    x: int,
    y: int,
    n0: int,
    n1: int,
    n2: int,
    n3: int,
    pill_index: int,
    power_pill_index: int,
) -> Node:
    nb = (n0, n1, n2, n3)
    return Node(
        node_index,
        Coords(x, y),
        pill_index,
        power_pill_index,
        nb,
        sum(n != -1 for n in nb),
    )


class Maze:
    """
    Stores the actual mazes, each of which is simply a connected graph.
    The differences between the mazes are the connectivity
    and the x,y coordinates (used for drawing or to compute
    the Euclidean distance. There are 3 built-in distance functions in
    total: Euclidean, Manhattan and Dijkstra's shortest path distance.
    The latter is pre-computed and loaded, the others are
    computed on the fly whenever getNextDir(-) is called.

    Each maze is stored as a (connected) graph: all nodes have neighbors,
    stored in an array of length 4. The index of the array associates
    the direction the neighbor is located at: '[up,right,down,left]'.
    For instance, if node '9' has neighbors '[-1,12,-1,6]', you can
    reach node '12' by going right, and node 6 by going left.
    The directions returned by the controllers should thus be in {0,1,2,3}
    and can be used directly to determine the next node to go to.
    """

    NODE_NAMES = ["a", "b", "c", "d"]
    DIST_NAMES = ["da", "db", "dc", "dd"]

    def __init__(self, index: int):
        self.graph: List[Node] = []

        # NOTE: self.pills[pill_index] == node_index
        self.pills: List[int] = []
        self.power_pills: List[int] = []
        self.junctions: List[int] = []

        self.distances: List[int] = []

        self.load_nodes(self.NODE_NAMES[index])
        self.load_distances(self.DIST_NAMES[index])

    def load_nodes(self, file_name: int) -> None:
        """Loads all the nodes from files and initializes all maze-specific information."""
        with open(path_join(LEVELS_DIR, file_name)) as file:
            h = file.readline()[:-1].split("\t")
            self.name = h[0]
            self.pac_pos = int(h[1])
            self.lair_pos = int(h[2])
            self.ghost_pos = int(h[3])
            self.graph_size = int(h[4])
            self.pill_count = int(h[5])
            self.power_pill_count = int(h[6])
            self.junction_count = int(h[7])
            self.width = int(h[8])
            self.height = int(h[9])

            for line in file:
                node = new_node(*map(int, line.split("\t")))
                self.graph.append(node)

                if node.pill_index >= 0:
                    self.pills.append(node.node_index)
                elif node.power_pill_index >= 0:
                    self.power_pills.append(node.node_index)

                if node.num_neighbors > 2:
                    self.junctions.append(node.node_index)

    def load_distances(self, file_name: str) -> None:
        """
        Loads the shortest path distances which have been pre-computed.
        The data contains the shortest distance from any node in the maze
        to any other node. Since the graph is symmetric, the symmetries
        have been removed to preserve memory and all distances are stored
        in a 1D array; they are looked-up using getDistance(-).
        """
        with open(path_join(LEVELS_DIR, file_name)) as file:
            for line in file:
                self.distances.append(int(line))

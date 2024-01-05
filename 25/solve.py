from __future__ import annotations
from dataclasses import dataclass, field
import sys

type Vertex = str

class Edge(tuple):
    def __new__(cls, a: Vertex, b: Vertex):
        if a < b:
            return super(Edge, cls).__new__(cls, (a, b))
        else:
            return super(Edge, cls).__new__(cls, (b, a))
        
    def other_end(self, a: Vertex):
        if self[0] == a:
            return self[1]
        else:
            return self[0]

@dataclass
class Graph:
    vertices: set[Vertex] = field(default_factory=set)
    edges: set[Edge] = field(default_factory=set)

    def add_edge(self, edge: Edge):
        self.edges.add(edge)
        self.vertices.add(edge[0])
        self.vertices.add(edge[1])

    def min_cut(self)->Cut:
        weights = {e: 1 for e in self.edges}

        swg = SWGraph(self.vertices, self.edges, weights)

        return swg.minimum_cut()
        
@dataclass
class SWGraph(Graph):
    """Implements the Stoer-Wagner minimum cut algo"""
    weights: dict[Edge, int] = field(default_factory=dict)

    
    def minimum_cut_phase(self)->tuple[Cut, SWGraph|None]:
        """Implements the Stoer-Wagner MinimumCutPhase"""            

        print(f'Entered minimum cut phase with |V| = {len(self.vertices)}')
        if len(self.vertices) == 2:
            return(Cut(list(self.edges), self.weights[next(iter(self.edges))]), None)
        
        vertices: set[Vertex] = set() # This is A in the original paper
        excluded_vertices = list(self.vertices)

        vertices.add(excluded_vertices.pop()) # Add an arbitrary vertex, can be different on each MinimumCutPhase

        connectedness: dict[str, int] = {v: 0 for v in excluded_vertices}
        for e in self.edges:
            (a, b) = e
            if (a in excluded_vertices and b in vertices):
                connectedness[a] += self.weights[e]
            elif (b in excluded_vertices and a in vertices):
                connectedness[b] += self.weights[e]

        while len(excluded_vertices) > 2:
            excluded_vertices.sort(key=lambda x: connectedness[x])
            next_vertex = excluded_vertices.pop()
            vertices.add(next_vertex)
            
            for w in excluded_vertices:
                if Edge(w, next_vertex) in self.edges:
                    connectedness[w] += self.weights[Edge(w, next_vertex)]

        # When we get here, we are at the merging phase
        assert len(excluded_vertices) == 2, f"Expected 2 vertices to merge, found {len(excluded_vertices)}"
        s = excluded_vertices[0]
        t = excluded_vertices[1]

        excluded_edges = list(filter(lambda e: (s in e or t in e) and e != Edge(s, t), self.edges))
        cut = Cut(excluded_edges, sum(self.weights[e] for e in excluded_edges))

        new_vertex = ','.join(excluded_vertices)
        vertices.add(new_vertex)

        edges: set[Edge] = set()
        weights: dict[Edge, int] = {}
        for e in self.edges:
            if s in e:
                if t not in e: # Don't do anything if the edge is s-t
                    new_edge = Edge(new_vertex, e.other_end(s))
                    if new_edge in weights:
                        weights[new_edge] += self.weights[e]
                    else:
                        weights[new_edge] = self.weights[e]
                        edges.add(new_edge)
    

            elif t in e:
                new_edge = Edge(new_vertex, e.other_end(t))
                if new_edge in weights:
                    weights[new_edge] += self.weights[e]
                else:
                    weights[new_edge] = self.weights[e]
                    edges.add(new_edge)

            else: # Neither end is s or t
                edges.add(e)
                weights[e] = (self.weights[e])
        
        return (cut, SWGraph(vertices, edges, weights=weights))
    
    def minimum_cut(self)->Cut:
        c, g = self.minimum_cut_phase()
        min_cut = c
        while g:
            #print(c)
            #print(g)
            c, g = g.minimum_cut_phase()
            if c.weight < min_cut.weight:
                min_cut = c
        
        #print(c)
        return min_cut
        
    @classmethod
    def from_graph(cls, g:Graph):
        weights = {e: 1 for e in g.edges}
        swg = SWGraph(g.vertices, g.edges, weights)
        return swg
    

@dataclass
class Cut:
    edges: list[Edge]
    weight: int

class Solver():
    def __init__(self, filename: str):
        self.graph = Graph()
        with open(filename, 'r') as f:
            for line in f:
                src, dsts = line.strip().split(':')
                for dst in dsts.split():
                    self.graph.add_edge(Edge(src, dst))

        print(f'Loaded the graph with |V|={len(self.graph.vertices)} and |E|={len(self.graph.edges)}')

    def solve1(self):
        # swg = SWGraph.from_graph(self.graph)
        # swg.minimum_cut_phase()
        # return 0
        cut = self.graph.min_cut()
        removed_edges = []
        for e in cut.edges:
            a = e[0].split(',')
            b = e[1].split(',')

            for v1 in a:
                for v2 in b:
                    if Edge(v1, v2) in self.graph.edges:
                        removed_edges.append(Edge(v1, v2))        
        
        assert len(removed_edges) == 3, f'Expected 3 edges, got {len(removed_edges)}'

        edges = self.graph.edges
        for e in removed_edges:
            edges.remove(e)
        
        visited: set[Vertex] = set()
        work_queue: list[Vertex] = list()
        work_queue.append(removed_edges[0][0]) # Grab an arbitrary vertex

        while work_queue:
            current = work_queue.pop()
            if current in visited:
                continue

            visited.add(current)
            for e in edges:
                if current in e:
                    other = e.other_end(current)
                    if other not in visited:
                        work_queue.append(other)

        unvisited = self.graph.vertices.difference(visited)

        print(f'Visisted: {visited}')
        print(f'Unvisited: {unvisited}')

        assert len(visited) + len(unvisited) == len(self.graph.vertices), "Number of vertices doesn't match up"

        return len(visited) * len(unvisited)

    def solve2(self):
        v = set(str(x) for x in range(1, 9))
        w = {}
        w[Edge('1', '2')] = 2
        w[Edge('1', '5')] = 3

        w[Edge('2', '3')] = 3
        w[Edge('2', '5')] = 2
        w[Edge('2', '6')] = 2

        w[Edge('3', '4')] = 4
        w[Edge('3', '7')] = 2

        w[Edge('4', '7')] = 2
        w[Edge('4', '8')] = 2

        w[Edge('5', '6')] = 3

        w[Edge('6', '7')] = 1

        w[Edge('7', '8')] = 3

        e = set(w.keys())

        swg = SWGraph(v, e, w)

        return swg.minimum_cut()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"First Solution: {solver.solve1()}")
    #print(f"Second Solution: {solver.solve2()}")
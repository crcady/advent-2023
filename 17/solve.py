from __future__ import annotations
import heapq
import sys

class Node:
    def __init__(self, name, edges: list[tuple]):
        self.name = name
        self.edges = edges
        self.distance = float('inf')

    def __lt__(self, other: Node):
        return self.distance < other.distance
    
    def set_distance(self, dist: int):
        self.distance = dist
    
class Graph:
    def __init__(self):
        self.vertex_names = set() # Set of any type
        self.edges = set() # Set of 3-tuples (src, dst, cost)
        
    def add_edge(self, v1, v2, cost=1):
        self.vertex_names.add(v1)
        self.vertex_names.add(v2)
        self.edges.add((v1, v2, cost))

    def solve(self, start, end):
        edge_lists = {name: [] for name in self.vertex_names}

        for (src, dst, cost) in self.edges:
            edge_lists[src].append((dst, cost))
        
        remaining: list[Node] = []
        node_dict: dict[any, Node]= {}

        for key, value in edge_lists.items():
            node = Node(key, value)
            if key == start:
                node.set_distance(0)

            remaining.append(node)
            node_dict[key] = node

        print(f"Starting to solve a graph with {len(self.edges)} edges and {len(remaining)} nodes")
        remaining.sort()
        assert remaining[0].distance == 0, "Start node distance isn't 0"

        current = remaining.pop(0)
        while current.name != end:
            tainted = False
            for (dst, cost) in current.edges:
                if current.distance + cost < node_dict[dst].distance:
                    tainted = True
                    node_dict[dst].set_distance(current.distance + cost)
            if tainted:
                remaining.sort()

            current = remaining.pop(0)

        return current.distance
        

class Solver():
    def __init__(self, filename: str):
        with open(filename, 'r') as f:
            self.board = [list(line.strip()) for line in f.readlines()]
            self.height = len(self.board)
            self.width = len(self.board[0])

    def lookup(self, coord)->int:
        x, y = coord
        return int(self.board[x][y])
        
    def solve0(self):
        # This solves the *unconstrained* case, which is no greater than the constrained solution
        g = Graph()
        for i in range(self.height):
            for j in range(self.width):
                cost = self.lookup((i, j))
                # From Above
                if i > 0:
                    g.add_edge((i - 1, j), (i, j), cost)

                # From Below
                if i < self.height - 1:
                    g.add_edge((i + 1, j), (i, j), cost)

                # From Left
                if j > 0:
                    g.add_edge((i, j-1), (i, j), cost)

                # From Right
                if j < self.width - 1:
                    g.add_edge((i, j+1), (i, j), cost)
        
        return g.solve(start=(0, 0), end=(self.height-1, self.width-1))
        
    def solve1(self):
        # This solves the *constrained* case, which has 12x as many vertices
        # For each vertex (i, j), create 12 new vertices instead:
        # (i, j, 'N'), (i, j, 'NN'), (i, j, 'NNN'), ..., (i, j, 'WWW')
        #
        # Then, create 8 edges instead of 1:
        # When handingling travel heading 'N' ("From Below"):
        # - There are no incoming edges from the (src, 'NNN') source vertex (no-long-path constraint)
        # - The (src, 'N') maps to (dst, 'NN') and 'NN' to 'NNN' (increase straight path length by one)
        # - There are no edges from 'S', 'SS', or 'SSS' (no-backing-up constraint)
        # - All 'E' and 'W' nodes from the south map to the (dst, 'N') vertex
        #
        # Do the above for all four directions
        #
        # This results in a graph with 12x as many vertices (some unreachable) and 8x as many edge
        #
        # Create a single start node that can go to either (0, 1, 'E') or (1, 0, 'S') (only 2 possible first steps)
        #
        # Create a single end node with a free path from all 12 bottom-right nodes to the end

        def extend(a:tuple, b:any):
            """Given tuple a and item b, extend a by adding b at the end"""
            return a + (b,)

        g = Graph()

        # Add up to 12 vertices for each board square
        for i in range(self.height):
            for j in range(self.width):
                current = (i, j)

                cost = self.lookup(current)
                # From Above
                if i > 0:
                    dst = extend(current, 'S')
                    src = (i - 1, j)

                    # [N]orth
                    # Skip, because N->S would be a backtrack

                    # [E]ast
                    for path in ['E', 'EE', 'EEE']:
                        g.add_edge(extend(src, path), dst, cost)

                    # [S]outh
                    g.add_edge(extend(src, 'S'), extend(current, 'SS'), cost)
                    g.add_edge(extend(src, 'SS'), extend(current, 'SSS'), cost)

                    # [W]est
                    for path in ['W', 'WW', 'WWW']:
                        g.add_edge(extend(src, path), dst, cost)

                # From Below
                if i < self.height - 1:
                    dst = extend(current, 'N')
                    src = (i + 1, j)

                    # [N]orth
                    g.add_edge(extend(src, 'N'), extend(current, 'NN'), cost)
                    g.add_edge(extend(src, 'NN'), extend(current, 'NNN'), cost)

                    # [E]ast
                    for path in ['E', 'EE', 'EEE']:
                        g.add_edge(extend(src, path), dst, cost)

                    # [S]outh
                    # Skip, S->N is a backtrack

                    # [W]est
                    for path in ['W', 'WW', 'WWW']:
                        g.add_edge(extend(src, path), dst, cost)


                # From Left
                if j > 0:
                    dst = extend(current, 'E')
                    src = (i, j-1)

                    # [N]orth
                    for path in ['N', 'NN', 'NNN']:
                        g.add_edge(extend(src, path), dst, cost)

                    # [E]ast
                    g.add_edge(extend(src, 'E'), extend(current, 'EE'), cost)
                    g.add_edge(extend(src, 'EE'), extend(current, 'EEE'), cost)

                    # [S]outh
                    for path in ['S', 'SS', 'SSS']:
                        g.add_edge(extend(src, path), dst, cost)

                    # [W]est
                    # Skip, W->E is a backtrack

                # From Right
                if j < self.width - 1:
                    dst = extend(current, 'W')
                    src = (i, j+1)

                    # [N]orth
                    for path in ['N', 'NN', 'NNN']:
                        g.add_edge(extend(src, path), dst, cost)

                    # [E]ast
                    # Skip, E->W is a backtrack

                    # [S]outh
                    for path in ['S', 'SS', 'SSS']:
                        g.add_edge(extend(src, path), dst, cost)

                    # [W]est
                    g.add_edge(extend(src, 'W'), extend(current, 'WW'), cost)
                    g.add_edge(extend(src, 'WW'), extend(current, 'WWW'), cost)
                
        # End of loop across the entire board    
        
        # Create a start node
        g.add_edge("start", (0, 1, 'E'), self.lookup((0, 1)))
        g.add_edge("start", (1, 0, 'S'), self.lookup((1, 0)))

        # Create an end node
        coord = (self.height - 1, self.width - 1)
        for letter in ['N', 'E', 'S', 'W']:
            for count in [1, 2, 3]:
                src = extend(coord, letter*count)
                g.add_edge(src, "end", 0)
        
        return g.solve("start", "end")

    def newSolve1(self, min_walk: int, max_walk: int):
        """Solves the constrained case"""
        g = Graph()

        # Create two nodes for each (x, y) coordinate in the board: one for horizontal arrivals and one for vertical arrivals.
        # For nodes that were arrived at via a horizontal walk, you may only exit vertically. The converse is also true.

        # Outgoing edges are of length min_walk <= length <= max_walk and have weight equal to the sum of the arrival costs.
        for i in range(self.height):
            for j in range(self.width):
                h_src = (i, j, True) # Horizontal arrival, vertical exit
                v_src = (i, j, False) # Vertical arrival, horizontal exit
                for offset in range(min_walk, max_walk + 1): # Includes min_walk and max_walk
                    if i - offset >  -1: # Walk north
                        cost = sum(self.lookup((i-k, j)) for k in range(1, offset+1))
                        g.add_edge(h_src, (i-offset, j, False), cost)

                    if i + offset < self.height: # Walk south
                        cost = sum(self.lookup((i+k, j)) for k in range(1, offset+1))
                        g.add_edge(h_src, (i+offset, j, False), cost)

                    if j - offset >  -1: # Walk west
                        cost = sum(self.lookup((i, j-k)) for k in range(1, offset+1))
                        g.add_edge(v_src, (i, j-offset, True), cost)

                    if j + offset < self.width: # Walk east
                        cost = sum(self.lookup((i, j+k)) for k in range(1, offset+1))
                        g.add_edge(v_src, (i, j+offset, True), cost)
        
        # Need two start nodes: one where we land at (0, 0) vertically and one where we land at (0, 0) horizontally
        g.add_edge("start", (0, 0, True), 0)
        g.add_edge("start", (0, 0, False), 0)

        # Likewise, we need two end nodes
        g.add_edge((self.height - 1, self.width - 1, True), "end", 0)
        g.add_edge((self.height - 1, self.width - 1, False), "end", 0)
        
        return g.solve("start", "end")
    
    def solve2(self):
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    #print(f"Zero Solution: {solver.solve0()}")
    #print(f"First Solution: {solver.solve1()}")
    print(f"Faster first solution: {solver.newSolve1(1, 3)}")
    print(f"Second Solution: {solver.newSolve1(4, 10)}")
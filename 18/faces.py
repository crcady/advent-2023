from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class Entry:
    dir:    str
    length: int
    color:  int


@dataclass(eq=True, frozen=True)
class Vertex:
    x: int
    y: int


@dataclass(eq=True, frozen=True)
class Edge:
    v1: Vertex
    v2: Vertex
    active: bool = field(compare=False)

    def horizonal(self) -> bool:
        return self.v1.y == self.v2.y
    
    def vertical(self) -> bool:
        return not self.horizonal()
    
    def contains(self, v: Vertex) -> bool:
        if self.horizonal():
            if self.v1.y != v.y:
                return False
            
            if v.x >= self.v1.x and v.x <= self.v2.x:
                return True
            
            return v.x >= self.v2.x and v.x <= self.v1.x
        else:
            if self.v1.x != v.x:
                return False
            
            if v.y >= self.v1.y and v.y <= self.v2.y:
                return True
            
            return v.y >= self.v2.y and v.y <= self.v1.y

    def count(self) -> int:
        if self.horizonal():
            return abs(self.v1.x - self.v2.x) - 1
        else:
            return abs(self.v1.y - self.v2.y) - 1

def make_edge(v1: Vertex, v2: Vertex, active: bool) -> Edge:
    if v1.x <= v2.x and v1.y <= v2.y:
        return Edge(v1, v2, active)
    else:
        return Edge(v2, v1, active)
            
@dataclass(eq=True, frozen=True)
class Face:
    top:    Edge
    right:  Edge
    bottom: Edge
    left:   Edge

    def count(self) -> int:
        height = abs(self.right.v1.y - self.right.v2.y)
        width = abs(self.top.v1.x - self.top.v2.x)
        return (height - 1) * (width - 1)

class Graph:
    """Holds and extends a graph that contains vertices and edges. Does computations regarding the faces of that graph."""
    def __init__(self):
        self.edges: set[Edge] = set()
        self.current = Vertex(0, 0)
        self.vertices = set([self.current])
        self.perimeter = 0

    def add_entry(self, entry: Entry):
        match entry.dir:
            case "R":
                new_vertex = Vertex(self.current.x + entry.length, self.current.y)
            case "L":
                new_vertex = Vertex(self.current.x - entry.length, self.current.y)
            case "D":
                new_vertex = Vertex(self.current.x, self.current.y + entry.length)
            case "U":
                new_vertex = Vertex(self.current.x, self.current.y - entry.length)

        self.vertices.add(new_vertex)
        self.edges.add(make_edge(self.current, new_vertex, True))
        self.current = new_vertex

        self.perimeter += entry.length

    def extend(self):
        assert self.current == Vertex(0, 0), "Not back at the beginning!"

        x_valset: set[int] = set()
        y_valset: set[int] = set()

        for v in self.vertices:
            x_valset.add(v.x)
            y_valset.add(v.y)

        x_vals: list[int] = list(x_valset)
        y_vals: list[int] = list(y_valset)

        x_vals.sort()
        y_vals.sort()

        new_vertices: set[Vertex] = set()
        new_edges: set[Edge] = set()

        for x in x_vals:
            for y in y_vals:
                new_vertices.add(Vertex(x, y))


        for y in y_vals:
            last_x = x_vals[0]
            for x in x_vals[1:]:
                v1 = Vertex(last_x, y)
                v2 = Vertex(x, y)
                active = False
                for e in self.edges:
                    if e.contains(v1) and e.contains(v2):
                        active = True
                        break
                new_edges.add(make_edge(v1, v2, active))
                last_x = x

        
        for x in x_vals:
            last_y = y_vals[0]
            for y in y_vals[1:]:
                v1 = Vertex(x, last_y)
                v2 = Vertex(x, y)
                active = False

                for e in self.edges:
                    if e.contains(v1) and e.contains(v2):
                        active = True
                        break
                new_edges.add(make_edge(v1, v2, active))
                last_y = y

        self.edges = new_edges
        self.vertices = new_vertices

    def count(self) -> int:
        # Every edge has either one or two faces that are adjacent to it
        # Every face has at least two neighbors, and most faces have four

        x_min, x_max, y_min, y_max = 0, 0, 0, 0
        for v in self.vertices:
            x_min = min(x_min, v.x)
            x_max = max(x_max, v.x)
            y_min = min(y_min, v.y)
            y_max = max(y_max, v.y)
        
        x_vals = list(set(v.x for v in self.vertices))
        y_vals = list(set(v.y for v in self.vertices))

        x_vals.sort()
        y_vals.sort()

        active_edges: set[Edge] = set()

        for e in self.edges:
            if e.active:
                active_edges.add(e)

        faces: list[Face] = []
        last_x = x_vals[0]
        for x in x_vals[1:]:
            last_y = y_vals[0]
            for y in y_vals[1:]:
                # a - b
                # |   |
                # c - d
                a = Vertex(last_x, last_y)
                b = Vertex(x, last_y)
                c = Vertex(last_x, y)
                d = Vertex(x, y)

                top = make_edge(a, b, False)
                if top in active_edges:
                    top = make_edge(a, b, True)

                bottom = make_edge(c, d, False)
                if bottom in active_edges:
                    bottom = make_edge(c, d, True)

                left = make_edge(a, c, False)
                if left in active_edges:
                    left = make_edge(a, c, True)

                right = make_edge(b, d, False)
                if right in active_edges:
                    right = make_edge(b, d, True)

                faces.append(Face(top, right, bottom, left))

                last_y = y
            last_x = x

        adjacent: dict[Edge, set[Face]] = {}
        print(f"There are {len(faces)} faces")

        for f in faces:
            for e in [f.bottom, f.left, f.right, f.top]:
                if e not in adjacent:
                    adjacent[e] = set()
                adjacent[e].add(f)
        
        for k, v in adjacent.items():
            if len(v) != 1 and len(v) != 2:
                print("Found a bad entry:", k)

        assert len(adjacent) == len(self.edges), "Not enough entries in adjacency dict"

        first_edge: Edge = None
        for e in self.edges:
            if e.active and e.horizonal() and e.v1.y == y_max:
                first_edge = e
                break

        assert first_edge is not None, "No first edge found"

        counted: set[Face] = set()
        frontier = set(adjacent[first_edge])

        assert len(frontier) == 1, "Unexpected frontier size"

        counted_edges: set[Edge] = set()
        counted_vertices: set[Vertex] = set()

        total = 0
        
        while len(frontier) != 0:
            current = frontier.pop()
            counted.add(current)
            total += current.count()

            for e in [current.bottom, current.left, current.right, current.top]:
                if e not in counted_edges:
                    total += e.count()
                    counted_edges.add(e)

                    for v in [e.v1, e.v2]:
                        if v not in counted_vertices:
                            total += 1
                            counted_vertices.add(v)

                if e.active:
                    continue

                for f in adjacent[e]:
                    if f == current:
                        continue

                    if f not in counted:
                        frontier.add(f)


        print(f"Counted {len(counted)} faces, {len(counted_edges)} edges, and {len(counted_vertices)} vertices")
        return total

    def print(self):
        """Don't do this with big graphs"""
        x_min, x_max, y_min, y_max = 0, 0, 0, 0
        for v in self.vertices:
            x_min = min(x_min, v.x)
            x_max = max(x_max, v.x)
            y_min = min(y_min, v.y)
            y_max = max(y_max, v.y)

        rows: list[list[chr]] = []
        for _ in range (y_min, y_max+1):
            row: list[chr] = []
            for _ in range(x_min, x_max+1):
                row.append('.')
            rows.append(row)

        for e in self.edges:
            if e.vertical():
                x = e.v1.x
                if e.v1.y < e.v2.y:
                    start = e.v1.y
                    end = e.v2.y+1
                else:
                    start = e.v2.y
                    end = e.v1.y+1
                for y in range(start, end):
                    if e.active:
                        rows[y-y_min][x-x_min] = '|'
                    else:
                        rows[y-y_min][x-x_min] = 'x'

            else:
                y = e.v1.y
                if e.v1.x < e.v2.x:
                    start = e.v1.x
                    end = e.v2.x+1
                else:
                    start = e.v2.x
                    end = e.v1.x+1
                for x in range(start, end):
                    if e.active:
                        rows[y-y_min][x-x_min] = "-"
                    else:
                        rows[y-y_min][x-x_min] = "x"

        for v in self.vertices:
            rows[v.y-y_min][v.x-x_min] = 'o'

        for row in rows:
            s = ''
            for c in row:
                s = s+c
            print(s)



def make_entry(line: str) -> Entry:
    d, l, c = line.strip().split(" ")
    return Entry(d, int(l), int(c[2:-1], 16))

def make_entry2(line: str) -> Entry:
    _, _, hexcode = line.strip().split(" ")
    l = hexcode[2:7]
    d = hexcode[7]
    return Entry({"0": "R", "1": "D", "2": "L", "3": "U"}[d], int(l, 16), 0)

g = Graph()

with open("input", "r") as f:
    for line in f:
        g.add_entry(make_entry2(line))

g.extend()
print(g.count())
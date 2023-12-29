from __future__ import annotations
from dataclasses import dataclass
import sys


@dataclass
class Coord:
    x: int
    y: int
    z: int

    def __str__(self) -> str:
        return f"{self.x},{self.y},{self.z}"

@dataclass
class Brick:
    c1: Coord
    c2: Coord
    idx: int

    def __post_init__(self):
        self._min_x = min(self.c1.x, self.c2.x)
        self._min_y = min(self.c1.y, self.c2.y)
        self._min_z = min(self.c1.z, self.c2.z)
        self._max_x = max(self.c1.x, self.c2.x)
        self._max_y = max(self.c1.y, self.c2.y)
        self._max_z = max(self.c1.z, self.c2.z)

    def min_x(self) -> int:
        return self._min_x

    def max_x(self) -> int:
        return self._max_x

    def min_y(self) -> int:
        return self._min_y

    def max_y(self) -> int:
        return self._max_y

    def min_z(self) -> int:
        return self._min_z

    def max_z(self) -> int:
        return self._max_z

    def collides(self, other: Brick) -> bool:
        return not self.misses(other)

    def misses(self, other: Brick) -> bool:
        return (
            self.min_x() > other.max_x()
            or self.max_x() < other.min_x()
            or self.min_y() > other.max_y()
            or self.max_y() < other.min_y()
        )

    def drop_to(self, base: int) -> Brick:
        delta = self.min_z() - base
        new_c1 = Coord(self.c1.x, self.c1.y, self.c1.z - delta)
        new_c2 = Coord(self.c2.x, self.c2.y, self.c2.z - delta)
        return Brick(new_c1, new_c2, self.idx)

    def __str__(self) -> str:
        return f"{self.c1}~{self.c2}"

class Stack:
    def __init__(self):
        self.bricks: list[Brick] = []

    @classmethod
    def from_bricks(self, bricks: list[Brick]) -> Stack:
        stack = Stack()
        stack.bricks = list(bricks)
        return stack

    def __str__(self) -> str:
        return "\n".join(str(x) for x in self.bricks)

    def settled(self) -> Stack:
        new_bricks: list[Brick] = sorted(self.bricks, key=lambda b: b.min_z())
        update_count = 0

        for i in range(len(new_bricks)):
            current = new_bricks[i]
            base_floor = 1
            for j in range(i):
                candidate = new_bricks[j]

                if current.collides(candidate):
                    base_floor = max(base_floor, candidate.max_z() + 1)

            if base_floor < current.min_z():
                update_count += 1
                new_bricks[i] = current.drop_to(base_floor)

        if update_count > 0:
            new_bricks.sort(key=lambda x: x.min_z())
            return Stack.from_bricks(new_bricks)
        else:
            return self


class Solver:
    def __init__(self, filename: str):
        bricks: list[Brick] = []
        with open(filename, "r") as f:
            count = 1
            for line in f:
                t1, t2 = line.strip().split("~")
                x1, y1, z1 = [int(x) for x in t1.split(",")]
                x2, y2, z2 = [int(x) for x in t2.split(",")]
                bricks.append(Brick(Coord(x1, y1, z1), Coord(x2, y2, z2), count))
                count += 1

        self.initial_stack = Stack.from_bricks(bricks)

    def solve1(self):
        settled = self.initial_stack.settled()

        brick_list = settled.bricks
        supported_by = {b.idx: [] for b in brick_list}

        for upper in brick_list:
            for lower in brick_list:
                if upper.min_z() == lower.max_z() + 1 and upper.collides(lower):
                    supported_by[upper.idx].append(lower.idx)

        key_bricks = set()
        for b, support_list in supported_by.items():
            if len(support_list) == 1:
                key_bricks.add(support_list[0])

        return len(brick_list) - len(key_bricks)

    def solve2(self):
        pass


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"First Solution: {solver.solve1()}")
    print(f"Second Solution: {solver.solve2()}")

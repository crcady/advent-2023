from __future__ import annotations
import sys

type Coord = tuple[int, int]


class Cube:
    """Represents a single cubic meter of space."""

    def __init__(self, coord: Coord):
        self.coord = coord


class Segment:
    """A segment that is made of cubes"""

    def __init__(
        self,
        start: Coord,
        length: int,
        direction: str,
        color: str,
        previous: Segment | None,
    ):
        self.start = start
        if direction == "R":
            self.end: Coord = (start[0], start[1] + length)
        elif direction == "L":
            self.end: Coord = (start[0], start[1] - length)
        elif direction == "U":
            self.end: Coord = (start[0] - length, start[1])
        elif direction == "D":
            self.end: Coord = (start[0] + length, start[1])
        else:
            assert False, "Encountered an unexpected direction"

        self.length = length
        self.direction = direction
        self.color = color
        self.previous = previous
        self.next: Segment = None

    def min_x(self) -> int:
        """Minimum x value in the segment"""
        return min(self.start[0], self.end[0])

    def min_y(self) -> int:
        """Minimum y value in the segment"""
        return min(self.start[1], self.end[1])

    def max_x(self) -> int:
        """Maximum x value in the segment"""
        return max(self.start[0], self.end[0])

    def max_y(self) -> int:
        """Maximum y value in the segment"""
        return max(self.start[1], self.end[1])

    def shift(self, dx: int, dy: int):
        """Change (x, y) by (dx, dy) respectively"""
        (start_x, start_y) = self.start
        (end_x, end_y) = self.end
        self.start = (start_x + dx, start_y + dy)
        self.end = (end_x + dx, end_y + dy)

    def cubes(self) -> list[Cube]:
        """Get the list of cubes in the segment"""
        if self.direction == "R":
            return [
                Cube((self.start[0], self.start[1] + x)) for x in range(self.length)
            ]
        if self.direction == "L":
            return [
                Cube((self.start[0], self.start[1] - x)) for x in range(self.length)
            ]
        if self.direction == "U":
            return [
                Cube((self.start[0] - x, self.start[1])) for x in range(self.length)
            ]
        if self.direction == "D":
            return [
                Cube((self.start[0] + x, self.start[1])) for x in range(self.length)
            ]

        assert False, "Encountered an unexpected direction"


class Solver:
    """Parses the input and solves the problem"""

    def __init__(self, filename: str):
        self.segments: list[Segment] = []
        with open(filename, "r") as f:
            current: Segment = None
            for line in f.readlines():
                line = line.strip()
                (direction, length_text, color_text) = line.split()
                length = int(length_text)
                color = color_text[1:-1]

                if current is None:
                    next_start: Coord = (0, 0)
                else:
                    next_start = current.end

                self.segments.append(
                    Segment(next_start, length, direction, color, current)
                )
                if current is not None:
                    current.next = self.segments[-1]
                current = self.segments[-1]

        assert current.end == (0, 0), "Failed to make a loop"
        self.segments[0].previous = current

    def solve1(self):
        """Counts the total volume (aread) dug out"""
        min_x = min(s.min_x() for s in self.segments)
        min_y = min(s.min_y() for s in self.segments)
        max_x = max(s.max_x() for s in self.segments)
        max_y = max(s.max_y() for s in self.segments)

        for s in self.segments:
            s.shift(-min_x + 1, -min_y + 1)

        board: list[list[str]] = [
            list("." * (max_y - min_y + 3)) for _ in range(min_x, max_x + 3)
        ]

        for s in self.segments:
            for c in s.cubes():
                (x, y) = c.coord
                board[x][y] = "#"

        for row in board:
            print("".join(row))

        print("\n---\n")

        # The board is padded on each edge with empty spaces
        # So, we how that (0, 0) is definitely empty and we can propagate out from there
        height = len(board)
        width = len(board[0])
        visited: set[Coord] = set()
        work_queue: list[Coord] = [(0, 0)]

        while work_queue:
            current = work_queue.pop()
            visited.add(current)

            (x, y) = current
            if board[x][y] == "#":
                continue

            board[x][y] = "0"
            if x > 0:  # Up is realistic
                coord = (x - 1, y)
                if coord not in visited:
                    work_queue.append(coord)

            if x < height - 1:  # Down is realistic
                coord = (x + 1, y)
                if coord not in visited:
                    work_queue.append(coord)

            if y > 0:  # Left is realistic
                coord = (x, y - 1)
                if coord not in visited:
                    work_queue.append(coord)

            if y < width - 1:  # Up is realistic
                coord = (x, y + 1)
                if coord not in visited:
                    work_queue.append(coord)

        for row in board:
            print("".join(row))

        return sum(row.count("#") + row.count(".") for row in board)

    def solve2(self):
        pass


class Solver2(Solver):
    """Uses the color hex as the direction and length"""

    def __init__(self, filename):
        self.segments: list[Segment] = []
        with open(filename, "r") as f:
            current: Segment = None
            for line in f.readlines():
                line = line.strip()
                (_, _, color_text) = line.split()
                color_hex = color_text[1:-1]
                length = int(color_hex[1:6], base=16)
                direction = ["R", "D", "L", "U"][int(color_hex[6])]

                if current is None:
                    next_start: Coord = (0, 0)
                else:
                    next_start = current.end

                self.segments.append(
                    Segment(next_start, length, direction, color_hex, current)
                )

                if current is not None:
                    current.next = self.segments[-1]
                current = self.segments[-1]

        assert current.end == (0, 0), f"Failed to make a loop: {current.end}"
        self.segments[0].previous = current


if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)
    solver2 = Solver2(filename)

    print(f"First Solution: {solver.solve1()}")
    print(f"Second Solution: {solver2.solve1()}")

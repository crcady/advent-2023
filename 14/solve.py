from __future__ import annotations
import sys

class Solver():
    def __init__(self, filename: str):
        with open(filename, 'r') as f:
            self.board = [line.strip() for line in f.readlines()]

    def solve1(self):
        columns = [[] for i in range(len(self.board[0]))]

        for row in self.board:
            for i in range(len(row)):
                columns[i].append(row[i])

        for col in columns:
            col_len = len(col)
            idx = 1
            while idx < col_len:
                if col[idx] == 'O':
                    temp_idx = idx
                    while temp_idx > 0 and col[temp_idx - 1] == '.':
                        col[temp_idx], col[temp_idx - 1] = '.', 'O'
                        temp_idx -= 1
                idx += 1
        
        # Convert the column view back to a row view
        tilted = [[] for i in range(len(columns[0]))]
        for col in columns:
            for i in range(len(col)):
                tilted[i].append(col[i])

        self.tilted = tilted

        load = 0
        score = len(tilted)
        for row in tilted:
            load += row.count('O') * score
            score -= 1

        return load
    
    def north(self):
        columns = [[] for i in range(len(self.board[0]))]

        for row in self.board:
            for i in range(len(row)):
                columns[i].append(row[i])

        for col in columns:
            col_len = len(col)
            idx = 1
            while idx < col_len:
                if col[idx] == 'O':
                    temp_idx = idx
                    while temp_idx > 0 and col[temp_idx - 1] == '.':
                        col[temp_idx], col[temp_idx - 1] = '.', 'O'
                        temp_idx -= 1
                idx += 1
        
        # Convert the column view back to a row view
        tilted = [[] for i in range(len(columns[0]))]
        for col in columns:
            for i in range(len(col)):
                tilted[i].append(col[i])

        self.board = tilted

    def south(self):
        columns = [[] for i in range(len(self.board[0]))]

        for row in self.board:
            for i in range(len(row)):
                columns[i].append(row[i])

        for col in columns:
            col_len = len(col)
            idx = col_len - 2
            while idx > -1:
                if col[idx] == 'O':
                    temp_idx = idx
                    while temp_idx < col_len - 1 and col[temp_idx + 1] == '.':
                        col[temp_idx], col[temp_idx + 1] = '.', 'O'
                        temp_idx += 1
                idx -= 1
        
        # Convert the column view back to a row view
        tilted = [[] for i in range(len(columns[0]))]
        for col in columns:
            for i in range(len(col)):
                tilted[i].append(col[i])

        self.board = tilted

    def west(self):
        rows = self.board
        for row in rows:
            row_len = len(row)
            idx = 1
            while idx < row_len:
                if row[idx] == 'O':
                    temp_idx = idx
                    while temp_idx > 0 and row[temp_idx - 1] == '.':
                        row[temp_idx], row[temp_idx - 1] = '.', 'O'
                        temp_idx -= 1
                idx += 1
        
        self.board = rows

    def east(self):
        rows = self.board
        for row in rows:
            row_len = len(row)
            idx = row_len - 2
            while idx > -1:
                if row[idx] == 'O':
                    temp_idx = idx
                    while temp_idx < row_len - 1 and row[temp_idx + 1] == '.':
                        row[temp_idx], row[temp_idx + 1] = '.', 'O'
                        temp_idx += 1
                idx -= 1
        
        self.board = rows

    def total_load(self):
        total_load = 0
        score = len(self.board)
        for row in self.board:
            total_load += row.count('O') * score
            score -= 1

        return total_load

    def cycle(self):
        self.north()
        self.west()
        self.south()
        self.east()

    def as_string(self):
        biglist = []
        for row in self.board:
            biglist.extend(row)

        return ''.join(biglist)

    def solve2(self):
        print("Initial Board:")
        for row in self.board:
            print(''.join(row))
        print("---")

        # print("After 1 cycle:")
        # self.cycle()
        # for row in self.board:
        #     print(''.join(row))
        # print("---")

        # print("After 2 cycles:")
        # self.cycle()
        # for row in self.board:
        #     print(''.join(row))
        # print("---")

        # print("After 3 cycles:")
        # self.cycle()
        # for row in self.board:
        #     print(''.join(row))
        # print("---")

        # self.north()
        # print("After tilting north:")
        # for row in self.board:
        #     print(''.join(row))
        # print("---")

        # self.west()
        # print("After tilting west:")
        # for row in self.board:
        #     print(''.join(row))
        # print("---")

        # self.south()
        # print("After tilting south:")
        # for row in self.board:
        #     print(''.join(row))
        # print("---")

        # self.east()
        # print("After tilting east:")
        # for row in self.board:
        #     print(''.join(row))
        # print("---")

        current = self.as_string()
        its = 0
        seen = set()
        seen2 = set()
        while current not in seen:
            seen.add(current)
            its += 1
            self.cycle()
            current = self.as_string()

        # When we break out of the loop, its is the number of cycles we have completed
        # The current state of the board is the very first repeated state that's been ovserved
        offset = its
        loads = []
        period = 0
        while current not in seen2:
            loads.append(self.total_load())
            seen2.add(current)
            self.cycle()
            current = self.as_string()
            period += 1

        print(loads)
        return loads[(1000000000 - offset) % period]

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"First Solution: {solver.solve1()}")
    print(f"Second Solution: {solver.solve2()}")
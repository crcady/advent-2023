from __future__ import annotations
import sys
import re

def generate_bits(length: int, ones: int):
    current = []
    choices = list(range(length))
    remaining = ones
    indices = generate_indices(current, choices, remaining, [])
    for index_list in indices:
        yield ''.join('#' if i in index_list else '.' for i in range(length))

def generate_indices(current: list[int], choices: list[int], remaining: int, values: list[list[int]])->list[list[int]]:
    if remaining == 0:
        values.append(list(current))
        return values

    choices_copy = list(choices)
    values_copy = list(values)
    while len(choices_copy) > 0:
        next_choice = choices_copy.pop()
        current.append(next_choice)
        values_copy = generate_indices(current, choices_copy, remaining - 1, values)
        current.pop()

    return values_copy

class Group:
    def __init__(self, text:str):
        self.text = text

    def concrete(self):
        return self.text.count('?') == 0
    
    def first_concrete_len(self)->int:
        idx = self.text.find('#')
        if idx == '-1':
            return 0
        
        max_idx = len(self.text) - 2
        count = 1

        while self.text[idx+1] == '#' and idx < max_idx:
            idx += 1
            count += 1
        
        return count

    
    def find_patterns(self, pattern: list[int])->list[tuple[list[int], list[Group]]]:
        """
        Tries to match the next element in the list. Returns a list of (matched prefixes and a remainder group)
        """
        
        print(f"Looking for {pattern} in {self.text}")
        
        # Check for an empty pattern
        if len(pattern) == 0:
            if self.first_concrete_len() == 0:
                return [([], [])] #Skip the whole group (no match/no remainder)
            else:
                return []
            
        # This is pretty simple if we don't have any variables...
        if self.concrete():
            if pattern[0] == len(self.text):
                return [([len(self.text)], [])] #Match the whole group
            else:
                return []
        
        # It's also pretty simple if we're too short to hit the next count...
        if pattern[0] > self.max_length():
            return []
        
        # Or if we're just the right length...
        if pattern[0] == self.max_length():
            patterns = []
            patterns.append(([pattern[0]], [])) # Either we can satisfy it,
            patterns.append(([], [])) # Or we can be skipped entirely
            print(f"Goldilox: {patterns}")
            return patterns
        
        # We can also bail out now if our first concrete string is longer than the next count...
        if self.first_concrete_len() > pattern[0]:
            print("Too Long")
            return []
        
        # Otherwise, we can break ourselves up by inserting some dots
        patterns = []
        for i in range(len(self.text)):
            if self.text[i] == '?':
                left_text = self.text[:i]
                right_text = self.text[i+1:]

                print(f"Complex: split into '{left_text}' and '{right_text}'")
                
                if len(right_text) > 0:
                    right_groups = [Group(right_text)]
                else:
                    right_groups = []

                if len(left_text) > 0:
                    left_group = Group(left_text)
                    left_matches = left_group.find_patterns(pattern)
                    for (ps, gs) in left_matches:
                        print(f"ps: {ps}, gs: {gs}")
                        gs.extend(right_groups)
                        print(f"Complex, appending {(ps, [g.text for g in gs])}")
                        patterns.append((ps, gs))
                else:
                    print(f"Complex: appending {([], right_groups)}")
                    patterns.append(([], right_groups)) #Skip the first ?

        print(f"Complex: returning {patterns}")
        return patterns

    def max_length(self):
        return len(self.text)
    
    def min_sizes(self):
        sizes = []
        current_size = 0
        for character in self.text:
            if character == '#':
                current_size += 1
            else:
                if current_size > 0:
                    sizes.append(current_size)
                    current_size = 0
        if current_size > 0:
            sizes.append(current_size)
        return sizes


class Row:
    def __init__(self, line, unfold=False):
        text, counts = line.split()
        if unfold:
            text = '?'.join([text for i in range(5)])
            counts = ','.join(counts for i in range(5))
        
        self.text:str = text
        self.counts = [int(x) for x in counts.split(',')]

    def make_groups(self):
        groups = []
        current_group = ''
        for char in self.text:
            if char == '.':
                if current_group != '':
                    groups.append(Group(current_group))
                    current_group = ''
            else:
                current_group += char
        if current_group != '':
            groups.append(Group(current_group))

        self.groups = groups

    def search(self)->int:
        self.make_groups()
        return self._search(self.groups[0], self.groups[1:], self.counts)

    def _search(self, group: Group, right: list[Group], counts: list[int])->int:
        n_found = 0
        print(f"entered _search({group.text}, {len(right)} right-groups, {counts})")
        results = group.find_patterns(counts)
        for pattern, remainder in results:
            assert pattern == counts[:len(pattern)], f"{pattern} isn't a prefix to {counts}"
            print(f"Found pattern: {pattern}")

            remaining_groups = list(remainder)
            remaining_groups.extend(right)
            if len(remaining_groups) == 0: # Then we need to match the whole pattern
                if len(pattern) == len(counts):
                    print(f"_search found a pattern!")
                    n_found += 1
                else:
                    pass # Don't need to do anything, we didn't solve it and we're out of patterns
                continue # No more work to do with this pattern
            
            next_group = remaining_groups[0] # We know this exists, because we didn't continue
            next_right = remaining_groups[1:]
            next_counts = counts[len(pattern):]

            n_found += self._search(next_group, next_right, next_counts)

        return n_found
                

    def check(self, string:str)->bool:
        # print(f"Checking {string}")
        current_count = 0
        count_index = 0
        for character in string:
            if character == '#':
                current_count += 1
            else:
                if current_count > 0:
                    if self.counts[count_index] != current_count:
                        # print(f"Bail 1: {current_count} doesn't match {self.counts[count_index]}")
                        return False
                    
                    # print(f"Found a group of size {current_count}")
                    current_count = 0
                    count_index += 1
        
        # At this point we've mading it through the string
        if count_index < len(self.counts)-1:
            # This means that we didn't find enough groups
            # print(f"Bail 2: {count_index} is not {len(self.counts) - 1}")
            return False
        
        if current_count > 0:
            # print(f"Bail 3: comparing {current_count} and {self.counts[count_index]}")
            happy = self.counts[count_index] == current_count
            # print(f"{happy}")
            return happy
        
        # print("Didn't bail\n")
        return True
    
    def count(self):
        num_vars = self.text.count('?')
        num_true = sum(self.counts)
        num_fixed = self.text.count('#')
        bits_needed = num_true - num_fixed
        
        max_num = pow(2, num_vars)
        fstring = "0" + str(num_vars) + "b"

        num_solutions = 0

        for generated in generate_bits(num_vars, bits_needed):
            # print(f"Generated values were: {generated}")
            count = 0
            string = ""

            for character in self.text:
                if character == '?':
                    string += generated[count]
                    count += 1
                else:
                    string += character

            # print(string)

            if self.check(string):
                num_solutions += 1
        
        return num_solutions


class Solver:
    def __init__(self, filename: str):
        self.rows: list[Row] = []
        self.rows2: list[Row] = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                self.rows.append(Row(line))
                self.rows2.append(Row(line, unfold=True))


    def solve1(self):
        sols = [row.count() for row in self.rows]
        print(sols)
        return sum(sols)
    
    def solve2(self):
        r = self.rows2[0]
        print(r.text)
        print(r.counts)
        r = self.rows[0]
        print(f"Trying to solve {r.text}")
        return r.search()
        return 0
        sols = [row.count() for row in self.rows2[0:1]]

        print(sols)
        return sum(sols)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "tiny_input"

    solver = Solver(filename)

    print(f"First Solution: {solver.solve1()}")
    #print(f"Second Solution: {solver.solve2()}")
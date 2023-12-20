
class Group:
    def __init__(self, text:str):
        self.text = text

    def all_patterns(self)->list[list[int]]:
        bit_count = self.text.count('?')
        width = len(self.text)
        if bit_count == 0:
            return[[width]]
        
        patterns = []
        strings = self.hash_strings(bit_count)
        for string in strings:
            temp = ['' for _ in range(width)]
            j = 0
            for i in range(width):
                if self.text[i] == '?':
                    temp[i] += string[j]
                    j += 1
                else:
                    temp[i] += self.text[i]
            
            patterns.append(self.pattern(''.join(temp)))

        return patterns

    def hash_strings(self, length:int):
        max_num = pow(2, length)
        current = 0
        fstring = '0' + str(length) + 'b'
        while current < max_num:
            bits = format(current, fstring)
            yield ['#' if x == '1' else '.' for x in bits]
            current += 1

    def pattern(self, concrete:str):
        counts: list[int] = []
        current = 0
        for i in range(len(concrete)):
            if concrete[i] == '#':
                current += 1
            elif current > 0:
                counts.append(current)
                current = 0
        if current > 0:
            counts.append(current)

        return counts

class Row:
    def __init__(self, rawtext:str):
        text, pattern = rawtext.split()
        self.pattern = [int(p) for p in pattern.split(',')]
        self.groups = [Group(x) for x in text.split('.') if x]
        print(f"Found {len(self.groups)} groups")

    def count(self):
        dict_list:list[dict] = []
        for g in self.groups:
            patterns = [self.p2s(p) for p in g.all_patterns()]
            dict_list.append({x: patterns.count(x) for x in set(patterns)})

        target_pattern = self.p2s(self.pattern)
        print(target_pattern)

        print(dict_list)

        tuple_list = [(1, 0)] #(Multiplier, index)
        for d in dict_list:
            next_tuple_list = []
            for string, count in d.items():
                for (m, i) in tuple_list:
                    if target_pattern[i:i+len(string)] == string:
                        next_tuple_list.append((m*count, i+len(string)))
            tuple_list = list(next_tuple_list)

        return sum(x for x, n in tuple_list if n == len(target_pattern))
        
    def p2s(self, pattern:list[int])->str:
        s = ''
        offset = ord('a')-1
        for num in pattern:
            s += chr(offset+num)
        return s
        
if __name__=="__main__":
    row = Row(".????#?????.?????.? 8,3")
    print(row.count())
from __future__ import annotations
import re


class SpringGroup:
    def __init__(self, group: str):
        self.size = len(group)
        self.type = {'.': "operational", '#': "damaged", '?': "unknown"}[group[0]]

    def is_operational(self) -> bool:
        return self.type == "operational"
    
    def is_damaged(self) -> bool:
        return self.type == "damaged"
    
    def is_unknown(self) -> bool:
        return self.type == "unknown"
    
    def shrink(self, n: int) -> SpringGroup:
        return SpringGroup(str(self)[n:])
    
    def __str__(self):
        c = {"operational": ".", "damaged": "#", "unknown": "?"}[self.type]
        return c * self.size
    
    def __repr__(self):
        return self.__str__()

def parse_spring_groups(line: str) -> list[SpringGroup]:
    m = re.findall(r"\?+|\.+|#+", line)
    return [SpringGroup(x) for x in m]


def parse_groupings(line:str) -> list[int]:
    return [int(x) for x in line.split(",")]


def parse_line(line: str) -> tuple[list[SpringGroup], list[int]]:
    first, second = line.split(" ")
    return parse_spring_groups(first), parse_groupings(second)


def parse_folded(line: str) -> tuple[list[SpringGroup], list[int]]:
    first, second = line.split(" ")
    new_first = "?".join(first for _ in range(5))
    new_second = ",".join(second.strip() for _ in range(5))
    return parse_spring_groups(new_first), parse_groupings(new_second)

def count_ways(sgs: list[SpringGroup], damaged: list[int], in_group: bool, cache: dict[str, int]|None=None) -> int:
    if cache is not None:
        as_str = "".join(str(sg) for sg in sgs) + " " + ",".join(str(x) for x in damaged) + " " + str(in_group)
        if as_str in cache:
            cache["hits"] = cache["hits"] + 1
            return cache[as_str]
        
        cache["misses"] = cache["misses"] + 1

        def ret_fun(n: int) -> int:
            cache[as_str] = n
            return n
    else:
        def ret_fun(n: int) -> int:
            return n
    
    if len(damaged) == 0:
        for sg in sgs:
            if sg.is_damaged():
                return ret_fun(0)
            
        return ret_fun(1)
    
    if len(sgs) == 0:
        return ret_fun(0)
    
    current_group = sgs[0]

    if current_group.is_operational():
        if in_group:
            return ret_fun(0)
        else:
            return ret_fun(count_ways(sgs[1:], damaged, False, cache))
    
    springs_needed = damaged[0]

    if current_group.is_damaged():
        if current_group.size > springs_needed:
            return ret_fun(0)
        
        if current_group.size == springs_needed:
            if len(sgs) == 1:
                if len(damaged) == 1:
                    return ret_fun(1)
                else:
                    return ret_fun(0)
            
            next_group = sgs[1]
            if next_group.is_operational():
                return ret_fun(count_ways(sgs[2:], damaged[1:], False, cache))
            else: # next group is Unknown
                if next_group.size == 1:
                    return ret_fun(count_ways(sgs[2:], damaged[1:], False, cache))
                else:
                    new_sgs = list(sgs[1:])
                    new_sgs[0] = new_sgs[0].shrink(1)
                    return ret_fun(count_ways(new_sgs, damaged[1:], False, cache))
        
        # If we get here, then we need the current group plus part of the next group
        new_damaged = list(damaged)
        new_damaged[0] = new_damaged[0] - current_group.size

        return ret_fun(count_ways(sgs[1:], new_damaged, True, cache))
    
    # If we get here, then we're in the "interesting" case of being in an unknown group
    # Either the first spring is operational, in which case we shrink the size of the group by 1 and continue
    # Or it is not operational, which means we need to match the next group of damaged springs

    first_op = 0
    if not in_group:
        if current_group.size > 1:
            new_sgs = list(sgs)
            new_sgs[0] = new_sgs[0].shrink(1)
            first_op = count_ways(new_sgs, damaged, False, cache)
        else:
            first_op = count_ways(sgs[1:], damaged, False, cache)
    
    if current_group.size < springs_needed:
        new_damaged = list(damaged)
        new_damaged[0] = new_damaged[0] - current_group.size
        return ret_fun(first_op + count_ways(sgs[1:], new_damaged, True, cache))
    
    if current_group.size == springs_needed:
        if len(sgs) == 1:
            if len(damaged) == 1:
                return ret_fun(first_op + 1)
            else:
                return ret_fun(first_op)
            
        
        next_group = sgs[1]

        if next_group.is_operational():
            return ret_fun(first_op + count_ways(sgs[2:], damaged[1:], False, cache))
        else:
            return ret_fun(first_op)
        

    if current_group.size == springs_needed + 1:
        return ret_fun(first_op + count_ways(sgs[1:], damaged[1:], False, cache))
    
    new_sgs = list(sgs)
    new_sgs[0] = new_sgs[0].shrink(springs_needed+1)

    return ret_fun(first_op + count_ways(new_sgs, damaged[1:], False, cache))


with open("tiny_input") as f:
    for line in f:
        sgs, dmg = parse_folded(line)
        cache: dict[str, int] = {"hits": 0, "misses": 0}
        res = count_ways(sgs, dmg, False, cache)
        print(line.strip(), "->", res, cache["hits"], cache["misses"])


ans1 = 0
ans2 = 0
print("")
with open("input") as f:
    for line in f:
        sgs, dmg = parse_line(line)
        sgs2, dmg2 = parse_folded(line)
        res = count_ways(sgs, dmg, False, None)
        cache: dict[str, int] = {"hits": 0, "misses": 0}
        res2 = count_ways(sgs2, dmg2, False, cache)
        ans1 += res
        ans2 += res2

print("First answer:", ans1)
print("Second answer: ", ans2)
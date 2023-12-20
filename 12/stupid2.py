def count(nums: list[int], s: str, last: bool):
    
    next_char = s[0]
    n = nums[0]

    if next_char == '0':
        if n != 0 and last:
            return False
        else:
            next_nums = nums[1:]
            next_s = s[1:]
            next_last = False


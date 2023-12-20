first = None
last = None

def main():
    result = 0
    with open('input', 'r') as f:
        for line in f.readlines():
            temp = getline(line)
            result += temp

    print(result)

def getline(line:str):
    global first
    global last

    first = None
    last = None

    def handle(num: int):
        global first
        global last

        if first == None:
            first = num

        last = num

    length = len(line)
    i = 0
    while i < length-1:
        if line[i].isdigit():
            handle(int(line[i]))
            i += 1
            continue

        else:
            remaining = length - i
            if remaining > 3:
                word = line[i:i+3]
                if word == "one":
                    handle(1)
                    i += 2
                    continue
                elif word == "two":
                    handle(2)
                    i += 2
                    continue
                elif word == "six":
                    handle(6)
                    i += 2
                    continue
            
            if remaining > 4:
                word = line[i:i+4]
                if word == "four":
                    handle(4)
                    i += 3
                    continue
                elif word == "five":
                    handle(5)
                    i += 3
                    continue
                elif word == "nine":
                    handle(9)
                    i += 3
                    continue

            if remaining > 5:
                word = line[i:i+5]
                if word == "three":
                    handle(3)
                    i = i+4
                    continue
                elif word == "seven":
                    handle(7)
                    i = i+4
                    continue
                elif word == "eight":
                    handle(8)
                    i = i+4
                    continue

        i += 1
        # end of while

    return 10*first + last

if __name__ == '__main__':
    main()
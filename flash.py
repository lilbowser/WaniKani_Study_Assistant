"""


"""

import re
import random

rng = random.SystemRandom()
if __name__ == '__main__':
    print("こんにちわ")

    rounds = 20
    data_store = []
    data_name = "BaseInfo"

    with open(data_name + ".txt", encoding="utf-16") as data:  # , errors='replace'
        for line in data:
            # print(line)

            match = re.findall('(.*)\t(.*)', line)
            if len(match) > 0:
                try:
                    if len(match[0][0]) > 0:
                        data_store.append((match[0][0], match[0][1]))
                    else:
                        # new char class
                        pass
                except:
                    print(match)
                    raise RuntimeError(match)

    data_store_length = len(data_store)
    for n in range(rounds):
        cur_num = rng.randint(0, data_store_length-1)
        print("{}".format(data_store[cur_num][1]))
        guess = input("")
        if guess == data_store[cur_num][0]:
            print("Correct")
        else:
            print("Wrong: Correct answer: {}".format(data_store[cur_num][0]))



input("Press Key To Exit")


from transsurfs.h11 import *
import re
from itertools import product
import signal
from contextlib import contextmanager

surface = TransSurfH11([1, 1, 2], ['A', 'B','B'],['A','A','A'],['A','B','A'])
atk_data = surface.compute_attacks()

first = {'A': -1, 'B': -1}

for i in range(len(surface)):
    if surface[i].label == 'A':
        first['A'] = i
        break
for i in range(len(surface)):
    if surface[i].label == 'B':
        first['B'] = i
        break

atk_formulas = []

for i in range(len(surface)):
    print(surface[i].name(), "->", atk_data[i])

for i in range(len(surface)):
    print(surface[i].name(), "->", pos(surface[i].label + '_0')
                               * (process_attack(atk_data[i]["top"])+process_attack(atk_data[i]["bottom"]))
                               - pos(surface[i].name())
                               * (process_attack(atk_data[first[surface[i].label]]["top"])
                                  + process_attack(atk_data[first[surface[i].label]]["bottom"])))

    atk_formulas.append(pos(surface[i].label + '_0')
                               * (process_attack(atk_data[i]["top"])+process_attack(atk_data[i]["bottom"]))
                               - pos(surface[i].name())
                               * (process_attack(atk_data[first[surface[i].label]]["top"])
                                  + process_attack(atk_data[first[surface[i].label]]["bottom"])))

sols = solve(atk_formulas + [pos('A_0') - 1, pos('B_0') - 1])
init_printing()

pprint(sols)
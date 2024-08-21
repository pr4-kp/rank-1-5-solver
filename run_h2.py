from transsurfs.h2 import *
import re
from itertools import product
import signal
from contextlib import contextmanager
import os

solution_number = 1

# from Paul's email: we won't have to check for rank 1.5s when 
# there is only one cylinder on the top or bottom
cylinder_counts_leq_6 = ([[2, 2]],
                         [[2, 3], [3, 2]], 
                         [[2, 4], [3, 3], [4, 2]],
                         [[2, 5], [3, 4], [4, 3], [5, 2]],
                         [[2, 6], [3, 5], [4, 4], [5, 3], [6, 2]])
scys = [["A", "A"], ["A", "B"], ["B", "A"], ["B", "B"]]


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def process_max(eqn: str) -> list[str]:
    """
    If we have an equation A_0*(Max(A_0,B_0+B_1)), this should create two equations
    A_0*(A_0) (assuming A_0>B_0+B_1) 
    A_0*(B_0+B_1) (assuming A_0<B_0+B_1) 

    Since nothing is attacked from by more than 2 things in one direction, it should 
    be easy to create two equations 
    """
    eqns = [eqn]
    replace = True

    while replace:
        new_eqns = []
        for e in eqns:
            # print(e, re.search(r'Max\(([\w\s+]+),\s*([\w\s+]+)\)', e))
            if re.search(r'Max\(([\w\s+]+),\s*([\w\s+]+)\)', e):
                sub_first_max = re.sub(r'Max\(([\w\s+]+),\s*([\w\s+]+)\)', r'\1', e, count=1)
                sub_second_max = re.sub(r'Max\(([\w\s+]+),\s*([\w\s+]+)\)', r'\2', e, count=1)
                new_eqns += [sub_first_max, sub_second_max]
            else: 
                replace = False
    
        if replace:
            eqns = new_eqns

    return eqns


def create_rel_def_condition(cylinders, number_cylinders):
    # from Paul's email:
    # (sum of heights of A-cylinders in the top cylinder)(sum of heights of B-cylinders in the bottom cylinder)
    # = (sum of heights of A-cylinders in the bottom cylinder)(sum of heights of B-cylinders in the top cylinder).
    a_sum_top = 0
    b_sum_top = 0
    a_sum_bottom = 0
    b_sum_bottom = 0
    for i in range(len(cylinders)):
        if i < number_cylinders[0]:
            if cylinders[i].label == 'A':
                a_sum_top += pos(cylinders[i].name())
            else:
                b_sum_top += pos(cylinders[i].name())
        else:
            if cylinders[i].label == 'A':
                a_sum_bottom += pos(cylinders[i].name())
            else:
                b_sum_bottom += pos(cylinders[i].name())

    rel_def_condition = a_sum_top * b_sum_bottom - b_sum_top * a_sum_bottom
    return rel_def_condition


def generate_mathematica_code(surface: TransSurfH2):

    first = {'A': -1, 'B': -1}

    for i in range(len(surface)):
        if surface[i].label == 'A':
            first['A'] = i
            break
    for i in range(len(surface)):
        if surface[i].label == 'B':
            first['B'] = i
            break

    attack_data = surface.compute_attacks()
    attack_formulas = []

    mathematica_code = ""

    # create attack formulas
    for i in range(len(surface)):
        # Formula: A_0 * (attack_speed A_i) - A_i * (attack_speed A_0) = 0
        attack_formulas.append(pos(surface[i].label + '_0')
                               * (process_attack(attack_data[i]["top"])+process_attack(attack_data[i]["bottom"]))
                               - pos(surface[i].name())
                               * (process_attack(attack_data[first[surface[i].label]]["top"])
                                  + process_attack(attack_data[first[surface[i].label]]["bottom"])))

        mathematica_code += surface[i].name() + ">0,"

        if i not in first.values():
            # print(attack_formulas[i], "=0,", sep='')
            mathematica_code += str(attack_formulas[i]) + "==0,"

    rel_def_condition = create_rel_def_condition(
        surface, surface.number_cylinders)
    mathematica_code += str(rel_def_condition) + "==0,"

    return mathematica_code


def create_sage_code(cylinders, number_cylinders, attack_formulas, f):
    """
    create the sage code and write it to the file f
    """
    sage_code = []
    variable_list = ""

    # add attacks, if there is a max, process_max will split it into multiple formulas 
    for i in range(len(cylinders)):
        sage_code += [process_max(str(attack_formulas[i]))]

    # add the rel deformation condition
    sage_code += [[str(create_rel_def_condition(cylinders, number_cylinders))]]

    for i in range(len(cylinders)):
        variable_list += cylinders[i].name()
        if i != len(cylinders) - 1:
            variable_list += ", "

    init_sage = variable_list + " = QQ[\"" + variable_list + "\"].gens()"

    sage_equations: list[str] = []
    for e in list(product(*sage_code)):
        sage_equations.append(','.join(e))

    f.write("\nFOR SAGE (to convert to Groebner basis):\n")
    f.write(init_sage + "\n")

    f.write("I_list = [")
    for eq in sage_equations:
        f.write("ideal(" + eq + ",A_0-1,B_0-1),\n")
    f.write("]\n")


def generate(surface: TransSurfH2, file_name):
    # chop half of the things to test
    if surface.top_cylinders[0] == 'B':
        return
    
    if (surface.number_cylinders[1] == 2 and surface.cylinders[-1].label == surface.cylinders[-2].label):
        return
    
    # devious attacked by 4 cylinders case
    if (surface.number_cylinders[1] == 5 
            and surface.cylinders[-1].label == surface.cylinders[-2].label
            and surface.cylinders[-2].label != surface.cylinders[-3].label
            and surface.cylinders[-3].label != surface.cylinders[-4].label
            and surface.cylinders[-4].label == surface.cylinders[-5].label):
        return

    if (surface.cylinders[0].label == surface.cylinders[-1].label 
        and surface.cylinders[-1].label == surface.cylinders[-2].label):
        return
    
    if (surface.number_cylinders[1] > 3
        and surface.cylinders[-1] == surface.cylinders[surface.number_cylinders[0]] 
        and surface.cylinders[surface.number_cylinders[0]] == surface.cylinders[surface.number_cylinders[0] + 1]):
        return
    
    for i in range(surface.number_cylinders[0] + surface.number_cylinders[1] - 2):
        if (surface.cylinders[i] == surface.cylinders[i + 1] and surface.cylinders[i + 1] == surface.cylinders[i + 2]):
            return

    # we need to find the index of the first A and B cylinder to
    # compare out ratios to (these ones will be assumed to be 1, or our equation will be solve in terms of them)
    first = {'A': -1, 'B': -1}

    for i in range(len(surface)):
        if surface[i].label == 'A':
            first['A'] = i
            break
    for i in range(len(surface)):
        if surface[i].label == 'B':
            first['B'] = i
            break

    # get the attack speed from top and bottom for each cylinder 
    attack_data = surface.compute_attacks()

    for i in range(len(surface)):
        if process_attack(attack_data[i]['top']) + process_attack(attack_data[i]['bottom']) == 0:
            return

    attack_formulas = []

    # print surface details
    print(surface.number_cylinders, surface.top_cylinders, surface.bottom_cylinders, surface.starting_cylinders)
    for i in range(len(surface)):
        print(surface[i].name(), "->", process_attack(attack_data[i]["top"]) +
            process_attack(attack_data[i]["bottom"]))

    # create attack formulas
    for i in range(len(surface)):
        # Formula: A_0 * (attack_speed A_i) - A_i * (attack_speed A_0) = 0
        attack_formulas.append(pos(surface[i].label + '_0')
                            * (process_attack(attack_data[i]["top"])+process_attack(attack_data[i]["bottom"]))
                            - pos(surface[i].name())
                            * (process_attack(attack_data[first[surface[i].label]]["top"])
                            + process_attack(attack_data[first[surface[i].label]]["bottom"])))

    rel_def_condition = create_rel_def_condition(surface, surface.number_cylinders)

    mathematica_code = generate_mathematica_code(surface)

    # write results to file
    f = open(file_name, 'a')
    global solution_number
        
    try:
        # should be faster than just regular solving 
        with time_limit(60):
            sols = solve_poly_system(attack_formulas + [rel_def_condition] + [pos('A_0') - 1, pos('B_0') - 1])
        init_printing()

        if not sols: # no solutions! rule it out
            f.close()
            return
        
        bad_sols = 0
        print(sols)
        for sol in sols:
            if any((not ele.is_real or ele <= 0) for ele in sol):
                bad_sols += 1
        
        # only negative solutions is bad
        if (bad_sols == len(sols)):
            f.close()
            return 

        f.write("-----\n" + str(solution_number) + ". CASE:" + str(surface.number_cylinders) + ' '
                + ' '.join([e.name() for e in surface]) + "\n")
        f.write(str(surface.marked_points) + "\n")
        solution_number += 1

        f.write("\nFOR MATHEMATICA:\n")
        f.write(mathematica_code.replace(" ", "") + "\n")

        create_sage_code(surface, surface.number_cylinders, attack_formulas, f)

        i = 1
        for e in sols:
            f.write("Solution " + str(i) + ":\n")
            f.write(str(e))
            # for k in e:
            #     f.write(str(k) + " = " + str(e[k].evalf()) + "\n")
            i += 1
            f.write("\n")
    except (TimeoutException, NotImplementedError) as e:
        f.write("-----\n" + str(solution_number) + ". CASE:" + str(surface.number_cylinders) + ' '
                + ' '.join([e.name() for e in surface]) + "\n")
        f.write(str(surface.marked_points) + "\n")
        solution_number += 1
        f.write("\nFOR MATHEMATICA:\n")
        f.write(mathematica_code.replace(" ", "") + "\n")

        create_sage_code(surface, surface.number_cylinders, attack_formulas, f)

        f.write("could not solve, try mathematica!\n")

    f.close()

# n1 = 3
# n2 = 2
# top_cylinders = ['A', 'B']
# bottom_cylinders = ['A', 'A']
# starting_cylinders = ['B', 'B']
# surface = TransSurfH2([n1, n2], top_cylinders,
#                       bottom_cylinders, starting_cylinders)
# surface.marked_points[-1] = ['l', 'r']

# for at in surface.compute_attacks():
#     print(at)

for number_configs in cylinder_counts_leq_6:
    for number_cylinders in number_configs:
        for top_cylinders, bottom_cylinders, starting_cylinders in product(scys, scys, scys):
            # switching the labeling of A and B cylinders will result in the same translation surface
            # so only consider when the first cylinder is A
            n1 = number_cylinders[0]
            n2 = number_cylinders[1]

            surface = TransSurfH2([n1, n2], top_cylinders,
                                bottom_cylinders, starting_cylinders)

            modify_marked_points: set[int] = set()
            if (n1 < n1 + 1 and n1 + 1 < n1 + n2):
                modify_marked_points.add(n1 + 1)
            if (n1 < n1 + 2 and n1 + 2 < n1 + n2):
                modify_marked_points.add(n1 + 2)
            if (n1 < n1 + n2 - 2 and n1 + n2 - 2 < n1 + n2):
                modify_marked_points.add(n1 + n2 - 2)
            if (n1 < n1 + n2 - 1 and n1 + n2 - 1 < n1 + n2):
                modify_marked_points.add(n1 + n2 - 1)

            seen_attacks = set()
            to_evaluate = []
            modify_marked_points = list(modify_marked_points)

            marked_pt_configs = list(
                product([['l'], ['r'], ['l', 'r']], repeat=len(modify_marked_points)))

            for config in marked_pt_configs:
                surface = TransSurfH2([n1, n2], top_cylinders,
                                      bottom_cylinders, starting_cylinders)
                for pt_idx in range(len(modify_marked_points)):
                    surface.marked_points[modify_marked_points[pt_idx]] = config[pt_idx]

                if generate_mathematica_code(surface) not in seen_attacks:
                    seen_attacks.add(generate_mathematica_code(surface))
                    to_evaluate.append(surface)
                else:
                    for i in range(len(to_evaluate)):
                        # print(generate_mathematica_code(surface), "\n",
                        #       generate_mathematica_code(to_evaluate[i]))
                        if (generate_mathematica_code(surface) == generate_mathematica_code(to_evaluate[i])):
                            if (surface.number_marked_points() <= to_evaluate[i].number_marked_points()):
                                del to_evaluate[i]
                                to_evaluate.append(surface)
                            break 

            for s in to_evaluate:
                if s.number_marked_points() <= 6:
                    generate(s, os.path.join("h2", "data", str(s.number_marked_points()) + ".txt"))
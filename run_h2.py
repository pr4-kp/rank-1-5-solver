from h2 import *
from itertools import product

# from Paul's email: we won't have to check for rank 1.5s when 
# there is only one cylinder on the top or bottom
ncys4 = [[2,4], [3,3], [4,2]]
ncys3 = [[2, 3], [3, 2]]
scys = [["A", "A"], ["A", "B"], ["B", "A"], ["B", "B"]]


for number_cylinders in ncys3:
    for top_cylinders, bottom_cylinders, starting_cylinders in product(scys, scys, scys):
        # switching the labeling of A and B cylinders will result in the same translation surface,
        # so only consider when the first cylinder is A
        if top_cylinders[0] == 'B':
            continue

        try:
            cylinders = generate_cylinders(
                number_cylinders, top_cylinders, bottom_cylinders, starting_cylinders)
        except ValueError as e:
            print(e)
            continue

        # we need to find the index of the first A and B cylinder to
        # compare out ratios to (these ones will be assumed to be 1, or our equation will be solve in terms of them)
        first = {'A': -1, 'B': -1}

        for i in range(len(cylinders)):
            if cylinders[i].label == 'A':
                first['A'] = i
                break
        for i in range(len(cylinders)):
            if cylinders[i].label == 'B':
                first['B'] = i
                break

        attack_data = compute_attacks(cylinders, number_cylinders)
        attack_formulas = []

        # for each cylinder, print how much attack is coming from the top and bottom 
        # for i in range(len(cylinders)):
        #     print(cylinders[i].name(), "->", process_attack(attack_data[i]["top"]) +
        #         process_attack(attack_data[i]["bottom"]))
        copy_paste_to_mathematica = ""

        variable_list = ""
        copy_paste_to_sage = ""

        for i in range(len(cylinders)):
            # Formula: A_0 * (attack_speed A_i) - A_i * (attack_speed A_0) = 0
            attack_formulas.append(pos(cylinders[i].label + '_0')
                                * (process_attack(attack_data[i]["top"])+process_attack(attack_data[i]["bottom"]))
                                - pos(cylinders[i].name())
                                * (process_attack(attack_data[first[cylinders[i].label]]["top"])
                                + process_attack(attack_data[first[cylinders[i].label]]["bottom"])))
            
            # the solutions are positive
            # print(cylinders[i].name() + ">0,")
            copy_paste_to_mathematica += cylinders[i].name() + ">0,"
            if i not in first.values():
                print(attack_formulas[i], "=0,", sep='')
                copy_paste_to_mathematica += str(attack_formulas[i]) + "==0,"
                copy_paste_to_sage += str(attack_formulas[i]) + ","
        
        copy_paste_to_sage = "I = ideal(" + copy_paste_to_sage + "A_0-1,B_0-1)"
        for i in range(len(cylinders)):
            variable_list += cylinders[i].name() 
            if i != len(cylinders) - 1:
                variable_list += ", "

        init_sage = variable_list + " = QQ[\"" + variable_list + "\"].gens()"

        # write results to file
        with open("solutionstest.txt", 'a') as f:
            f.write("-----\nCASE:" + str(number_cylinders) + ' '
                    + ' '.join([e.name() for e in cylinders]) + "\n")

            f.write("\nFOR MATHEMATICA:\n")
            f.write(copy_paste_to_mathematica.replace(" ", "") + "\n")

            f.write("\nFOR SAGE (to convert to Groebner basis):\n")
            f.write(init_sage + "\n")
            f.write(copy_paste_to_sage + "\n")

            try:
                sols = solve(attack_formulas, exclude=[pos('A_0'), pos('B_0')])
                init_printing()

                i = 1
                for e in sols:
                    f.write("Solution " + str(i) + ":\n")
                    for k in e:
                        f.write(str(k) + " = " + str(e[k].evalf()) + "\n")
                    # pprint(e, use_unicode=True)
                    i += 1
                    f.write("\n")
            except NotImplementedError as e:
                f.write("could not solve, try mathematica!\n")

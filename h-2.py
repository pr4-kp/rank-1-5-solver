from sympy import *

class Cylinder:
    label: str 
    index: int

    def __init__(self, label: str, index: int) -> None:
        self.label = label
        self.index = index

    def name(self) -> str:
        return self.label + "_" + str(self.index)


def pos(num):
    return Symbol(num, positive=True)

def generate_cylinders(number_cylinders: list[int], starting_cylinders: list[str]) -> list[Cylinder]:
    cylinders: list[Cylinder] = []
    a_ct, b_ct = 0, 0 

    for t in range(2):
        for i in range(number_cylinders[t]):
            added_cylinder = starting_cylinders[t]
            if i % 2 == 1:
                if added_cylinder == 'A':
                    added_cylinder = 'B'
                elif added_cylinder == 'B':
                    added_cylinder = 'A'

            if added_cylinder == 'A':
                cylinders.append(Cylinder(added_cylinder, a_ct))
                a_ct += 1
            else: 
                cylinders.append(Cylinder(added_cylinder, b_ct))
                b_ct += 1

    return cylinders


def compute_attacks(cylinders, number_cylinders):
    n = len(cylinders)
    attacks = []

    def check_direction(start, index, direction):
        assert(direction == "top" or direction == "bottom")
        attack = []

        if direction == "bottom":
            if cylinders[index].label != cylinders[(start + 1) % n].label:
                attack = [cylinders[(start + 1) % n].name()]

                if cylinders[index].label != cylinders[(start + 2) % n].label:
                    attack.append(cylinders[(start + 2) % n].name())

        elif direction == "top":
            if cylinders[index].label != cylinders[(start - 1) % n].label:
                attack = [cylinders[(start - 1) % n].name()]

                if cylinders[index].label != cylinders[(start - 2) % n].label:
                    attack.append(cylinders[(start - 2) % n].name())

        attacks[index][direction].append(attack)

    for i in range(n):
        attacks.append({"top": [], "bottom": []})

        # for most cases, it suffices to look up 2 and down 2 and sum it up
        check_direction(i, i, "bottom")
        check_direction(i, i, "top")
        
        # for the first "long" cylinder, it could get attacked from 3 directions
        if i == number_cylinders[0]:
            check_direction(n, i, "top")

        # same for the last "long cylinder"
        if i == n - 1:
            check_direction(number_cylinders[0] - 1, i, "bottom")

    return attacks


def process_attack(attack: dict[str, list]): 
    out = 0
    
    for a in attack:
        part = 0
        for e in a:
            part += pos(e)
        out = Max(out, part)

    return out


number_cylinders = [2,2]  # 1 marked point on top and 2 on bottom
starting_cylinders = ["A", "A"]
cylinders = generate_cylinders(number_cylinders, starting_cylinders)

"""
The above code corresponds to the following translation surface:
┌────────┐                                  
│   A0   │                                  
├────────┤           
│   B0   │ 
├────────┴───────────┐                      
│         B1         │ <-- we should pay special attention to this cylinder,                       
├────────────────────┤     it gets attacked from "3 directions"
│         A1         │                      
├────────────────────┤                      
│         B2         │                      
└────────────────────┘                      
for each cylinder, I want to get how much its being attacked.
- this is computed by the fastest attacking speed on top + fastest attacking speed on bottom
- for example, A1 is being attacked at speed b1 on top and b3 on bottom so A1 will have height 

    a1 - t(b1 + b3)

- all the data i _really_ need is (b1 + b3)      

Fix an A-cylinder C. Let h(t) be the height of C where t > 1. Let s be a vertical line segment that starts at a cone point, travels southward exclusively through B-cylinders before ending at the top boundary of C. The length L of s on X is the sum (with multiplicity) of the heights of the B-cylinders that s passes through. So on X_t (t > 1), s cuts into C a distance of L(t-1). This shows the following.
"""

attacks = compute_attacks(cylinders, number_cylinders)
print(attacks)

for i in range(len(cylinders)):
    print(cylinders[i].name(), " -> ", pos(cylinders[i].name()) - pos('t') *
          (process_attack(attacks[i]["top"])+process_attack(attacks[i]["bottom"])), sep='')

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

def generate_cylinders(number_cylinders: list[int], top_cylinders: list[str], 
                       bottom_cylinders: list[str], starting_cylinders: list[str]) -> list[Cylinder]:
    """
    Given three arrays of length 2 representing the top, bottom, and first cylinder after the top cylinder,
    generate_cylinders creates a list of Cylinder objects that represent the translation surface.

    ┌────────┐
    │   A0   │ <- top_cylinder[0]
    ├────────┤
    │   B0   │  <- bottom_cylinder[0]
    ├────────┴───────────┐
    │         B1         │ <- top_cylinder[1]
    ├────────────────────┤
    │         A1         │ <- starting_cylinder[1]
    ├────────────────────┤
    │         B2         │ <- bottom_cylinder[1]
    └────────────────────┘

    There cannot be only one cylinder in the top/bottom part of the translation surface if it is 
    rank 1.5. The first assertion verifies this.
    
    If there are 3 A/B cylinders in a row, then this cannot be a rank 1.5 translation surface 
    by a cylinder collapsing argument. This function will throw an error in that case. 
    """
    assert(number_cylinders[0] >= 2 and number_cylinders[1] >= 2)

    cylinders: list[Cylinder] = []
    a_ct, b_ct = 0, 0 # using these for labelling the cylinders

    for t in range(2):
        # start by adding the top cylinder
        if top_cylinders[t] == 'A':
            cylinders.append(Cylinder(top_cylinders[t], a_ct))
            a_ct += 1
        else:
            cylinders.append(Cylinder(top_cylinders[t], b_ct))
            b_ct += 1

        # in an alternating fashion, add the middle cylinders
        for i in range(number_cylinders[t] - 2):
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

        # at the end, add the bottom cylinder
        if bottom_cylinders[t] == 'A':
            cylinders.append(Cylinder(bottom_cylinders[t], a_ct))
            a_ct += 1
        else:
            cylinders.append(Cylinder(bottom_cylinders[t], b_ct))
            b_ct += 1

    # check that there are not three cylinders in a row
    for i in range(1, len(cylinders) - 1):
        if cylinders[i-1].label == cylinders[i].label and cylinders[i].label == cylinders[i+1].label:
            raise ValueError(f"There are three {cylinders[i].label} cylinders in a row!")

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

    def check_direction2(start, index, direction):
        assert (direction == "top" or direction == "bottom")
        attack = []
        start -= number_cylinders[0]

        if direction == "bottom":
            if cylinders[index].label != cylinders[(start + 1) % number_cylinders[1] + number_cylinders[0]].label:
                attack = [
                    cylinders[(start + 1) % number_cylinders[1] + number_cylinders[0]].name()]

                if cylinders[index].label != cylinders[(start + 2) % number_cylinders[1] + number_cylinders[0]].label:
                    attack.append(
                        cylinders[(start + 2) % number_cylinders[1] + number_cylinders[0]].name())

        elif direction == "top":
            if cylinders[index].label != cylinders[(start - 1) % number_cylinders[1] + number_cylinders[0]].label:
                attack = [
                    cylinders[(start - 1) % number_cylinders[1] + number_cylinders[0]].name()]

                if cylinders[index].label != cylinders[(start - 2) % number_cylinders[1] + number_cylinders[0]].label:
                    attack.append(
                        cylinders[(start - 2) % number_cylinders[1] + number_cylinders[0]].name())

        attacks[index][direction].append(attack)

    for i in range(n):
        attacks.append({"top": [], "bottom": []})

        # for most cases, it suffices to look up 2 and down 2 and sum it up
        check_direction(i, i, "bottom")
        check_direction(i, i, "top")
        
        # for the first "long" cylinder, it could get attacked from 3 directions
        if i == number_cylinders[0]:
            check_direction2(n, i, "top")

        # same for the last "long cylinder"
        if i == n - 1:
            check_direction2(number_cylinders[0] - 1, i, "bottom")

    return attacks


def process_attack(attack: dict[str, list]): 
    out = 0
    
    for a in attack:
        part = 0
        for e in a:
            part += pos(e)
        out = Max(out, part)

    return out


from sympy import *

class Cylinder:
    label: str 
    index: int

    def __init__(self, label: str, index: int) -> None:
        self.label = label
        self.index = index

    def name(self) -> str:
        return self.label + "_" + str(self.index)


class TransSurfH2:
    cylinders: list[Cylinder]
    number_cylinders: list[int]
    top_cylinders: list[str]
    bottom_cylinders: list[str]
    starting_cylinders: list[str]
    marked_points: list[list[str]]

    def __init__(self, number_cylinders: list[int], top_cylinders: list[str],
                 bottom_cylinders: list[str], starting_cylinders: list[str]):
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

        There cannot be only one cylinder in the top/bottom part of the translation surface of genus 2 if it is 
        rank 1.5. The first assertion verifies this.
        """
        assert (len(number_cylinders) == 2)
        assert (number_cylinders[0] >= 2 and number_cylinders[1] >= 2)

        self.number_cylinders = number_cylinders
        self.bottom_cylinders = bottom_cylinders
        self.top_cylinders = top_cylinders
        self.starting_cylinders = starting_cylinders

        cylinders: list[Cylinder] = []
        a_ct, b_ct = 0, 0  # using these for labelling the cylinders

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

        self.marked_points = [[] for _ in range(len(cylinders))]

        for i in range(len(cylinders)):
            self.marked_points[i].append('l')

        self.cylinders = cylinders

    def __getitem__(self, key: int):
        return self.cylinders[key]
    
    def __len__(self):
        return len(self.cylinders)
    
    def compute_attacks(self) -> list:

        def check_direction(start, direction):
            assert (direction == "top" or direction == "bottom")

            if direction == "bottom":

                down1 = (start + 1) % n
                down2 = (start + 2) % n

                if (start == self.number_cylinders[0] - 1):
                    if (self.number_cylinders[1] > 2 
                            and self[down1].label != self[start].label
                            and self[down2].label != self[start].label 
                            and 'l' in self.marked_points[down2 + 1]):
                        return [self[down1].name(), self[down2].name()]
                    elif (self[down1].label != self[start].label
                          and 'l' in self.marked_points[down1 + 1]):
                        return [self[down1].name()]
                    else: 
                        return []
                elif (start == self.number_cylinders[0] - 2):
                    if (self.cylinders[down1].label != self.cylinders[start].label
                            and self.cylinders[down2].label != self.cylinders[start].label
                            and 'l' in self.marked_points[down2 + 1]):
                        return [self.cylinders[down1].name(), self.cylinders[down2].name()]
                    elif (self.cylinders[down1].label != self.cylinders[start].label):
                        return [self.cylinders[down1].name()]
                    else:
                        return []
                else:
                    if (self.cylinders[down1].label != self.cylinders[start].label
                            and self.cylinders[down2].label != self.cylinders[start].label):
                        return [self.cylinders[down1].name(), self.cylinders[down2].name()]
                    elif (self.cylinders[down1].label != self.cylinders[start].label):
                        return [self.cylinders[down1].name()]
                    else:
                        return []


            elif direction == "top":
                
                above1 = (start - 1) % n
                above2 = (start - 2) % n
                
                if (start == 0):
                    if (self.number_cylinders[1] > 2
                            and self.cylinders[above1].label != self.cylinders[start].label
                            and self.cylinders[above2].label != self.cylinders[start].label
                            and 'l' in self.marked_points[above2]):
                        return [self.cylinders[above1].name(), self.cylinders[above2].name()]
                    elif (self.cylinders[above1].label != self.cylinders[start].label
                          and 'l' in self.marked_points[above1]):
                        return [self.cylinders[above1].name()]
                    else:
                        return []
                elif (start == 1):
                    if (self.cylinders[above1].label != self.cylinders[start].label
                            and self.cylinders[above2].label != self.cylinders[start].label
                            and 'l' in self.marked_points[above2]):
                        return [self.cylinders[above1].name(), self.cylinders[above2].name()]
                    elif (self.cylinders[above1].label != self.cylinders[start].label):
                        return [self.cylinders[above1].name()]
                    else:
                        return []
                else:
                    if (self.cylinders[above1].label != self.cylinders[start].label
                            and self.cylinders[above2].label != self.cylinders[start].label):
                        return [self.cylinders[above1].name(), self.cylinders[above2].name()]
                    elif (self.cylinders[above1].label != self.cylinders[start].label):
                        return [self.cylinders[above1].name()]
                    else:
                        return []


        def check_direction2(start, direction):
            assert (direction == "top" or direction == "bottom")
            assert (start in {self.number_cylinders[0], 
                              self.number_cylinders[0] + 1, 
                              self.number_cylinders[0] + self.number_cylinders[1] - 1, 
                              self.number_cylinders[0] + self.number_cylinders[1] - 2})
            attack = []

            if direction == "bottom":

                if (start == self.number_cylinders[0] + self.number_cylinders[1] - 1):
                    down1 = self.number_cylinders[0]
                    down2 = self.number_cylinders[0] + 1
                    if (self.number_cylinders[1] > 2 
                            and self.cylinders[down1].label != self.cylinders[start].label
                            and self.cylinders[down2].label != self.cylinders[start].label 
                            and 'r' in self.marked_points[down2 + 1]):
                        return [self.cylinders[down1].name(), self.cylinders[down2].name()]
                    elif (self.cylinders[down1].label != self.cylinders[start].label
                          and 'r' in self.marked_points[down1 + 1]):
                        return [self.cylinders[down1].name()]
                    else:
                        return []
                elif (start == self.number_cylinders[0] + self.number_cylinders[1] - 2):
                    down1 = self.number_cylinders[0] + self.number_cylinders[1] - 1
                    down2 = self.number_cylinders[0]
                    if (self.cylinders[down1].label != self.cylinders[start].label
                            and self.cylinders[down2].label != self.cylinders[start].label
                            and 'r' in self.marked_points[down2 + 1]):
                        return [self.cylinders[down1].name(), self.cylinders[down2].name()]
                    elif (self.cylinders[down1].label != self.cylinders[start].label):
                        return [self.cylinders[down1].name()]
                    else:
                        return []
                else:
                    assert(false)

            elif direction == "top":

                if (start == self.number_cylinders[0]):
                    above1 = self.number_cylinders[0] + self.number_cylinders[1] - 1
                    above2 = self.number_cylinders[0] + self.number_cylinders[1] - 2
                    if (self.number_cylinders[1] > 2 
                            and self.cylinders[above1].label != self.cylinders[start].label
                            and self.cylinders[above2].label != self.cylinders[start].label
                            and 'r' in self.marked_points[above2]):
                        return [self.cylinders[above1].name(), self.cylinders[above2].name()]
                    elif (self.cylinders[above1].label != self.cylinders[start].label
                          and 'r' in self.marked_points[above1]):
                        return [self.cylinders[above1].name()]
                    else:
                        return []
                elif (start == self.number_cylinders[0] + 1):
                    above1 = self.number_cylinders[0]
                    above2 = self.number_cylinders[0] + self.number_cylinders[1] - 1
                    if (self.cylinders[above1].label != self.cylinders[start].label
                            and self.cylinders[above2].label != self.cylinders[start].label
                            and 'r' in self.marked_points[above2]):
                        return [self.cylinders[above1].name(), self.cylinders[above2].name()]
                    elif (self.cylinders[above1].label != self.cylinders[start].label):
                        return [self.cylinders[above1].name()]
                    else:
                        return []
                else:
                    assert(false)


        n = len(self)
        assert (n == self.number_cylinders[0] + self.number_cylinders[1])

        attacks = []
        
        for i in range(n):
            attacks.append({"top": [], "bottom": []})

            # for most cases, it suffices to look up 2 and down 2 and sum it up
            attacks[i]['bottom'].append(check_direction(i, "bottom"))
            attacks[i]['top'].append(check_direction(i, "top"))

            # for the first/second "long" cylinder, it could get attacked from 3 directions
            if i == self.number_cylinders[0] or i == self.number_cylinders[0] + 1:
                attacks[i]['top'].append(check_direction2(i, "top"))

            # same for the last/second last "long cylinder"
            if i == n - 1 or i == n - 2:
                attacks[i]['bottom'].append(check_direction2(i, "bottom"))

        return attacks

    def number_marked_points(self) -> int:
        pts = 0

        for i in range(len(self.cylinders)):
            if (i not in {0, self.number_cylinders[0]}):
                pts += len(self.marked_points[i])

        return pts


def pos(num):
    return Symbol(num, positive=True)


def process_attack(attack: dict[str, list]): 
    expr = 0
    
    for a in attack:
        part = 0
        for e in a:
            part += pos(e)
        expr = Max(expr, part)

    return expr


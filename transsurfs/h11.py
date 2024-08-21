from sympy import *

class Cylinder:
    label: str 
    index: int

    def __init__(self, label: str, index: int) -> None:
        self.label = label
        self.index = index

    def name(self) -> str:
        return self.label + "_" + str(self.index)


class TransSurfH11:
    cylinders: list[Cylinder]
    number_cylinders: list[int]
    top_cylinders: list[str]
    bottom_cylinders: list[str]
    starting_cylinders: list[str]
    marked_points: list[list[str]]

    def __init__(self, number_cylinders: list[int], top_cylinders: list[str],
                 bottom_cylinders: list[str], starting_cylinders: list[str]):
        """
        H(1,1,0^k) translation surfaces look like this. 
        ┌────────┐            
        │        │            
        ├────────┤             number_cylinders[0]
        │        │            
        ├────────┴───────────┐
        │                    │
        ├────────────────────┤
        │                    │ number_cylinders[1]
        ├────────────────────┤
        │                    │
        └────────┌───────────┐
                 │           │
                 ┼───────────┼
                 │           │ number_cylinders[2]
                 ┼───────────┼
                 │           │
                 └───────────┘
        """
        assert(len(number_cylinders) == 3)

        self.number_cylinders = number_cylinders
        self.bottom_cylinders = bottom_cylinders
        self.top_cylinders = top_cylinders
        self.starting_cylinders = starting_cylinders

        cylinders: list[Cylinder] = []
        a_ct, b_ct = 0, 0  # using these for labelling the cylinders

        for t in range(3):
            # start by adding the top cylinder
            if top_cylinders[t] == 'A':
                cylinders.append(Cylinder(top_cylinders[t], a_ct))
                a_ct += 1
            else:
                cylinders.append(Cylinder(top_cylinders[t], b_ct))
                b_ct += 1

            if (number_cylinders[t] == 1):
                continue

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

        self.marked_points = [[] for _ in range(len(cylinders) + 1)]

        for i in range(len(cylinders) + 1):
            self.marked_points[i] += ['l', 'r']

        self.cylinders = cylinders

    def __getitem__(self, key: int):
        return self.cylinders[key]
    
    def __len__(self):
        return len(self.cylinders)

    def compute_attacks(self) -> list:

        attacks = []
        n = len(self)
        for _ in range(n):
            attacks.append({"top": [], "bottom": []})

        mod_top: int = self.number_cylinders[0] + self.number_cylinders[1]
        mod_bottom: int = self.number_cylinders[1] + self.number_cylinders[2]
        mod_all: int = len(self)

        # the top part gets attacked normally
        for i in range(self.number_cylinders[0]):
            # top attack 
            attack = []
            nextid: int = (i - 1) % mod_top
            furthest_atk: int = i

            # find the furthest cylinder an attack could come from 
            while (self[nextid].label != self[i].label):
                if ('l' in self.marked_points[nextid]):
                    furthest_atk = nextid
                # print("FURTHEST_ATK", furthest_atk)
                nextid -= 1
                nextid %= mod_top

            # compute the attack
            k: int = i
            while (k != furthest_atk):
                k -= 1
                k %= mod_top
                attack.append(self[k].name())
                

            attacks[i]['top'].append(attack)

            # bottom attack 
            attack = []
            nextid: int = (i + 1) % mod_top
            furthest_atk: int = i

            # find the furthest cylinder an attack could come from
            while (self[nextid].label != self[i].label):
                if ('l' in self.marked_points[(nextid - 1) % mod_top]):
                    furthest_atk = nextid
                # print("FURTHEST_ATK", furthest_atk)
                nextid += 1
                nextid %= mod_top

            # compute the attack
            k: int = i
            while (k != furthest_atk):
                k += 1
                k %= mod_top
                attack.append(self[k].name())

            attacks[i]['bottom'].append(attack)
                
        # the bottom part gets attacked normally also 
        for i in range(self.number_cylinders[0] + self.number_cylinders[1], len(self)):
            # top attack
            attack = []
            nextid: int = ((i - 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]
            furthest_atk: int = i

            # find the furthest cylinder an attack could come from
            while (self[nextid].label != self[i].label):
                if ('r' in self.marked_points[nextid]):
                    furthest_atk = nextid
                # print("FURTHEST_ATK", furthest_atk)
                nextid = (
                    (nextid - 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]

            # compute the attack
            k: int = i
            while (k != furthest_atk):
                k = (
                    (k - 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]
                attack.append(self[k].name())

            attacks[i]['top'].append(attack)

            # bottom attack
            attack = []
            nextid: int = (
                (i + 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]
            furthest_atk: int = i

            # find the furthest cylinder an attack could come from
            while (self[nextid].label != self[i].label):
                if ('r' in self.marked_points[(
                    (nextid + 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]]):
                    furthest_atk = nextid
                # print("FURTHEST_ATK", furthest_atk)
                nextid = (
                    (nextid + 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]

            # compute the attack
            k: int = i
            while (k != furthest_atk):
                k = (
                    (k + 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]
                attack.append(self[k].name())

            attacks[i]['bottom'].append(attack)

        # the middle gets attacked like both the top and bottom:
        for i in range(self.number_cylinders[0], self.number_cylinders[0] + self.number_cylinders[1]):
            # top attack
            attack = []
            nextid: int = (i - 1) % mod_top
            furthest_atk: int = i

            # find the furthest cylinder an attack could come from
            while (self[nextid].label != self[i].label):
                if ('l' in self.marked_points[nextid]):
                    furthest_atk = nextid
                # print("FURTHEST_ATK", furthest_atk)
                nextid -= 1
                nextid %= mod_top

            # compute the attack
            k: int = i
            while (k != furthest_atk):
                k -= 1
                k %= mod_top
                attack.append(self[k].name())

            attacks[i]['top'].append(attack)

            # bottom attack
            attack = []
            nextid: int = (i + 1) % mod_top
            furthest_atk: int = i

            # find the furthest cylinder an attack could come from
            while (self[nextid].label != self[i].label):
                if ('l' in self.marked_points[(nextid + 1) % mod_top]):
                    furthest_atk = nextid
                # print("FURTHEST_ATK", furthest_atk)
                nextid += 1
                nextid %= mod_top

            # compute the attack
            k: int = i
            while (k != furthest_atk):
                k += 1
                k %= mod_top
                attack.append(self[k].name())

            attacks[i]['bottom'].append(attack)

        for i in range(self.number_cylinders[0], self.number_cylinders[0] + self.number_cylinders[1]):
            # top attack
            attack = []
            nextid: int = (
                (i - 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]
            furthest_atk: int = i

            # find the furthest cylinder an attack could come from
            while (self[nextid].label != self[i].label):
                if ('r' in self.marked_points[nextid]):
                    furthest_atk = nextid
                # print("FURTHEST_ATK", furthest_atk)
                nextid = (
                    (nextid - 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]

            # compute the attack
            k: int = i
            while (k != furthest_atk):
                k = (
                    (k - 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]
                attack.append(self[k].name())

            attacks[i]['top'].append(attack)

            # bottom attack
            attack = []
            nextid: int = (
                (i + 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]
            furthest_atk: int = i

            # find the furthest cylinder an attack could come from
            while (self[nextid].label != self[i].label):
                if ('r' in self.marked_points[(
                    (nextid - 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]]):
                    furthest_atk = nextid
                # print("FURTHEST_ATK", furthest_atk)
                nextid = (
                    (nextid + 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]

            # compute the attack
            k: int = i
            while (k != furthest_atk):
                k = (
                    (k + 1 - self.number_cylinders[0]) % mod_bottom) + self.number_cylinders[0]
                attack.append(self[k].name())

            attacks[i]['bottom'].append(attack)
        
        # """
        # we can also attack through the middle sometimes
        for i in range(len(self)):
            # top attack 
            attack = []
            nextid: int = (i - 1) % mod_all
            furthest_atk: int = i

            # find the furthest cylinder an attack could come from 
            while (self[nextid].label != self[i].label):
                if ('l' in self.marked_points[nextid]):
                    furthest_atk = nextid
                # print("FURTHEST_ATK", furthest_atk)
                nextid -= 1
                nextid %= mod_all

            # compute the attack if it passes though the center 
            if (i >= self.number_cylinders[0] + self.number_cylinders[1]) \
                    and (furthest_atk < self.number_cylinders[0] + self.number_cylinders[1]):
                k: int = i
                while (k != furthest_atk):
                    k -= 1
                    k %= mod_all
                    attack.append(self[k].name())
                    

                attacks[i]['top'].append(attack)

            # bottom attack 
            attack = []
            nextid: int = (i + 1) % mod_all
            furthest_atk: int = i

            # find the furthest cylinder an attack could come from
            while (self[nextid].label != self[i].label):
                if ('l' in self.marked_points[(nextid - 1) % mod_all]):
                    furthest_atk = nextid
                # print("FURTHEST_ATK", furthest_atk)
                nextid += 1
                nextid %= mod_all

            # compute the attack if it passes though the center 
            if (i <= self.number_cylinders[0]) \
                    and (furthest_atk > self.number_cylinders[0]):
                k: int = i
                while (k != furthest_atk):
                    k += 1
                    k %= mod_all
                    attack.append(self[k].name())

                attacks[i]['bottom'].append(attack)
        # """
        return attacks

    def number_marked_points(self) -> int:
        modifiable_points: set[int] = set() 
        n1 = self.number_cylinders[0]
        n2 = self.number_cylinders[1]

        if (n1 < n1 + 1 and n1 + 1 < n1 + n2):
            modifiable_points.add(n1 + 1)
        if (n1 < n1 + 2 and n1 + 2 < n1 + n2):
            modifiable_points.add(n1 + 2)
        if (n1 < n1 + n2 - 2 and n1 + n2 - 2 < n1 + n2):
            modifiable_points.add(n1 + n2 - 2)
        if (n1 < n1 + n2 - 1 and n1 + n2 - 1 < n1 + n2):
            modifiable_points.add(n1 + n2 - 1)

        pts = 0

        for i in range(len(self.cylinders)):
            if (i in modifiable_points):
                pts += len(self.marked_points[i])
            elif (i in {0, n1, n1 + n2}):
                pass
            else:
                pts += 1

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


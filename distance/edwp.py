# -*- coding: utf-8 -*-
import math


class EDwP(object):
    @staticmethod
    def get_distance(r, s):
        return EDwP.get_EDwP(r, s)

    @staticmethod
    def get_EDwP(r, s):
        total_cost_edwp = 0
        if len(r) == 0 and len(s) == 0:
            return 0
        if len(r) == 0 or len(s) == 0:
            return float("inf")

        flag = False
        while not flag:
            replacement, coverage = 0, 0
            if len(s) == 1 and len(r) > 1:
                e_p1, e_p2 = r[0], r[1]
                p = s[0]
                replacement = EDwP.replacement(e_p1, e_p2, p, p)
                coverage = EDwP.coverage(e_p1, e_p2, p, p)
            elif len(r) == 1 and len(s) > 1:
                e_p1, e_p2 = s[0], s[1]
                p = r[0]
                replacement = EDwP.replacement(e_p1, e_p2, p, p)
                coverage = EDwP.coverage(e_p1, e_p2, p, p)
            elif len(r) > 1 and len(s) > 1:
                e1_p1, e1_p2 = r[0], r[1]
                e2_p1, e2_p2 = s[0], s[1]
                p_ins_e1 = EDwP.projection(e1_p1, e1_p2, e2_p2)
                p_ins_e2 = EDwP.projection(e2_p1, e2_p2, e1_p2)

                replace_e1 = EDwP.replacement(e1_p1, p_ins_e1, e2_p1, e2_p2)
                replace_e2 = EDwP.replacement(e2_p1, p_ins_e2, e1_p1, e1_p2)
                cover_e1 = EDwP.coverage(e1_p1, p_ins_e1, e2_p1, e2_p2)
                cover_e2 = EDwP.coverage(e2_p1, p_ins_e2, e1_p1, e1_p2)

                if cover_e1 * replace_e1 < cover_e2 * replace_e2:
                    replacement = replace_e1
                    coverage = cover_e1

                    if not EDwP.equals(p_ins_e1, e1_p1) and not EDwP.equals(p_ins_e1, e1_p2):
                        r.insert(1, p_ins_e1)
                else:
                    replacement = replace_e2
                    coverage = cover_e2
                    if not EDwP.equals(p_ins_e2, e2_p1) and not EDwP.equals(p_ins_e2, e2_p2):
                        s.insert(1, p_ins_e2)
            else:
                flag = True
            r, s = EDwP.rest(r), EDwP.rest(s)
            total_cost_edwp += (replacement * coverage)
        return total_cost_edwp


    @staticmethod
    def replacement(e1_p1, e1_p2, e2_p1, e2_p2):
        dist_p1, dist_p2 = EDwP.distance(e1_p1, e2_p1), EDwP.distance(e1_p2, e2_p2)
        return dist_p1 + dist_p2

    @staticmethod
    def coverage(e1_p1, e1_p2, e2_p1, e2_p2):
        return EDwP.distance(e1_p1, e1_p2) + EDwP.distance(e2_p1, e2_p2)

    @staticmethod
    def projection(e_p1, e_p2, p):
        if EDwP.equals(e_p1, e_p2):
            return e_p1

        dot_product_temp = EDwP.dot_product(e_p1, e_p2, p)
        len_2 = math.pow(e_p2[0] - e_p1[0], 2) + math.pow(e_p2[1] - e_p1[1], 2)

        x = e_p1[0] + float(dot_product_temp * (e_p2[0] - e_p1[0])) / len_2
        y = e_p1[1] + float(dot_product_temp * (e_p2[1] - e_p1[1])) / len_2
        return [x, y]

    @staticmethod
    def dot_product(e_p1, e_p2, p):
        shift_e, shift_p = [0, 0], [0, 0]
        for i in range(0, 2):
            shift_e[i] = e_p2[i] - e_p1[i]
            shift_p[i] = p[i] - e_p1[i]
        dot_product_ret = 0
        for i in range(0, 2):
            dot_product_ret += (shift_e[i] * shift_p[i])
        return dot_product_ret

    @staticmethod
    def rest(l):
        if len(l) > 0:
            return l[1:]

    @staticmethod
    def distance(p, q):
        square = math.pow(p[0] - q[0], 2) + math.pow(p[1] - q[1], 2)
        return math.sqrt(square)

    @staticmethod
    def equals(a, b):
        for i in range(0, 2):
            if a[i] != b[i]:
                return False
        return True

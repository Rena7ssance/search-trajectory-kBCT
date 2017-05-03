# -*- coding: utf-8 -*-
class Function:
    def __init__(self):
        pass

    @staticmethod
    def is_valid(username, password):
        if username == 'roy7wt' and password == 'qijianw1':
            return True
        else:
            return False


def fun(a):
    b,c,d = a
    print b,c,d


if __name__ == '__main__':
    t = (2015, 11, 1)
    fun(t)

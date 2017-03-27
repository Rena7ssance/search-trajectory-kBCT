from simlifier import *
from helper import *

if __name__ == '__main__':
    # print Helper.lnglat2distance(121.342441, 31.263124, 121.341876, 31.263346)
    s = Simplifier()
    # print s.heading_direction([121.334382, 31.264038], [121.334338, 31.263517])
    # print s.heading_direction([121.334338, 31.263517], [121.334338, 31.262883])
    # Helper.heading_direction([0, 0], [-0.1, -0.9])
    # Helper.heading_direction([0, 0], [-1, 1])
    # Helper.heading_direction([0, 0], [-1.7, -1])

    t = Helper.file2points('data/test_data/test.txt')
    print s.ts_algorithm(t)


# -*- coding: utf-8 -*-

import os
from helper import *


class Processor(object):
    dir_path = ''

    def __init__(self, read_path, write_dir, city, city_range):
        self._rp = read_path
        self._wd = write_dir
        self._city = city
        self._range = city_range

    def def_write_dir(self):
        self.dir_path = '%s/%s/%s' % (self._wd, self._city, self._rp[-11:-4])

    def create_write_dir(self):
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

    def pre_extract(self, time_threshold=1500):
        self.def_write_dir()
        self.create_write_dir()

        obd = {'OBD_ID': 2, 'OBD_LNG': 3, 'OBD_LAT': 4, 'OBD_TIME': 8}
        lng_lb, lng_ub, lat_lb, lat_ub = \
            self._range['lng'][0], self._range['lng'][1], self._range['lat'][0], self._range['lat'][1],
        print lng_lb, lng_ub, lat_lb, lat_ub

        with open(self._rp, 'r') as fr:
            for line in fr:
                obd_info = line.strip('\n').split(',')
                obd_id, obd_lng, obd_lat, obd_time = \
                    obd_info[obd['OBD_ID']], obd_info[obd['OBD_LNG']], \
                    obd_info[obd['OBD_LAT']], obd_info[obd['OBD_TIME']],

                # Search for specified district or city
                if lng_lb < float(obd_lng) < lng_ub \
                        and lat_lb < float(obd_lat) < lat_ub:
                    with open(self.dir_path + '/%s.txt' % obd_id, 'a+') as fw:
                        # read the last timestamp
                        if fw.tell() != 0:
                            fw.seek(-20, 1)
                            timestamp = fw.read(19)

                            # break individual trajectory
                            if Helper.timestamp_delta(obd_time, timestamp) > time_threshold:
                                fw.write('\n')

                        # 'lng'\t'lat'\t'time'\n
                        fw.write('%.6f\t%.6f\t%s\n' % (
                            round(float(obd_lng), 6), round(float(obd_lat), 6), obd_time))
                    fw.close()
        fr.close()

        for f in os.listdir(self.dir_path):
            Helper.append_linebreak(f)


if __name__ == '__main__':
    rp = 'data/raw_data/vehicle_gps_log_2015-04.txt'
    wd = 'data/raw_trajectory'
    c = 'shanghai'
    c_range = {'lng': [119.5, 123.5], 'lat': [30.5, 32.5]}
    p = Processor(rp, wd, c, c_range)
    p.pre_extract()

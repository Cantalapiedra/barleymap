#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MapInterval.py is part of Barleymap.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

class MapInterval(object):
    _positions = None
    _chrom = -1
    _ini_pos = -1
    _end_pos = -1
    
    def __init__(self, chrom, ini_pos, end_pos):
        self._positions = []
        self._chrom = chrom
        self._ini_pos = ini_pos
        self._end_pos = end_pos
    
    def add_position(self, position):
        self._positions.append(position)
    
    def get_positions(self):
        return self._positions
    
    def get_chrom(self):
        return self._chrom
    
    def get_ini_pos(self):
        return self._ini_pos
    
    def get_end_pos(self):
        return self._end_pos
    
    def set_end_pos(self, end_pos):
        self._end_pos = end_pos
    
    def __str__(self):
        return str(self._chrom)+" : "+str(self._ini_pos)+" - "+str(self._end_pos)+" : num positions "+str(len(self._positions))
    
    @staticmethod
    def intervals_overlap(int1, int2):
        retvalue = False
        
        if MapInterval.same_chrom(int1, int2) and \
            (MapInterval.contains(int1, int2) or MapInterval.contains(int2, int1) or \
            MapInterval.overlaps(int1, int2) or MapInterval.overlaps(int2, int1)):
            retvalue = True
        
        return retvalue
    
    @staticmethod
    def same_chrom(int1, int2):
        return int2.get_chrom() == int1.get_chrom()
    
    @staticmethod
    def contains(int1, int2):
        return (float(int1.get_ini_pos())<=float(int2.get_ini_pos()) and float(int1.get_end_pos())>=float(int2.get_end_pos()))
    
    @staticmethod
    def overlaps(int1, int2):
        return (float(int1.get_ini_pos())>=float(int2.get_ini_pos()) and float(int1.get_ini_pos())<=float(int2.get_end_pos()))

# Composite of MapInterval and list of features associated
# to that MapInterval
class FeaturedMapInterval(object):
    _features = None
    _map_interval = None
    #_mapping_result = None
    
    def __init__(self, map_interval):
        self._features = []
        self._map_interval = map_interval
    
    #def get_mapping_result(self, ):
    #    return self._mapping_result
    #
    #def set_mapping_result(self, mapping_result):
    #    self._mapping_result = mapping_result
    
    def get_features(self, ):
        return self._features
    
    def set_features(self, features):
        self._features = features
    
    def get_map_interval(self, ):
        return self._map_interval
    
    def set_map_interval(self, map_interval):
        self._map_interval = map_interval

## END

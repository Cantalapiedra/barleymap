#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MapFile.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

from barleymapcore.maps.MapsBase import MapTypes

# MapFile: fields of original maps of contigs (IBSC2012 Morex contigs, ...)
class MapFile(object):
    
    # Tab separated fields in the map config files
    MAP_FILE_CONTIG = 0
    MAP_FILE_CHR = 1
    MAP_FILE_CM = 2
    MAP_FILE_BP = 3
    
    @staticmethod
    def get_sort_pos_contigs(sort_param, map_has_cm, map_has_bp):
        sort_by = -1 # 1st sorting pos
        sec_pos = -1 # 2nd sorting pos
        
        if map_has_cm and map_has_bp:
            if sort_param == MapTypes.MAP_SORT_PARAM_CM:
                sort_by = MapFile.MAP_FILE_CM
                sec_pos = MapFile.MAP_FILE_BP
            elif sort_param == MapTypes.MAP_SORT_PARAM_BP:
                sort_by = MapFile.MAP_FILE_BP
                sec_pos = MapFile.MAP_FILE_CM
            else:
                raise Exception("Wrong sort type "+str(sort_param))
            
        elif map_has_cm or map_has_bp:
            sort_by = MapFile.MAP_FILE_CM
            sec_pos = MapFile.MAP_FILE_CM
        else:
            raise Exception("Map must have either cM or bp, or both.")
        
        ## sort type
        #if sort_param == MapTypes.MAP_SORT_PARAM_CM:
        #    if map_has_cm and map_has_bp:
        #        sort_by = MapFile.MAP_FILE_CM
        #        sec_pos = MapFile.MAP_FILE_BP
        #    elif map_has_cm:
        #        sort_by = MapFile.MAP_FILE_CM
        #        sec_pos = MapFile.MAP_FILE_CM
        #    elif map_has_bp:
        #        sort_by = MapFile.MAP_FILE_CM
        #        sec_pos = MapFile.MAP_FILE_CM
        #elif sort_param == MapTypes.MAP_SORT_PARAM_BP:
        #    if map_has_cm and map_has_bp:
        #        sort_by = MapFile.MAP_FILE_BP
        #        sec_pos = MapFile.MAP_FILE_CM
        #    elif map_has_cm:
        #        sort_by = MapFile.MAP_FILE_CM
        #        sec_pos = MapFile.MAP_FILE_CM
        #    elif map_has_bp:
        #        sort_by = MapFile.MAP_FILE_CM
        #        sec_pos = MapFile.MAP_FILE_CM
        #else:
        #    raise Exception("get_sort_pos_contigs: Wrong field for sorting "+str(sort_param))
        
        return (sort_by, sec_pos)
    
# Like MapFile but for physical maps.
# In this case, there is a single file (no database files)
# which has just the numeric ordering of the chromosomes of this map
class ChromosomesFile(object):
    
    FILE_EXT = ".chrom"
    # Tab separated fields in the map config files
    CHROM_NAME = 0
    CHROM_ORDER = 1

## END
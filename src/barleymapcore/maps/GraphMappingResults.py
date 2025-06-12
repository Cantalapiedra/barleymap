#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MappingResults.py is part of Barleymap.
# Copyright (C) 2025 Bruno Contreras Moreira and Joan Sarria
# (terms of use can be found within the distributed LICENSE file).

from MapsBase import MapTypes

## This class represents the map position of a marker which has been aligned first to a graph
##
class GraphMappingResult(object):
    _marker_id = ""
    _chrom_name = ""
    _chrom_order = "-1"
    _cm_pos = "-1.0"
    _cm_end_pos = "-1.0"
    _bp_pos = "-1"
    _bp_end_pos = "-1"
    _strand = "-"
    _multiple_pos = False
    _graph_ranges = ""
    _map_name = ""
    _feature = None
    
    _empty = False
    
    MAP_FIELDS = 7
    
    def __init__(self, marker_id, chrom_name, chrom_order,
                 cm_pos, cm_end_pos, bp_pos, bp_end_pos, strand,
                 has_multiple_pos, graph_ranges, map_name, empty = False):
        
        self._marker_id = marker_id
        self._chrom_name = chrom_name
        self._chrom_order = chrom_order
        self._cm_pos = cm_pos
        self._cm_end_pos = cm_end_pos
        self._bp_pos = bp_pos
        self._bp_end_pos = bp_end_pos
        self._strand = strand
        self._multiple_pos = has_multiple_pos
        self._graph_ranges = graph_ranges
        self._map_name = map_name
        self._empty = empty
    
    # An empty MappingResult can be created for several reasons,
    # including creating an empty mapping result which has features associated
    @staticmethod
    def get_empty():
        mapping_result = GraphMappingResult("-", "-", "-", "-", "-", "-", "-", "-", False, "", "")
        mapping_result.set_empty(True)
        return mapping_result
    
    def is_empty(self):
        return self._empty
    
    def set_empty(self, empty):
        self._empty = empty
    
    def clone(self):
        new_mapping_result = MappingResult(self.get_marker_id(),
                                           self.get_chrom_name(),
                                           self.get_chrom_order(),
                                           self.get_cm_pos(),
                                           self.get_cm_end_pos(),
                                           self.get_bp_pos(),
                                           self.get_bp_end_pos(),
                                           self.get_strand(),
                                           self.has_multiple_pos(),
                                           self.get_graph_ranges(),
                                           self.get_map_name(),
                                           self.is_empty())
        
        new_mapping_result.set_feature(self.get_feature())
        
        return new_mapping_result
    
    
    # A feature is an attachment or additional information
    # associated to this mapping result. For example,
    # markers or genes around the mapping result
    # used in enrichment procedures
    def set_feature(self, feature):
        self._feature = feature
    
    def get_feature(self):
        return self._feature
    
    def get_marker_id(self):
        return self._marker_id
    
    def set_marker_id(self, marker_id):
        self._marker_id = marker_id
    
    def get_chrom_name(self):
        return self._chrom_name
    
    def get_chrom_order(self):
        return self._chrom_order
    
    def get_cm_pos(self):
        return self._cm_pos
    
    def get_cm_end_pos(self):
        return self._cm_end_pos
    
    def get_bp_pos(self):
        return self._bp_pos
    
    def get_bp_end_pos(self):
        return self._bp_end_pos
    
    def get_strand(self):
        return self._strand
    
    def has_multiple_pos(self):
        return self._multiple_pos
    
    def get_graph_ranges(self):
        return self._graph_ranges
    
    def get_map_name(self):
        return self._map_name
    
    def get_sort_pos(self, sort_by):
        ret_value = -1
        
        if sort_by == MapTypes.MAP_SORT_PARAM_CM:
            ret_value = self._cm_pos#float(self._cm_pos)
        elif sort_by == MapTypes.MAP_SORT_PARAM_BP:
            ret_value = self._bp_pos#long(self._bp_pos)
        else:
            raise m2pException("Unrecognized sort field "+str(sort_by)+".")
        
        return ret_value
    
    def get_sort_end_pos(self, sort_by):
        ret_value = -1
        
        if sort_by == MapTypes.MAP_SORT_PARAM_CM:
            ret_value = self._cm_end_pos#float(self._cm_pos)
        elif sort_by == MapTypes.MAP_SORT_PARAM_BP:
            ret_value = self._bp_end_pos#long(self._bp_pos)
        else:
            raise m2pException("Unrecognized sort field "+str(sort_by)+".")
        
        return ret_value
    
    def get_sort_sec_pos(self, sort_by):
        ret_value = -1
        
        if sort_by == MapTypes.MAP_SORT_PARAM_CM:
            ret_value = self._bp_pos
        elif sort_by == MapTypes.MAP_SORT_PARAM_BP:
            ret_value = self._cm_pos
        else:
            raise m2pException("Unrecognized sort field "+str(sort_by)+".")
        
        return ret_value
    
    def get_sort_end_sec_pos(self, sort_by):
        ret_value = -1
        
        if sort_by == MapTypes.MAP_SORT_PARAM_CM:
            ret_value = self._end_end_pos
        elif sort_by == MapTypes.MAP_SORT_PARAM_BP:
            ret_value = self._cm_end_pos
        else:
            raise m2pException("Unrecognized sort field "+str(sort_by)+".")
        
        return ret_value
    
 
    
## END
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MappingResults.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

from MapsBase import MapTypes

## This class represents the map position of a marker which has been aligned first to a DB
##
class MappingResult(object):
    _marker_id = ""
    _chrom_name = ""
    _chrom_order = "-1"
    _cm_pos = "-1.0"
    _cm_end_pos = "-1.0"
    _bp_pos = "-1"
    _bp_end_pos = "-1"
    _strand = "-"
    _multiple_pos = False
    _other_alignments = False
    _map_name = ""
    _feature = None
    
    _empty = False
    
    MAP_FIELDS = 7
    
    def __init__(self, marker_id, chrom_name, chrom_order,
                 cm_pos, cm_end_pos, bp_pos, bp_end_pos, strand,
                 has_multiple_pos, has_other_alignments, map_name, empty = False):
        
        self._marker_id = marker_id
        self._chrom_name = chrom_name
        self._chrom_order = chrom_order
        self._cm_pos = cm_pos
        self._cm_end_pos = cm_end_pos
        self._bp_pos = bp_pos
        self._bp_end_pos = bp_end_pos
        self._strand = strand
        self._multiple_pos = has_multiple_pos
        self._other_alignments = has_other_alignments
        self._map_name = map_name
        self._empty = empty
    
    # An empty MappingResult can be created for several reasons,
    # including creating an empty mapping result which has features associated
    @staticmethod
    def get_empty():
        mapping_result = MappingResult("-", "-", "-", "-", "-", "-", "-", "-", False, False, "")
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
                                           self.has_other_alignments(),
                                           self.get_map_name(),
                                           self.is_empty())
        
        new_mapping_result.set_feature(self.get_feature())
        
        return new_mapping_result
    
    
    @staticmethod
    def init_from_data(mapping_data, map_name, chrom_dict, map_is_physical, map_has_cm_pos, map_has_bp_pos):
        
        marker_id = mapping_data[0]
        chrom_name = mapping_data[1]
        chrom_order = chrom_dict[chrom_name]
        
        if map_is_physical:
            cm_pos = -1.0
            cm_end_pos = -1.0
            bp_pos = mapping_data[2]
            bp_end_pos = mapping_data[3]
            strand = mapping_data[4]
            pos_shift = 5
        else:
            if map_has_cm_pos and map_has_bp_pos:
                cm_pos = mapping_data[2]#float(mapping_data[2])
                cm_end_pos = cm_pos
                bp_pos = mapping_data[3]#long(mapping_data[3])
                bp_end_pos = bp_pos
                strand = ""
                pos_shift = 4
            elif map_has_cm_pos:
                cm_pos = mapping_data[2]#float(mapping_data[2])
                cm_end_pos = cm_pos
                bp_pos = -1
                bp_end_pos = -1
                strand = ""
                pos_shift = 3
            elif map_has_bp_pos:
                cm_pos = -1.0
                cm_end_pos = -1.0
                bp_pos = mapping_data[2]#long(mapping_data[2])
                bp_end_pos = bp_pos
                strand = ""
                pos_shift = 3
            else:
                raise m2pException("Map configuration is wrong: has not cm nor bp positions.")  
        
        has_multiple_pos = True if mapping_data[pos_shift] == "Yes" or mapping_data[pos_shift] == True else False
        has_other_alignments = True if mapping_data[pos_shift + 1] == "Yes" or mapping_data[pos_shift + 1] == True else False
        empty = False # a mapping result with data is not empty by definition
        
        return MappingResult(marker_id, chrom_name, chrom_order,
                             cm_pos, cm_end_pos, bp_pos, bp_end_pos, strand, 
                             has_multiple_pos, has_other_alignments, map_name, empty)
    
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
    
    def has_other_alignments(self):
        return self._other_alignments
    
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
    
    def __str__(self):
        return " - ".join([self._marker_id, str(self._chrom_name)+"/"+str(self._chrom_order),
                           str(self._cm_pos), str(self._cm_end_pos), str(self._bp_pos), str(self._bp_end_pos), str(self._strand),
                           str(self._multiple_pos), str(self._other_alignments), str(self._map_name),
                           str(self._feature), str(self._empty)])
    
##############################
## A class with the results of barleymap
## including the mapped, unmapped and unaligned markers
class MappingResults(object):
    _mapped = None
    _unmapped = None
    _unaligned = None
    _fine_mapping = False
    _sort_by = ""
    _map_config = None
    
    _map_with_genes = None
    _map_with_markers = None
    _map_with_anchored = None
    
    _annotator = None
    
    def __init__(self):
        return
    
    def extend(self, mapping_results):
        self._mapped.extend(mapping_results.get_mapped())
    
    def get_mapped(self):
        return self._mapped
    
    def set_mapped(self, mapped):
        self._mapped = mapped
    
    def get_unmapped(self):
        return self._unmapped
    
    def set_unmapped(self, unmapped):
        self._unmapped = unmapped
    
    def get_unaligned(self):
        return self._unaligned
    
    def set_unaligned(self, unaligned):
        self._unaligned = unaligned
    
    def is_fine_mapping(self):
        return self._fine_mapping
    
    def set_fine_mapping(self, fine_mapping):
        self._fine_mapping = fine_mapping
    
    def get_sort_by(self):
        return self._sort_by
    
    def set_sort_by(self, sort_by):
        self._sort_by = sort_by
    
    def get_map_config(self):
        return self._map_config
    
    def set_map_config(self, map_config):
        self._map_config = map_config
    
    def set_map_with_genes(self, map_with_genes):
        self._map_with_genes = map_with_genes
    
    def get_map_with_genes(self):
        return self._map_with_genes
    
    def get_annotator(self, ):
        return self._annotator
    
    def set_annotator(self, annotator):
        self._annotator = annotator
    
    def set_map_with_markers(self, map_with_markers):
        self._map_with_markers = map_with_markers
    
    def get_map_with_markers(self):
        return self._map_with_markers
    
    def set_map_with_anchored(self, map_with_anchored):
        self._map_with_anchored = map_with_anchored
    
    def get_map_with_anchored(self):
        return self._map_with_anchored
    
## END
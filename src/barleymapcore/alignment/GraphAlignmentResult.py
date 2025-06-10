#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AlignmentResult.py is part of Barleymap.
# Copyright (C) 2025 Bruno Contreras Moreira and Joan Sarria
# (terms of use can be found within the distributed LICENSE file).

class GraphAlignmentResult(object):
    
    _query_id = ""
    # scores
    perc_ident = 0.0
    perc_cover = 0.0
    align_score = 0.0
    # graph alignment attributes, coords in reference used to build graph (PHG)
    _ref_id = "."
    _ref_start = -1
    _ref_end = -1
    _ref_strand = "."
    # genome alignment attributes, coords in matched genome (gmap)
    _subj_mult_maps = "No"
    _subj_name = "."
    _subj_id = "."
    _subj_start = -1
    _subj_end = -1
    _subj_strand = "."
    # string with all overlapping graph ranges
    _graph_ranges = "."
    
    def __init__(self):
        return
    
    def create_from_attributes(self, query_id, ref_id, ref_start, ref_end, ref_strand, 
                                subj_name,subj_id,subj_start,subj_end,subj_strand,
                                subj_ident, subj_cover, subj_score, subj_multmaps,
                                graph_ranges, graph_id, algorithm):
        self.set_query_id(query_id)
        self.set_ref_id(ref_id)
        self.set_ref_start(ref_start)
        self.set_ref_end(ref_end)
        self.set_ref_strand(ref_strand)
        self.set_subj_name(subj_name)
        self.set_subj_id(subj_id)
        self.set_subj_start(subj_start)
        self.set_subj_end(subj_end)
        self.set_subj_strand(subj_strand)
        self.set_perc_ident(subj_ident)
        self.set_perc_cover(subj_cover)
        self.set_align_score(subj_score)
        self.set_subj_multmaps(subj_multmaps)
        self.set_graph_ranges(graph_ranges)
        self.set_graph_id(graph_id)
        self.set_algorithm(algorithm)
        
        return
    
    def set_query_id(self, query_id):       
        self._query_id = query_id

    def set_ref_id(self, ref_id):
        self._ref_id = ref_id

    def set_ref_start(self, ref_start):
        self._ref_start = ref_start

    def set_ref_end(self, ref_end):
        self._ref_end = ref_end

    def set_ref_strand(self, ref_strand):
        self._ref_strand = ref_strand

    def set_subj_name(self, subj_name):
        self._subj_name = subj_name

    def set_subj_id(self, subj_id):
        self._subj_id = subj_id

    def set_subj_start(self, subj_start):
        self._subj_start = subj_start

    def set_subj_end(self, subj_end):
        self._subj_end = subj_end

    def set_subj_strand(self, subj_strand):
        self._subj_strand = subj_strand

    def set_perc_ident(self, perc_ident):
        self.perc_ident = perc_ident
    
    def set_perc_cover(self, perc_cover):
        self.perc_cover = perc_cover

    def set_align_score(self, align_score):
        self.align_score = align_score

    def set_subj_multmaps(self, subj_multmaps):
        self._subj_multmaps = subj_multmaps

    def set_graph_ranges(self, graph_ranges):
        self._graph_ranges = graph_ranges

    def set_graph_id(self, graph_id):
        self._db_id = graph_id

    def set_algorithm(self, algorithm):
        self._algorithm = algorithm

    def get_query_id(self):
        return self._query_id

    def get_ref_id(self):
        return self._ref_id

    def get_ref_start(self):
        return self._ref_start

    def get_ref_end(self):
        return self._ref_end

    def get_ref_strand(self):
        return self._ref_strand

    def get_subj_name(self):
        return self._subj_name

    def get_subj_id(self):
        return self._subj_id

    def get_subj_start(self):
        return self._subj_start

    def get_subj_end(self):
        return self._subj_end

    def get_subj_strand(self):
        return self._subj_strand

    def get_perc_ident(self):
        return self.perc_ident

    def get_perc_cover(self):
        return self.perc_cover

    def get_align_score(self):
        return self.align_score

    def get_subj_multmaps(self):
        return self._subj_multmaps

    def get_graph_ranges(self):
        return self._graph_ranges

    def get_graph_id(self):
        return self._db_id

    def get_algorithm(self):
        return self._algorithm       

    ## backwards compatibility, methods called from other classes to retrieve alignment attribs,
    ## note that *subject* in PhysicalMapper is actually *ref* in graph context
    
    def get_subject_id(self):
        return self._ref_id       

    def get_local_position(self):
        return self._ref_start

    def get_end_position(self):
        return self._ref_end

    def get_strand(self):
        return self._ref_strand
    

## END
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AlignmentFacade.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# Copyright (C)  2016-2017 Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import os, sys

from barleymapcore.db.DatabasesConfig import REF_TYPE_STD

from AlignmentEngines import AlignmentEnginesFactory
from AlignmentResult import AlignmentResults, AlignmentResult

class AlignmentFacade():
    
    _paths_config = None
    
    _alignment_results = None
    
    _verbose = False
    
    def __init__(self, paths_config, verbose = False):
        self._paths_config = paths_config
        self._verbose = verbose
    
    def _create_alignment_results(self, query_path):
        results = []
        
        with open(query_path, 'r') as query_file:
            for line in query_file:
                if line.startswith("#") or not line.strip(): continue
                line_data = line.strip().split("\t")
                # If not tab separated, try space separated
                if len(line_data)!=2: line_data = line.strip().split(" ")
                # Try commas also
                if len(line_data)!=2: line_data = line.strip().split(",")
                if len(line_data)!=2:
                    sys.stderr.write("WARNING: position data on file has no 2 fields "+str(line)+"\n")
                    sys.stderr.write("\tcontinue to next line in query file...\n")
                    continue
                
                #sys.stderr.write(line+"\n")
                
                subject_id = line_data[0]
                local_position = line_data[1]
                
                # create fields for pseudoalignment
                query_id = subject_id+"_"+local_position
                align_ident = "100"
                query_cov = "100"
                align_score = "0"
                strand = "+"
                qstart_pos = "1"
                qend_pos = "2"
                end_position = str(long(local_position) + 1)
                db_name = "-"
                algorithm = "-"
                
                result = AlignmentResult()
                result.create_from_attributes(query_id, subject_id,
                                        align_ident, query_cov, align_score,
                                        strand, qstart_pos, qend_pos, local_position, end_position,
                                        db_name, algorithm)
                results.append(result)
                #sys.stderr.write(str(result)+"\n\n")
        
        return results
    
    # Creates AlignmentResults directly from positions
    def create_alignment_results(self, query_path):
        
        results = self._create_alignment_results(query_path)
        unaligned = []
        alignment_results = AlignmentResults(results, unaligned) # reset alignment results
        
        self._alignment_results = alignment_results
        return alignment_results
    
    # Performs the alignment of fasta sequences different DBs
    def perform_alignment(self, query_fasta_path, dbs_list, databases_config, search_type, aligner_list, \
                          threshold_id = 98, threshold_cov = 95, n_threads = 1, ref_type_param = REF_TYPE_STD):
        
        ## Create the SearchEngine (greedy, hierarchical, exhaustive searches on top of splitblast, gmap,...)
        alignment_engine = AlignmentEnginesFactory.get_alignment_engine(search_type, aligner_list, self._paths_config, 
                                                               ref_type_param, n_threads, self._verbose)
        
        ## Perform the search and alignments
        alignment_results = alignment_engine.perform_alignment(query_fasta_path, dbs_list, databases_config, threshold_id, threshold_cov)
        
        self._alignment_results = alignment_results
        
        return alignment_results
    
    def get_alignment_results(self):
        return self._alignment_results
    
## END
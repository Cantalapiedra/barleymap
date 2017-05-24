#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SearchEngines.py is part of Barleymap.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys, os

from reader.MapReader import MapReader
from mappers.Mappers import Mappers
from barleymapcore.db.MapsConfig import MapsConfig
from barleymapcore.m2p_exception import m2pException
import barleymapcore.utils.alignment_utils as alignment_utils

from barleymapcore.alignment.AlignmentEngines import ALIGNMENT_TYPE_GREEDY, ALIGNMENT_TYPE_HIERARCHICAL, ALIGNMENT_TYPE_BEST_SCORE

class SearchEnginesFactory(object):
    @staticmethod
    def get_search_engine_positions(maps_path, verbose):
        
        search_engine = SearchEnginePositions(maps_path, verbose)
        
        return search_engine
    
    @staticmethod
    def get_search_engine_datasets(maps_path, verbose):
        
        search_engine = SearchEngineDatasets(maps_path, verbose)
        
        return search_engine
    
    @staticmethod
    def get_search_engine(search_type, maps_path, best_score_param, databases_config,
                          aligner_list, threshold_id, threshold_cov, n_threads, verbose = False):
        
        search_engine = None
        
        if search_type == MapsConfig.SEARCH_TYPE_GREEDY:
            
            if best_score_param:
                search_engine = SearchEngineGreedy(maps_path, best_score_param, databases_config, aligner_list,
                                                   threshold_id, threshold_cov, n_threads, ALIGNMENT_TYPE_BEST_SCORE, verbose)
            else:
                search_engine = SearchEngineGreedy(maps_path, best_score_param, databases_config, aligner_list,
                                                   threshold_id, threshold_cov, n_threads, ALIGNMENT_TYPE_GREEDY, verbose)
                
        elif search_type == MapsConfig.SEARCH_TYPE_HIERARCHICAL:
            
            search_engine = SearchEngineGreedy(maps_path, best_score_param, databases_config, aligner_list,
                                                   threshold_id, threshold_cov, n_threads, ALIGNMENT_TYPE_HIERARCHICAL, verbose)
            
        elif search_type == MapsConfig.SEARCH_TYPE_EXHAUSTIVE:
            
            if best_score_param:
                search_engine = SearchEngineExhaustive(maps_path, best_score_param, databases_config, aligner_list,
                                                   threshold_id, threshold_cov, n_threads, ALIGNMENT_TYPE_BEST_SCORE, verbose)
            else:
                search_engine = SearchEngineExhaustive(maps_path, best_score_param, databases_config, aligner_list,
                                                   threshold_id, threshold_cov, n_threads, ALIGNMENT_TYPE_GREEDY, verbose)
        else:
            raise m2pException("Unrecognized search type "+search_type+".")
        
        return search_engine

class SearchEngine(object):
    _maps_path = None
    _verbose = False
    
    def __init__(self, maps_path, verbose = False):
        self._maps_path = maps_path
        self._verbose = verbose
    
    def create_map(self, query_path, query_sets_ids, map_config, facade, sort_param, multiple_param, tmp_files_dir = None):
        raise m2pException("To be implemented in child classes.")

# An engine to search for specific positions
# in the maps
class SearchEnginePositions(SearchEngine):
    
    def create_map(self, query_path, query_sets_ids, map_config, facade, sort_param, multiple_param, tmp_files_dir = None):
        
        sys.stderr.write("SearchEnginePositions: creating map: "+map_config.get_name()+"\n")
        
        ############ Retrieve pre-computed alignments
        alignment_results = facade.create_alignment_results(query_path)
        
        aligned = alignment_results.get_aligned()
        unaligned = alignment_results.get_unaligned()
        
        map_as_physical = map_config.as_physical()
        
        map_reader = MapReader(self._maps_path, map_config, self._verbose)
        
        mapper = Mappers.get_alignments_mapper(map_as_physical, map_reader, self._verbose)
        
        mapping_results = mapper.create_map(aligned, unaligned, map_config, sort_param, multiple_param)
        
        sys.stderr.write("SearchEnginePositions:"+str(len(mapping_results.get_mapped()))+"\n")
        
        return mapping_results
    
# An engine to search for markers or genes in
# precalculated datasets
class SearchEngineDatasets(SearchEngine):
    
    def create_map(self, query_path, query_sets_ids, map_config, facade, sort_param, multiple_param, tmp_files_dir = None):
        
        sys.stderr.write("SearchEngineDatasets: creating map: "+map_config.get_name()+"\n")
        
        map_reader = MapReader(self._maps_path, map_config, self._verbose)
        chrom_dict = map_reader.get_chrom_dict()
        
        ############ Retrieve pre-computed alignments
        facade.retrieve_datasets(query_path, query_sets_ids, map_config, chrom_dict, multiple_param)
        
        mapping_results = facade.get_results()
        mapping_unmapped = facade.get_unmapped()
        
        # Obtain Mapper
        mapper = Mappers.get_mappings_mapper(map_reader, self._verbose)
        
        mapping_results = mapper.create_map(mapping_results, mapping_unmapped, map_config, sort_param)
        
        sys.stderr.write("SearchEngineDatasets:"+str(len(mapping_results.get_mapped()))+"\n")
        
        return mapping_results

# Base class of alignments engine
# To search fasta sequences in the
# maps
class SearchEngineAlignments(SearchEngine):
    
    _alignment_type = ""
    
    def __init__(self, maps_path, best_score_param, databases_config,
                 aligner_list, threshold_id, threshold_cov, n_threads, alignment_type, verbose = False):
        
        SearchEngine.__init__(self, maps_path, verbose)
        self._databases_config = databases_config
        self._aligner_list = aligner_list
        self._threshold_id = threshold_id
        self._threshold_cov = threshold_cov
        self._n_threads = n_threads
        self._alignment_type = alignment_type
    
    def create_map(self, query_path, query_sets_ids, map_config, facade, sort_param, multiple_param, tmp_files_dir = None):
        raise m2pException("To be implemented in child classes.")

class SearchEngineGreedy(SearchEngineAlignments):
    
    def create_map(self, query_path, query_sets_ids, map_config, facade, sort_param, multiple_param, tmp_files_dir = None):
        
        sys.stderr.write("SearchEngineGreedy: creating map: "+map_config.get_name()+"\n")
        
        alignment_results = facade.perform_alignment(query_path, query_sets_ids, self._databases_config, self._alignment_type, self._aligner_list, \
                                self._threshold_id, self._threshold_cov, self._n_threads)
        
        sys.stderr.write("SearchEngineGreedy: aligned "+str(len(alignment_results.get_aligned()))+"\n")
        
        aligned = alignment_results.get_aligned()
        unaligned = alignment_results.get_unaligned()
        
        map_as_physical = map_config.as_physical()
        
        map_reader = MapReader(self._maps_path, map_config, self._verbose)
        
        mapper = Mappers.get_alignments_mapper(map_as_physical, map_reader, self._verbose)
        
        mapping_results = mapper.create_map(aligned, unaligned, map_config, sort_param, multiple_param)
        
        sys.stderr.write("SearchEngineGreedy: mapped "+str(len(mapping_results.get_mapped()))+"\n")
        
        return mapping_results

class SearchEngineExhaustive(SearchEngineAlignments):
    
    def create_map(self, query_path, query_sets_ids, map_config, facade, sort_param, multiple_param, tmp_files_dir = None):
        
        sys.stderr.write("SearchEngineGreedy: creating map: "+map_config.get_name()+"\n")
        
        map_as_physical = map_config.as_physical()
        map_reader = MapReader(self._maps_path, map_config, self._verbose)
        mapper = Mappers.get_alignments_mapper(map_as_physical, map_reader, self._verbose)
        
        current_path = query_path
        
        tmp_files_list = []
        prev_mapping_results = None
        try:
            for db in query_sets_ids:
                query_set = [db]
                alignment_results = facade.perform_alignment(current_path, query_set,
                                                             self._databases_config, self._alignment_type, self._aligner_list, \
                                                                self._threshold_id, self._threshold_cov, self._n_threads)
                
                sys.stderr.write("SearchEngineExhaustive: aligned "+str(len(alignment_results.get_aligned()))+"\n")
                
                aligned = alignment_results.get_aligned()
                unaligned = alignment_results.get_unaligned()
                
                mapping_results = mapper.create_map(aligned, unaligned, map_config, sort_param, multiple_param)
                
                sys.stderr.write("SearchEngineExhaustive: mapped "+str(len(mapping_results.get_mapped()))+"\n")
                
                if prev_mapping_results:
                    mapping_results.extend(prev_mapping_results)
                
                sys.stderr.write("\toverall:"+str(len(mapping_results.get_mapped()))+"\n")
                
                unique_unmapped = set([record[0] for record in mapping_results.get_unmapped()])
                num_unmapped = len(unique_unmapped)
                sys.stderr.write("SearchEngineExhaustive: unmapped "+str(num_unmapped)+"\n")
                
                remaining_queries = self._combine(unaligned, unique_unmapped)
                
                sys.stderr.write("SearchEngineExhaustive: total remaining queries "+str(len(remaining_queries))+".\n")
                
                if len(remaining_queries)==0:
                    break
                else:
                    current_path = alignment_utils.extract_fasta_headers(current_path, remaining_queries, tmp_files_dir)
                    tmp_files_list.append(current_path)
                
                prev_mapping_results = mapping_results
            
        except Exception:
            raise
        finally:
            for tmp_file in tmp_files_list:
                os.remove(tmp_file)
        
        sorted_positions = mapper._sort_positions_list(mapping_results.get_mapped(), sort_param)
        mapping_results.set_mapped(sorted_positions)
        
        return mapping_results
    
    def _combine(self, unaligned, unmapped):
        combined = []
        
        combined = set(unaligned)
        combined.update(unmapped)
        #for record in unmapped:
        #    marker_id = record[0]
        #    if marker_id not in combined: # avoid redundant marker_ids
        #        combined.add(marker_id)
        
        return combined

## END
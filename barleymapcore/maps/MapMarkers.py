#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MapMarkers.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys

from SearchEngines import SearchEnginesFactory
from reader.MapReader import MapReader
from mappers.Mappers import Mappers
from enrichment.MapEnricher import MapEnricherFactory, MapEnricher
from enrichment.Enrichers import EnricherFactory

from barleymapcore.datasets.DatasetsFacade import DatasetsFacade
from barleymapcore.alignment.AlignmentResult import *
from barleymapcore.db.MapsConfig import MapsConfig
from barleymapcore.m2p_exception import m2pException

## Read conf file
ALIGN_ACTION = "align"
FIND_ACTION = "find"

class MapMarkers(object):
    
    #_config_path_dict = {}
    _maps_path = ""
    _map_config = None
    _facade = None
    _verbose = False
    _mapReader = None
    
    _mapping_results = None
    _maps_data = {}
    
    def __init__(self, maps_path, map_config, facade = None, verbose = False):
        self._maps_path = maps_path
        self._map_config = map_config
        self._facade = facade
        self._verbose = verbose
        # Load MapReader
        self._mapReader = MapReader(self._maps_path, map_config, self._verbose)
    
    def get_mapping_results(self):
        return self._mapping_results
    
    def get_map_config(self):
        return self._map_config
    
    def locate_positions(self, query_pos_path, sort_param, multiple_param):
        
        search_engine = SearchEnginesFactory.get_search_engine_positions(self._maps_path, self._verbose)
        
        mapping_results = search_engine.create_map(query_pos_path, None, self._map_config, self._facade,
                                                   sort_param, multiple_param)
        
        sys.stderr.write("MapMarkers: Map "+self._map_config.get_name()+" created.\n")
        if self._verbose: sys.stderr.write("\tNum. mapped results: "+str(len(mapping_results.get_mapped()))+".\n")
        sys.stderr.write("\n")
        
        self._mapping_results = mapping_results
        
        return mapping_results
    
    # previously: setup_map
    def retrieve_mappings(self, query_ids_path, datasets_ids, sort_param, multiple_param):
        
        search_engine = SearchEnginesFactory.get_search_engine_datasets(self._maps_path, self._verbose)
        
        mapping_results = search_engine.create_map(query_ids_path, datasets_ids, self._map_config, self._facade,
                                                   sort_param, multiple_param)
        
        sys.stderr.write("MapMarkers: Map "+self._map_config.get_name()+" created.\n")
        if self._verbose: sys.stderr.write("\tNum. mapped results: "+str(len(mapping_results.get_mapped()))+".\n")
        sys.stderr.write("\n")
        
        self._mapping_results = mapping_results
        
        return mapping_results
    
    def perform_mappings(self, query_fasta_path, databases_ids, databases_config, aligner_list,
                                threshold_id, threshold_cov, n_threads,
                                best_score_param, sort_param, multiple_param, tmp_files_dir):
        
        search_type = self._map_config.get_search_type()
        
        search_engine = SearchEnginesFactory.get_search_engine(search_type, self._maps_path,
                                                               best_score_param, databases_config, aligner_list,
                                                               threshold_id, threshold_cov, n_threads, self._verbose)
        
        mapping_results = search_engine.create_map(query_fasta_path, databases_ids, self._map_config, self._facade,
                                                   sort_param, multiple_param, tmp_files_dir)
        
        sys.stderr.write("MapMarkers: Map "+self._map_config.get_name()+" created.\n")
        sys.stderr.write("\n")
        
        self._mapping_results = mapping_results
        
        return mapping_results
    
    ### Create a map from AlignmentResult list
    ### (do not remove, used in bmap_build_datasets.py)
    def create_map(self, alignment_results, unaligned, sort_param, multiple_param):
        
        map_config = self.get_map_config()
        
        sys.stderr.write("MapMarkers: creating map: "+map_config.get_name()+"\n")
        
        map_as_physical = map_config.as_physical()
        
        mapper = Mappers.get_alignments_mapper(map_as_physical, self._mapReader, self._verbose)
        
        self._mapping_results = mapper.create_map(alignment_results, unaligned, map_config, sort_param, multiple_param)
        
        sys.stderr.write("MapMarkers: Map "+map_config.get_name()+" created.\n")
        sys.stderr.write("\n")
        
        return
    
    def _get_enriched_map(self, map_enricher, datasets_facade, datasets_ids, extend_window, collapsed_view, constrain_fine_mapping = False):
        
        sys.stderr.write("\tMap : "+self.get_map_config().get_name()+"\n")
        
        # 1) Translate mapping results to intervals
        
        map_intervals = map_enricher.map_to_intervals(extend_window)
        
        # 2) Use those intervals to
        #      obtain markers within those positions (map.as_physical)
        #      obtain contigs within those positions and, afterwards, markers anchored to them (not map.as_physical)
        # and add markers to the map
        
        enriched_map = map_enricher.enrich(map_intervals, datasets_facade, datasets_ids, collapsed_view)
        
        return enriched_map
    
    #
    def enrichment(self, annotator, show_markers, show_genes, show_anchored, show_how,
                   datasets_facade, datasets_ids, extend_window, collapsed_view, constrain_fine_mapping = False):
        
        if not (show_genes or show_markers or show_anchored): return
        
        mapping_results = self.get_mapping_results()
        
        sys.stderr.write("MapMarkers: adding features...\n")
        
        #
        if show_anchored:
            
            enricher_factory = MapEnricherFactory.get_enricher_factory(show_how)
            enricher = enricher_factory.get_anchored_enricher(self._mapReader)
            map_enricher = MapEnricherFactory.get_map_enricher(show_how, enricher, mapping_results, self._verbose)
            
            enriched_map = self._get_enriched_map(map_enricher, datasets_facade, datasets_ids, extend_window, collapsed_view, constrain_fine_mapping)
            mapping_results.set_map_with_anchored(enriched_map)
        
        if show_genes:
            
            enricher_factory = MapEnricherFactory.get_enricher_factory(show_how)
            enricher = enricher_factory.get_gene_enricher(self._mapReader, annotator)
            map_enricher = MapEnricherFactory.get_map_enricher(show_how, enricher, mapping_results, self._verbose)
            
            enriched_map = self._get_enriched_map(map_enricher, datasets_facade, datasets_ids, extend_window, collapsed_view, constrain_fine_mapping)
            mapping_results.set_map_with_genes(enriched_map)
        
        if show_markers:
            
            enricher_factory = MapEnricherFactory.get_enricher_factory(show_how)
            enricher = enricher_factory.get_marker_enricher(self._mapReader)
            map_enricher = MapEnricherFactory.get_map_enricher(show_how, enricher, mapping_results, self._verbose)
            
            enriched_map = self._get_enriched_map(map_enricher, datasets_facade, datasets_ids, extend_window, collapsed_view, constrain_fine_mapping)
            mapping_results.set_map_with_markers(enriched_map)
        
        sys.stderr.write("MapMarkers: added other features.\n")
        
        return
    
    def enrich_with_anchored(self, show_how, datasets_facade, datasets_ids, extend_window, \
                            collapsed_view = False, constrain_fine_mapping = True):
        
        enrichment(self, None, False, False, True, show_how,
                   datasets_facade, datasets_ids, extend_window, collapsed_view, constrain_fine_mapping)
        
        return
    
    def enrich_with_markers(self, show_how, datasets_facade, datasets_ids, extend_window, \
                            collapsed_view = False, constrain_fine_mapping = True):
        
        enrichment(self, None, True, False, False, show_how,
                   datasets_facade, datasets_ids, extend_window, collapsed_view, constrain_fine_mapping)
        
        return
    
    def enrich_with_genes(self, show_how, datasets_facade, datasets_ids, extend_window, \
                            annotator, collapsed_view = False, constrain_fine_mapping = True):
        
        enrichment(self, annotator, False, True, False, show_how,
                   datasets_facade, datasets_ids, extend_window, collapsed_view, constrain_fine_mapping)
        
        return

## END
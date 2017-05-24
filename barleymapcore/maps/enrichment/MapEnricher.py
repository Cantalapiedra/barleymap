#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MapEnricher.py is part of Barleymap.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys

#from Enrichers import *

from barleymapcore.maps.MapInterval import MapInterval, FeaturedMapInterval
from barleymapcore.maps.MapsBase import MapTypes

from barleymapcore.m2p_exception import m2pException

from Enrichers import EnricherFactory
from MarkerEnrichers import MarkerEnricherFactory

SHOW_ON_INTERVALS = "0"
SHOW_ON_MARKERS = "1"

class MapEnricherFactory(object):
    @staticmethod
    def get_map_enricher(show_how, enricher, mapping_results, verbose):
        map_enricher = None
        
        if show_how == SHOW_ON_INTERVALS:
            map_enricher = MapEnricher(enricher, mapping_results, verbose)
            
        elif show_how == SHOW_ON_MARKERS:
            map_enricher = MarkerEnricher(enricher, mapping_results, verbose)
            
        else:
            raise m2pException("Unrecognized show_how parameter "+str(show_how)+".")
        
        return map_enricher
    
    @staticmethod
    def get_enricher_factory(show_how):
        enricher_factory = None
        
        if show_how == SHOW_ON_INTERVALS:
            enricher_factory = EnricherFactory()
            
        elif show_how == SHOW_ON_MARKERS:
            enricher_factory = MarkerEnricherFactory()
            
        else:
            raise m2pException("Unrecognized show_how parameter "+str(show_how)+".")
        
        return enricher_factory
    
## Main class to enrich a regular map from barleymap
## with additional positional data
class MapEnricher(object):
    
    _enricher = None
    _mapping_results = None
    
    MAP_UNIT_PHYSICAL = 1 # 1 bp
    MAP_UNIT_GENETIC = 0.0001 # 0.0001 cM
    MAP_UNIT = -1

    _verbose = False
    
    def __init__(self, enricher, mapping_results, verbose = False):
        self._enricher = enricher
        self._mapping_results = mapping_results
        self._verbose = verbose
        
        return
    
    def get_mapping_results(self):
        return self._mapping_results
    
    def enrich(self, map_intervals, datasets_facade, dataset_list, collapsed_view):
        
        mapping_results = self.get_mapping_results()
        map_config = mapping_results.get_map_config()
        
        map_id = map_config.get_id()
        map_sort_by = mapping_results.get_sort_by()
        
        ### Retrieve features (what type depends on the enricher used to retrieve them)
        sys.stderr.write("MapEnricher: retrieve features...\n")
        features = []
        if len(map_intervals)>0:
            features = self._enricher.retrieve_features(map_config, map_intervals, datasets_facade, dataset_list, map_sort_by)
        if self._verbose: sys.stderr.write("\t features retrieved: "+str(len(features))+"\n")
        
        ## Enrich map
        sys.stderr.write("MapEnricher: enrich map...\n")
        enriched_map = self._enricher.enrich(mapping_results, features, collapsed_view)
        
        return enriched_map
    
    def enrich_with_anchored(self, map_intervals, datasets_facade, collapsed_view):
        
        mapping_results = self.get_mapping_results()
        map_config = mapping_results.get_map_config()
        
        # Obtain a physical- or anchored-map enricher
        #enricher = EnricherFactory.get_anchored_enricher(mapReader)
        
        map_id = map_config.get_id()
        map_sort_by = mapping_results.get_sort_by()
        
        ### Retrieve markers
        sys.stderr.write("MapEnricher: retrieve anchored...\n")
        features = self._enricher.retrieve_features(map_config, map_intervals, datasets_facade, dataset_list, map_sort_by)
        if self._verbose: sys.stderr.write("\tanchored features retrieved: "+str(len(features))+"\n")
        
        ## Enrich map
        sys.stderr.write("MapEnricher: enrich map...\n")
        enriched_map = self._enricher.enrich(mapping_results, features, collapsed_view)
        
        mapping_results.set_map_with_anchored(enriched_map)
        
        return
    
    def enrich_with_markers(self, map_intervals, datasets_facade, collapsed_view):
        
        mapping_results = self.get_mapping_results()
        map_config = mapping_results.get_map_config()
        
        # Obtain a physical- or anchored-map enricher
        #enricher = EnricherFactory.get_marker_enricher(mapReader)
        
        map_id = map_config.get_id()
        map_sort_by = mapping_results.get_sort_by()
        
        ### Retrieve markers
        sys.stderr.write("MapEnricher: retrieve markers...\n")
        features = self._enricher.retrieve_features(map_config, map_intervals, datasets_facade, dataset_list, map_sort_by)
        if self._verbose: sys.stderr.write("\tmarkers retrieved: "+str(len(features))+"\n")
        
        ## Enrich map
        sys.stderr.write("MapEnricher: enrich map...\n")
        enriched_map = self._enricher.enrich(mapping_results, features, collapsed_view)
        
        mapping_results.set_map_with_markers(enriched_map)
        
        return
    
    def enrich_with_genes(self, map_intervals, datasets_facade, annotator, collapsed_view):
        
        mapping_results = self.get_mapping_results()
        map_config = mapping_results.get_map_config()
        
        # Obtain a physical- or anchored-map enricher
        #enricher = EnricherFactory.get_gene_enricher(mapReader, annotator)
        
        map_id = map_config.get_id()
        map_sort_by = mapping_results.get_sort_by()
        
        ### Retrieve markers
        sys.stderr.write("MapEnricher: retrieve genes...\n")
        features = self._enricher.retrieve_features(map_config, map_intervals, datasets_facade, dataset_list, map_sort_by)
        if self._verbose: sys.stderr.write("\tgenes retrieved: "+str(len(features))+"\n")
        
        ## Enrich map
        sys.stderr.write("MapEnricher: enrich map...\n")
        enriched_map = self._enricher.enrich(mapping_results, features, collapsed_view)
        
        mapping_results.set_map_with_genes(enriched_map)
        
        return
    
    ## Main public function to transform a map with positions
    ## into a map of intervals
    def map_to_intervals(self, extend_window):
        
        map_sort_by = self.get_mapping_results().get_sort_by()
        
        sorted_map = self.get_mapping_results().get_mapped()
        map_intervals = self._map_intervals(sorted_map, map_sort_by, extend_window)
        
        return map_intervals
    
    ### This function iterates over each position of the map
    ### For each position, it creates an interval using extend_window
    ### If two positions overlap to each other, then the intervals are adjusted:
    ###         the previous interval ends at the new position
    ###         the new position + extend_window is a new interval
    def _map_intervals(self, sorted_map, map_sort_by, extend_window):
        map_intervals = []
        
        if self._verbose: sys.stderr.write("MapEnricher: creating intervals around markers\n")
        
        sys.stderr.write("MapEnricher: map sort by "+str(map_sort_by)+", extend interval "+str(extend_window)+"\n")
        
        if map_sort_by == MapTypes.MAP_SORT_PARAM_BP:
            self.MAP_UNIT = self.MAP_UNIT_PHYSICAL
        elif map_sort_by == MapTypes.MAP_SORT_PARAM_CM:
            self.MAP_UNIT = self.MAP_UNIT_GENETIC
        else:
            raise m2pException("Unrecognized map sort unit "+str(map_sort_by)+".")
        
        # Loop over consecutive positions to compare them and create intervals
        prev_position = None
        prev_interval = None
        for map_position in sorted_map:
            
            pos_marker = map_position.get_marker_id() #position[MapFields.MARKER_NAME_POS]
            pos_chr = map_position.get_chrom_name() #position[MapFields.MARKER_CHR_POS]
            pos_pos = map_position.get_sort_pos(map_sort_by) #float(position[map_sort_by])
            pos_end_pos = map_position.get_sort_end_pos(map_sort_by)
            
            #if self._verbose: sys.stderr.write("\tMap position: "+str(map_position)+"\n")
            
            interval = self._get_new_interval(map_position, pos_chr, pos_pos, pos_end_pos, extend_window)
            
            ## check whether intervals overlap to each other
            if prev_position:
                
                prev_chr = prev_position.get_chrom_name() #prev_position[MapFields.MARKER_CHR_POS]
                if pos_chr != prev_chr:
                    self._append_interval(map_intervals, prev_interval)
                    
                # The same chromosome...
                else:
                    # Check if there is overlap
                    if MapInterval.intervals_overlap(prev_interval, interval):
                        self._add_position_to_interval(prev_interval, map_position, pos_end_pos, extend_window)
                        interval = prev_interval
                        #if self._verbose: sys.stdout.write("\t\toverlap --> Updated interval "+str(prev_interval)+"\n")
                    else:
                        self._append_interval(map_intervals, prev_interval)
            
            # If first interval
            # else: DO NOTHING
            
            prev_position = map_position
            prev_interval = interval
        
        # Append the last interval
        if prev_interval:
            self._append_interval(map_intervals, prev_interval)
        
        sys.stderr.write("MapEnricher: "+str(len(map_intervals))+" intervals created.\n")
        
        return map_intervals
    
    def _append_interval(self, map_intervals, interval):
        map_intervals.append(interval)
        #if self._verbose: sys.stdout.write("\t\tAppended interval "+str(interval)+"\n")
        
        interval = None
        
        return
    
    def _get_new_interval(self, position, pos_chr, pos_pos, pos_end_pos, extend_window = 0):
        interval_chr = pos_chr
        interval_ini_pos = float(pos_pos) - extend_window
        if interval_ini_pos < 0:
            interval_ini_pos = 0 #self.MAP_UNIT
        
        interval_end_pos = float(pos_end_pos) + extend_window
        
        interval = MapInterval(interval_chr, interval_ini_pos, interval_end_pos)
        interval.add_position(position)
        
        #if self._verbose: sys.stdout.write("\t\tnew interval "+str(interval)+"\n")
        
        return interval
    
    def _add_position_to_interval(self, interval, position, pos_pos, extend_window):
        interval.add_position(position)
        interval.set_end_pos(float(pos_pos) + extend_window)
        
        #if self._verbose: sys.stdout.write("\t\tadded position "+str(position)+"\n")
        
        return

class MarkerEnricher(MapEnricher):
    
    def __init__(self, enricher, mapping_results, verbose = False):
        self._enricher = enricher
        self._mapping_results = mapping_results
        self._verbose = verbose
        
        return
    
    ### Overwrites _map_intervals of MapEnricher
    def _map_intervals(self, sorted_map, map_sort_by, extend_window):
        map_intervals = []
        
        if self._verbose: sys.stderr.write("MarkerEnricher: creating intervals on markers\n")
        
        sys.stderr.write("MarkerEnricher: map sort by "+str(map_sort_by)+"\n")
        
        if map_sort_by == MapTypes.MAP_SORT_PARAM_BP:
            self.MAP_UNIT = self.MAP_UNIT_PHYSICAL
        elif map_sort_by == MapTypes.MAP_SORT_PARAM_CM:
            self.MAP_UNIT = self.MAP_UNIT_GENETIC
        else:
            raise m2pException("Unrecognized map sort unit "+str(map_sort_by)+".")
        
        # Loop over consecutive positions to compare them and create intervals
        prev_position = None
        prev_interval = None
        for map_position in sorted_map:
            #sys.stderr.write("\tMap position: "+str(map_position)+"\n")
            
            pos_marker = map_position.get_marker_id() #position[MapFields.MARKER_NAME_POS]
            pos_chr = map_position.get_chrom_name() #position[MapFields.MARKER_CHR_POS]
            pos_pos = map_position.get_sort_pos(map_sort_by) #float(position[map_sort_by])
            pos_end_pos = map_position.get_sort_end_pos(map_sort_by)
            
            interval = self._get_new_interval(map_position, pos_chr, pos_pos, pos_end_pos, extend_window)
            #sys.stderr.write("\tInterval "+str(interval)+"\n")
            
            self._append_interval(map_intervals, interval)
        
        sys.stderr.write("MapEnricher: "+str(len(map_intervals))+" intervals created.\n")
        
        return map_intervals
    
    ### Overwrites _get_new_itnerval of MapEnricher
    ### to create FeaturedMapInterval instead of MapInterval
    def _get_new_interval(self, position, pos_chr, pos_pos, pos_end_pos, extend_window = 0):
        interval_chr = pos_chr
        interval_ini_pos = float(pos_pos) - extend_window
        if interval_ini_pos < 0:
            interval_ini_pos = 0 #self.MAP_UNIT
        
        interval_end_pos = float(pos_end_pos) + extend_window
        
        interval = MapInterval(interval_chr, interval_ini_pos, interval_end_pos)
        interval.add_position(position)
        interval = FeaturedMapInterval(interval)
        
        #if self._verbose: sys.stdout.write("\t\tnew interval "+str(interval)+"\n")
        
        return interval
    
## END
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MarkerEnrichers.py is part of Barleymap.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys

from barleymapcore.db.DatasetsConfig import DatasetsConfig
from barleymapcore.maps.enrichment.FeatureMapping import FeaturesFactory, FeatureMapping
from barleymapcore.maps.MappingResults import MappingResult
from barleymapcore.maps.MapInterval import MapInterval

ROW_TYPE_POSITION = "pos"
ROW_TYPE_FEATURE = "feature"
ROW_TYPE_BOTH = "both"

## Factory
class MarkerEnricherFactory(object):
    
    def __init__(self, ):
        pass
    
    @staticmethod
    def get_marker_enricher(mapReader, verbose = False):
        return MarkerEnricher(mapReader, verbose)
    
    @staticmethod
    def get_gene_enricher(mapReader, load_annot, verbose = False):
        return GeneEnricher(mapReader, load_annot, verbose)
    
    @staticmethod
    def get_anchored_enricher(mapReader, verbose = False):
        return AnchoredEnricher(mapReader, verbose)

class Enricher(object):
    
    _mapReader = None
    _verbose = False
    
    def get_enricher_type(self):
        raise m2pException("Method 'get_enricher_type' should be implemented in a class inheriting Enricher.")
    
    def get_map_reader(self):
        return self._mapReader
    
    def retrieve_features(self, map_config, map_intervals, datasets_facade, map_sort_by):
        raise m2pException("Method 'retrieve_features' should be implemented in a class inheriting Enricher.")
    
    def sort_features(self, features, map_sort_by):
        features = sorted(features, key=lambda feature_mapping: \
                        (int(feature_mapping.get_chrom_order()),
                         float(feature_mapping.get_sort_pos(map_sort_by)), float(feature_mapping.get_sort_end_pos(map_sort_by)),
                        feature_mapping.get_dataset_name(), feature_mapping.get_feature_id()))
        
        return features
    
    def enrich(self, mapping_results, features, collapsed_view = False):
        
        enriched_map = []
        
        #sys.stderr.write("MarkerEnrichers.\n")
        
        for featured_map_interval in features:
            map_interval = featured_map_interval.get_map_interval()
            #sys.stderr.write("\tinterval: "+str(map_interval)+"\n")
            
            positions = map_interval.get_positions()
            for position in positions:
                #sys.stderr.write("\tposition: "+str(position)+"\n")
                row = self._create_row(position, None, ROW_TYPE_POSITION, collapsed_view)
                enriched_map.append(row)
            
            
            features = featured_map_interval.get_features()
            for feature in features:
                #sys.stderr.write("\tfeature:"+str(feature)+"\n")
                row = self._create_row(None, feature, ROW_TYPE_FEATURE, collapsed_view)
                enriched_map.append(row)
        
        return enriched_map
    
    def _create_row(self, map_position, feature_mapping, row_type, collapsed_view):
        row = None
        
        if row_type == ROW_TYPE_POSITION:
            row = self._create_row_position(map_position, collapsed_view)
            
        elif row_type == ROW_TYPE_FEATURE:
            row = self._create_row_feature(feature_mapping, collapsed_view)
            
        elif row_type == ROW_TYPE_BOTH:
            row = self._create_row_position_feature(map_position, feature_mapping)
            
        else:
            raise m2pException("Enricher: unrecognized row type "+str(row_type)+".")
        
        if self._verbose: sys.stderr.write("Enricher: new enriched row created: "+str(row)+"\n")
        
        return row
    
    def _create_row_position(self, map_position, collapsed_view):
        
        if collapsed_view:
            new_map_position = FeaturesFactory.get_empty_feature(self.get_enricher_type())
            new_map_position.set_mapping_result(map_position)
            new_map_position.set_empty(False)
            
        else:
            feature_mapping = FeaturesFactory.get_empty_feature(self.get_enricher_type())
            
            new_map_position = map_position.clone()
            new_map_position.set_feature(feature_mapping)
        
        return new_map_position
    
    def _create_row_feature(self, feature_mapping, collapsed_view):
        
        if collapsed_view:
            new_map_position = feature_mapping.clone()
        else:
            map_position = MappingResult.get_empty()
            
            new_map_position = map_position.clone()
            new_map_position.set_feature(feature_mapping)
        
        return new_map_position
    
    def _create_row_position_feature(self, map_position, feature_mapping):
        
        new_map_position = map_position.clone()
        new_map_position.set_feature(feature_mapping)
        feature_mapping.set_row_type(FeatureMapping.ROW_TYPE_MAPPING_RESULT)
        
        return new_map_position

class MarkerEnricher(Enricher):
    
    def __init__(self, mapReader, verbose = False):
        self._mapReader = mapReader
        self._verbose = verbose
        return
    
    def retrieve_features(self, map_config, map_intervals, datasets_facade, dataset_list, map_sort_by):
        
        sys.stderr.write("MarkerEnricher: retrieve markers...\n")
        
        # 1) Obtain the translation to numeric chromosome (for sorting purposes)
        # of chromosome names
        chrom_dict = self._mapReader.get_chrom_dict()
        
        # 2) Obtain the markers in the intervals
        #
        featured_map_intervals = datasets_facade.retrieve_features_on_pos(map_intervals, map_config, chrom_dict, map_sort_by, dataset_list,
                                                           DatasetsConfig.DATASET_TYPE_GENETIC_MARKER)
        
        # 3) Sort the list by chrom and position
        for featured_map_interval in featured_map_intervals:
            features = featured_map_interval.get_features()
            features = self.sort_features(features, map_sort_by)
            featured_map_interval.set_features(features)
        
        return featured_map_intervals
    
    def get_enricher_type(self):
        return DatasetsConfig.DATASET_TYPE_GENETIC_MARKER

class AnchoredEnricher(Enricher):
    
    def __init__(self, mapReader, verbose = False):
        self._mapReader = mapReader
        self._verbose = verbose
        return
    
    def retrieve_features(self, map_config, map_intervals, datasets_facade, dataset_list, map_sort_by):
        
        sys.stderr.write("AnchoredEnricher: retrieve anchored features...\n")
        
        # 1) Obtain the translation to numeric chromosome (for sorting purposes)
        # of chromosome names
        chrom_dict = self._mapReader.get_chrom_dict()
        
        # 2) Obtain the markers in the intervals
        #
        featured_map_intervals = datasets_facade.retrieve_features_on_pos(map_intervals, map_config, chrom_dict, map_sort_by, dataset_list,
                                                           DatasetsConfig.DATASET_TYPE_ANCHORED)
        
        # 3) Sort the list by chrom and position
        for featured_map_interval in featured_map_intervals:
            features = featured_map_interval.get_features()
            features = self.sort_features(features, map_sort_by)
            featured_map_interval.set_features(features)
        
        return featured_map_intervals
    
    def get_enricher_type(self):
        return DatasetsConfig.DATASET_TYPE_ANCHORED
    
class GeneEnricher(Enricher):
    
    _annotator = None
    
    def __init__(self, mapReader, annotator, verbose = False):
        self._mapReader = mapReader
        self._annotator = annotator
        self._verbose = verbose
        return
    
    def retrieve_features(self, map_config, map_intervals, datasets_facade, dataset_list, map_sort_by):
        
        sys.stderr.write("GeneEnricher: retrieve genes...\n")
        
        # 1) Obtain the translation to numeric chromosome (for sorting purposes)
        # of chromosome names
        chrom_dict = self._mapReader.get_chrom_dict()
        
        # 2) Obtain the genes in the intervals
        #
        featured_map_intervals = datasets_facade.retrieve_features_on_pos(map_intervals, map_config, chrom_dict, map_sort_by, dataset_list,
                                                           DatasetsConfig.DATASET_TYPE_GENE)
        
        #sys.stderr.write("GeneEnricher: num features "+str(len(features))+"\n")
        
        # 3) Sort the list by chrom and position
        # 4) If required, annotate genes
        for featured_map_interval in featured_map_intervals:
            features = featured_map_interval.get_features()
            features = self.sort_features(features, map_sort_by)
            featured_map_interval.set_features(features)
            if self._annotator:
                features = self._annotator.annotate_features(features)
        
        #sys.stderr.write("GeneEnricher\n")
        #
        #for featured_map_interval in featured_map_intervals:
        #    map_interval = featured_map_interval.get_map_interval()
        #    sys.stderr.write("\tinterval: "+str(map_interval)+"\n")
        #    features = featured_map_interval.get_features()
        #    for feature in features:
        #        sys.stderr.write("\t\tfeature: "+str(feature)+"\n")
        
        return featured_map_intervals
    
    def get_enricher_type(self):
        return DatasetsConfig.DATASET_TYPE_GENE
    


######## ContigsMarkerEnricher will be useful when we want to show
######## markers which hit specific Contigs instead of by map positions.
######## For example, to show the data associated to contigs or to show
######## the markers from alignment results (which report contigs)
######## instead of from mapping results (which report map positions)

#class ContigsMarkerEnricher(MarkerEnricher):
#    
#    def __init__(self, mapReader, verbose):
#        self._mapReader = mapReader
#        self._verbose = verbose
#        return
#    
#    def retrieve_markers(self, map_config, map_intervals, datasets_facade, map_sort_by):
#        
#        sys.stderr.write("AnchoredEnricher: retrieve markers...\n")
#        
#        # 1) Obtain the contigs found in those map intervals
#        # and also the translation to numeric chromosome (for sorting purposes)
#        # of chromosome names
#        contig_list = self._mapReader.retrieve_contigs(map_intervals, map_sort_by)
#        
#        chrom_dict = self._mapReader.get_chrom_dict()
#        
#        # 2) Obtain the markers which hit to those contigs and add them to each contig
#        #   in contig_list (field "markers" of each contig)
#        
#        datasets_facade.retrieve_markers_by_anchor(contig_list, map_config)
#        
#        # 3) Reformat to have the markers but with the map positions of the contigs
#        # and sort the list by chrom and position
#        markers = self.__get_list_of_markers(contig_list, chrom_dict)
#        
#        markers = self.sort_features(markers)
#        
#        return markers
#    
#    def __get_list_of_markers(self, contig_list, chrom_dict):
#        markers = []
#        
#        for contig_dict in contig_list:
#            
#            if len(contig_dict["markers"]) == 0: continue
#            
#            pos = contig_dict["map_file_pos"]
#            chrom = contig_dict["map_file_chr"]
#            chrom_order = chrom_dict[chrom]
#            for marker in contig_dict["markers"]:
#                alignment_result = marker["alignment_result"]
#                dataset_name = marker["dataset_name"]
#                query_id = alignment_result.get_query_id()
#                
#                marker_mapping = MarkerMapping(query_id, dataset_name, chrom, chrom_order, pos)
#                markers.append(marker_mapping)
#        
#        return markers

## END
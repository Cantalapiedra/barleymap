#!/usr/bin/env python
# -*- coding: utf-8 -*-

# FeatureMapping.py is part of Barleymap.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

from barleymapcore.db.DatasetsConfig import DatasetsConfig
from barleymapcore.maps.MappingResults import MappingResult
from barleymapcore.m2p_exception import m2pException

## A class to create new FeatureMapping objects
## depending on feature_type (genetic_marker, gene, ...)
class FeaturesFactory(object):
    @staticmethod
    def get_feature(marker_id, dataset_id, dataset_name,
                feature_type, mapping_result):
        
        feature = None
        
        if feature_type == DatasetsConfig.DATASET_TYPE_GENETIC_MARKER:
            
            feature = MarkerMapping(marker_id, dataset_id, dataset_name,
                                     feature_type, mapping_result, FeatureMapping.ROW_TYPE_ENRICHMENT)
            
        elif feature_type == DatasetsConfig.DATASET_TYPE_GENE:
            
            feature = GeneMapping(marker_id, dataset_id, dataset_name,
                                    feature_type, mapping_result, FeatureMapping.ROW_TYPE_ENRICHMENT, annots = [])
            
        elif feature_type == DatasetsConfig.DATASET_TYPE_ANCHORED:
            
            feature = AnchoredMapping(marker_id, dataset_id, dataset_name,
                                      feature_type, mapping_result, FeatureMapping.ROW_TYPE_ENRICHMENT)
            
        else:
            raise m2pException("Unrecognized feature type "+str(feature_type)+".")
        
        return feature
    
    @staticmethod
    def get_empty_feature(feature_type):
        feature = None
        
        if feature_type == DatasetsConfig.DATASET_TYPE_GENETIC_MARKER:
            
            feature = MarkerMapping.get_empty()
            
        elif feature_type == DatasetsConfig.DATASET_TYPE_GENE:
            
            feature = GeneMapping.get_empty()
            
        elif feature_type == DatasetsConfig.DATASET_TYPE_ANCHORED:
            
            feature = AnchoredMapping.get_empty()
            
        else:
            raise m2pException("Unrecognized feature type "+str(feature_type)+".")
        
        return feature

# This is a class with features which can be attached to
# a MappingResult, including genes or markers in the same position, etc.
class FeatureMapping(MappingResult):
    _feature_id = ""
    _dataset_id = ""
    _dataset_name = ""
    _feature_type = "" # genetic_marker, gene, ... see DatasetsConfig
    _mapping_result = None # MappingResult object
    _row_type = ""
    _empty = False
    
    ROW_TYPE_MAPPING_RESULT = "+"
    ROW_TYPE_ENRICHMENT = "."
    
    def __init__(self, feature_id, dataset_id, dataset_name,
                 feature_type, mapping_result, row_type = ROW_TYPE_MAPPING_RESULT, empty = False):
        self._feature_id = feature_id
        self._dataset_id = dataset_id
        self._dataset_name = dataset_name
        self._feature_type = feature_type
        self._mapping_result = mapping_result
        self._row_type = row_type
        self._empty = empty
    
    def clone(self):
        new = FeatureMapping(self.get_feature_id(),
                            self.get_dataset_id(),
                            self.get_dataset_name(),
                            self.get_feature_type(),
                            self.get_mapping_result(),
                            self.get_row_type(),
                            self.is_empty())
        
        return new
    
    def __str__(self):
        return " - ".join([self._feature_id, self._dataset_id, self._dataset_name,
                           str(self._feature_type), str(self.get_mapping_result()), str(self._row_type), str(self._empty)])
    
    # An empty FeatureMapping is used in enriched maps
    # for those mapping positions without features associated
    @staticmethod
    def get_empty():
        return FeatureMapping("-", "-", "-", "-", MappingResult.get_empty(), FeatureMapping.ROW_TYPE_MAPPING_RESULT, empty = True)
    
    def is_empty(self):
        return self._empty
    
    def set_empty(self, empty):
        self._empty = empty
        
    def get_mapping_result(self):
        return self._mapping_result
    
    def set_mapping_result(self, mapping_result):
        self._mapping_result = mapping_result
    
    def get_feature_id(self):
        return self._feature_id
    
    def get_dataset_id(self):
        return self._dataset_id
    
    def get_dataset_name(self):
        return self._dataset_name
    
    def get_feature_type(self):
        return self._feature_type
    
    def get_row_type(self):
        return self._row_type
    
    def set_row_type(self, row_type):
        self._row_type = row_type
    
    ########## MappingResult methods
    def get_marker_id(self):
        return self._mapping_result.get_marker_id()
    
    def get_chrom_name(self):
        return self._mapping_result.get_chrom_name()
    
    def get_chrom_order(self):
        return self._mapping_result.get_chrom_order()
    
    def get_cm_pos(self):
        return self._mapping_result.get_cm_pos()
    
    def get_cm_end_pos(self):
        return self._mapping_result.get_cm_end_pos()
    
    def get_bp_pos(self):
        return self._mapping_result.get_bp_pos()
    
    def get_bp_end_pos(self):
        return self._mapping_result.get_bp_end_pos()
    
    def get_strand(self):
        return self._mapping_result.get_strand()
    
    def has_multiple_pos(self):
        return self._mapping_result.has_multiple_pos()
    
    def has_other_alignments(self):
        return self._mapping_result.has_other_alignments()
    
    def get_map_name(self):
        return self._mapping_result.get_map_name()
    
    def get_sort_pos(self, sort_by):
        return self._mapping_result.get_sort_pos(sort_by)
    
    def get_sort_end_pos(self, sort_by):
        return self._mapping_result.get_sort_end_pos(sort_by)
    
    def get_sort_sec_pos(self, sort_by):
        return self._mapping_result.get_sort_sec_pos(sort_by)
    
    def get_sort_end_sec_pos(self, sort_by):
        return self._mapping_result.get_sort_end_sec_pos(sort_by)
    
##############################
#
class MarkerMapping(FeatureMapping):
    # An empty MarkerMapping is used in enriched maps
    # for those mapping positions without features associated
    @staticmethod
    def get_empty():
        return MarkerMapping("-", "-", "-", "-", MappingResult.get_empty(), FeatureMapping.ROW_TYPE_MAPPING_RESULT, empty = True)
    
    def clone(self):
        new = MarkerMapping(self.get_feature_id(),
                            self.get_dataset_id(),
                            self.get_dataset_name(),
                            self.get_feature_type(),
                            self.get_mapping_result(),
                            self.get_row_type(),
                            self.is_empty())
        
        return new

#
class AnchoredMapping(FeatureMapping):
    # An empty MarkerMapping is used in enriched maps
    # for those mapping positions without features associated
    @staticmethod
    def get_empty():
        return MarkerMapping("-", "-", "-", "-", MappingResult.get_empty(), FeatureMapping.ROW_TYPE_MAPPING_RESULT, empty = True)
    
    def clone(self):
        new = MarkerMapping(self.get_feature_id(),
                            self.get_dataset_id(),
                            self.get_dataset_name(),
                            self.get_feature_type(),
                            self.get_mapping_result(),
                            self.get_row_type(),
                            self.is_empty())
        
        return new

## This is a FeatureMapping
## which in addition can hold several anotations (see GenesAnnotator)
class GeneMapping(FeatureMapping):
    _annots = []
    
    def __init__(self, feature_id, dataset_id, dataset_name,
                 feature_type, mapping_result, row_type = FeatureMapping.ROW_TYPE_ENRICHMENT,
                 empty = False, annots = []):
        self._feature_id = feature_id
        self._dataset_id = dataset_id
        self._dataset_name = dataset_name
        self._feature_type = feature_type
        self._mapping_result = mapping_result
        self._row_type = row_type
        self._empty = empty
        self._annots = annots
    
    def clone(self):
        new = GeneMapping(self.get_feature_id(),
                            self.get_dataset_id(),
                            self.get_dataset_name(),
                            self.get_feature_type(),
                            self.get_mapping_result(),
                            self.get_row_type(),
                            self.is_empty(),
                            self.get_annots())
        
        return new
    
    def __str__(self):
        retvalue = " - ".join([self._feature_id, self._dataset_id, self._dataset_name,
                           str(self._feature_type), str(self.get_mapping_result()), str(self._row_type), str(self._empty)])
        
        # Annotations
        if len(self._annots)>0:
            retvalue = retvalue + "\n\t" + "\n\t".join([str(annot) for annot in self._annots])
            
        return retvalue
    
    # An empty GeneMapping is used in enriched maps
    # for those mapping positions without features associated
    @staticmethod
    def get_empty():
        return GeneMapping("-", "-", "-", "-", MappingResult.get_empty(), FeatureMapping.ROW_TYPE_MAPPING_RESULT, empty = True, annots = [])
    
    def get_annots(self):
        return self._annots
    
    def add_annot(self, annot):
        self._annots.append(annot)
    
## END
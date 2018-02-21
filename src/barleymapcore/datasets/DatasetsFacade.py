#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DatasetsFacade.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# Copyright (C)  2016-2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys, os

from barleymapcore.db.DatasetsConfig import DatasetsConfig
#from barleymapcore.alignment.AlignmentResult import *

from DatasetsRetriever import DatasetsRetriever

class DatasetsFacade(DatasetsRetriever):
    
    _datasets_config = None
    _datasets_path = ""
    _query_ids_path = ""
    _verbose = False
    
    _datasets_retriever = None
    
    def __init__(self, datasets_config, datasets_path, maps_path, verbose = True):
        self._datasets_config = datasets_config
        self._datasets_path = datasets_path
        self._verbose = verbose
        self._datasets_retriever = DatasetsRetriever(datasets_config, datasets_path, maps_path, verbose)
    
    def get_results(self):
        return self._datasets_retriever.get_results()
    
    def get_unmapped(self):
        return self._datasets_retriever.get_unmapped()
    
    #####################################################
    # Obtain the mapping results from a dataset in a given map
    #
    def retrieve_datasets(self, query_ids_path, dataset_list, map_config, chrom_dict,
                                 multiple_param = True):
        
        results = self._datasets_retriever.retrieve_datasets_by_id(query_ids_path, dataset_list, map_config, chrom_dict,
                                                                   multiple_param)
        
        return results
    
    ### Obtain markers aligned to a series of alignment intervals
    ###
    def retrieve_features_by_pos(self, map_intervals, map_config, chrom_dict, map_sort_by, dataset_list, 
                                 feature_type = DatasetsConfig.DATASET_TYPE_GENETIC_MARKER):
        
        if self._verbose: sys.stderr.write("DatasetsFacade: loading markers associated to physical positions...\n")
        
        features = []
        
        ## Search datasets for markers
        ## associated to those contigs
        #dataset_list = self._datasets_config.get_datasets().keys()
        multiple_param = True
        
        features = self._datasets_retriever.retrieve_datasets_by_pos(map_intervals, dataset_list, map_config, chrom_dict,
                                                                   multiple_param, map_sort_by, feature_type)
        
        return features
    
    ### Obtain markers aligned on each of a series of alignment intervals
    ###
    def retrieve_features_on_pos(self, map_intervals, map_config, chrom_dict, map_sort_by, dataset_list,
                                 feature_type = DatasetsConfig.DATASET_TYPE_GENETIC_MARKER):
        
        if self._verbose: sys.stderr.write("DatasetsFacade: loading markers associated to physical positions...\n")
        
        ## Search datasets for markers
        ## associated to those contigs
        #dataset_list = self._datasets_config.get_datasets().keys()
        multiple_param = True
        
        featured_map_intervals = self._datasets_retriever.retrieve_datasets_on_pos(map_intervals, dataset_list, map_config, chrom_dict,
                                                                   multiple_param, map_sort_by, feature_type)
        
        return featured_map_intervals
    
## END
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DatasetsRetriever.py is part of Barleymap.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys, os

from barleymapcore.db.DatasetsConfig import DatasetsConfig
from barleymapcore.maps.reader.MappingsParser import MappingsParser
from barleymapcore.maps.enrichment.FeatureMapping import FeaturesFactory
from barleymapcore.m2p_exception import m2pException

class DatasetsRetriever(object):
    
    _datasets_config = None
    _datasets_path = None
    _maps_path = None
    _verbose = False
    
    _results = None
    _unmapped = None
    
    def __init__(self, datasets_config, datasets_path, maps_path, verbose = False):
        self._datasets_config = datasets_config
        self._datasets_path = datasets_path
        self._maps_path = maps_path
        self._verbose = verbose
    
    def load_synonyms(self, synonyms):
        dataset_synonyms = {}
        
        if synonyms != "" and synonyms != DatasetsConfig.SYNONYMS_NO:
            for syn_line in open(synonyms, 'r'):
                syn_data = syn_line.strip().split()
                syn_key = syn_data[0]
                if syn_key in dataset_synonyms:
                    raise m2pException("Repeated synonyms entry for marker "+syn_key+".")
                else:
                    dataset_synonyms[syn_key] = syn_data
        
        return dataset_synonyms
    
    def get_results(self):
        retvalue = None
        
        if self._results != None:
            retvalue = self._results
        else:
            raise m2pException("DatasetsRetriever: error obtaining unloaded results. Call a retrieve method first.")
        
        return retvalue
    
    def get_unmapped(self):
        retvalue = None
        
        if self._unmapped != None:
            retvalue = self._unmapped
        else:
            raise m2pException("DatasetsRetriever: error obtaining unloaded list of unmapped markers. Call a retrieve method first.")
        
        return retvalue
    
    def get_dataset_path(self, dataset, map_id, feature_type = DatasetsConfig.DATASET_TYPE_GENETIC_MARKER):
        dataset_map_path = None
        
        if feature_type == DatasetsConfig.DATASET_TYPE_MAP:
            dataset_map_path = self._maps_path+"/"+str(map_id)+"/"+str(map_id)+"."+str(dataset)
            #sys.stderr.write("DatasetsRetriever: get_dataset_path MAP TYPE "+str(dataset_map_path)+"\n")
        else:
            dataset_map_path = self._datasets_path+str(dataset)+"/"+str(dataset)+"."+str(map_id)
            #sys.stderr.write("DatasetsRetriever: get_dataset_path "+str(dataset_map_path)+"\n")
        
        return dataset_map_path
    
    def common_dbs(self, dataset_config, map_config):
        ret_value = False
        
        dataset_db_list = dataset_config.get_db_list()
        map_db_list = map_config.get_db_list()
        
        common_dbs = set(dataset_db_list).intersection(set(map_db_list))
        
        if (DatasetsConfig.DATABASES_ANY not in dataset_db_list) and (len(common_dbs)<1):
            ret_value = False
        else:
            ret_value = True
        
        return ret_value
    
    def retrieve_datasets_by_id(self, query_ids_path, dataset_list, map_config, chrom_dict, multiple_param = True):
        self._results = []
        
        self._query_ids_path = query_ids_path
        
        map_id = map_config.get_id()
        
        sys.stderr.write("DatasetsRetriever: searching "+query_ids_path+"...\n")
        
        # Load list of queries to search for
        initial_num_queries = 0
        query_ids_dict = {}
        for query_ids in open(query_ids_path, 'r'):
            query_ids_dict[query_ids.strip()] = 0
            initial_num_queries += 1
        
        num_results = 0
        num_queries_left = initial_num_queries
        
        for dataset in dataset_list:
            
            sys.stderr.write("\t dataset: "+dataset+"\n")
            
            # Check if map and dataset do share databases
            dataset_config = self._datasets_config.get_dataset_config(dataset)
            if not self.common_dbs(dataset_config, map_config):
                continue
            
            dataset_prefixes = dataset_config.get_prefixes()
            
            # Check if there are not found queries
            temp_query_dict = dict([(query, 0) for query in query_ids_dict if query_ids_dict[query] == 0])
            num_queries_left = len(temp_query_dict)
            
            if num_queries_left == 0:
                sys.stderr.write("DatasetsRetriever: All queries found.\n")
                break
            else:
                if self._verbose:
                    sys.stderr.write("\t\t MAP: "+map_id+"\n")
                    sys.stderr.write("\t\t queries to search for: "+str(num_queries_left)+"\n")
            
            # If there are dataset prefixes, search for this dataset only those queries
            # which start with those prefixes
            if len(dataset_prefixes) >= 1 and dataset_prefixes[0] != "no":
                # Check if there are not found queries
                temp_query_dict = dict([(query, 0) for query in query_ids_dict if query_ids_dict[query] == 0 and
                                                                                query.startswith(tuple(dataset_prefixes))])
            
            # If there are not queries with those prefixes (given that there are prefixes), continue
            if len(temp_query_dict) <= 0: continue
            
            #sys.stderr.write(str(temp_query_dict)+"\n")
            
            # Obtain dataset.map file
            dataset_type = dataset_config.get_dataset_type()
            dataset_map_path = self.get_dataset_path(dataset, map_id, dataset_type)
            
            ############ Retrieve dataset markers
            ############ either from mappings or from alignments
            map_results = []
            
            if os.path.exists(dataset_map_path) and os.path.isfile(dataset_map_path): # mapping results are available
                
                sys.stderr.write("\t\t path: "+dataset_map_path+"\n")
                
                if self._verbose: sys.stderr.write("\t\t loading synonyms\n")
                
                synonyms_path = dataset_config.get_synonyms()
                dataset_synonyms = self.load_synonyms(synonyms_path)
                
                if self._verbose: sys.stderr.write("\t\t creating test set\n")
                
                test_set = set(query for query in temp_query_dict)
                
                #sys.stderr.write(str(temp_query_dict)+"\n")
                
                if self._verbose: sys.stderr.write("\t\t parsing dataset file\n")
                
                mappings_parser = MappingsParser()
                map_results = mappings_parser.parse_mapping_file_by_id(temp_query_dict, dataset_map_path, map_config, chrom_dict,
                                                      multiple_param, dataset_synonyms, test_set)
                
            else:
                # TODO refactor to handled exception
                sys.stderr.write("WARNING: DatasetsRetriever: there is no available data for dataset "+dataset+"\n")
            
            num_results += len(map_results)
            if self._verbose:
                num_queries = len(set([result.get_marker_id() for result in map_results]))
                sys.stderr.write("\t\t hits found: "+str(len(map_results))+" for "+str(num_queries)+" queries.\n")
            
            sys.stderr.write("\t\t updating map results\n")
            
            query_ids_dict.update(temp_query_dict)
            
            self._results.extend(map_results)
        
        temp_query_dict = dict([(query, 0) for query in query_ids_dict if query_ids_dict[query] == 0])
        num_queries_left = len(temp_query_dict)
        
        queries_found = initial_num_queries - num_queries_left
        
        if self._verbose: sys.stderr.write("DatasetsRetriever: final number of results "+str(num_results)+"\n")
        sys.stderr.write("DatasetsRetriever: found "+str(queries_found)+" out of "+str(initial_num_queries)+"\n")
        
        self._unmapped = [query for query in query_ids_dict.keys() if query_ids_dict[query] == 0]
        
        return
    
    def retrieve_datasets_by_pos(self, map_intervals, dataset_list, map_config, chrom_dict,
                                 multiple_param, map_sort_by, feature_type = DatasetsConfig.DATASET_TYPE_GENETIC_MARKER):
        features = []
        
        map_id = map_config.get_id()
        
        # Look for markers for each dataset
        for dataset in dataset_list:
            
            sys.stderr.write("\t dataset: "+dataset+"\n")
            
            # Check if map and dataset do share databases
            dataset_config = self._datasets_config.get_dataset_config(dataset)
            if not self.common_dbs(dataset_config, map_config):
                continue
            
            dataset_type = dataset_config.get_dataset_type()
            dataset_name = dataset_config.get_dataset_name()#datasets_dict[dataset]["dataset_name"]
            
            ####### If dataset type is the type requested, pass, else (dataset type does not match the one requested) continue
            ###### Note that MAP type is a subtype of ANCHORED and therefore MAP types are accepted with ANCHORED filtering
            if dataset_type == feature_type or (dataset_type == DatasetsConfig.DATASET_TYPE_MAP and feature_type == DatasetsConfig.DATASET_TYPE_ANCHORED):
                pass
            else:
                continue
            
            if self._verbose: sys.stderr.write("\t dataset: "+dataset+"\n")
            
            ########## Retrieve markers within intervals
            ##########
            dataset_map_path = self.get_dataset_path(dataset, map_id, dataset_type)
            
            sys.stderr.write("\t\t path: "+dataset_map_path+"\n")
            
            if os.path.exists(dataset_map_path) and os.path.isfile(dataset_map_path):
                if self._verbose: sys.stderr.write("DatasetsRetriever: loading features from map data: "+dataset_map_path+"\n")
                
                mappings_parser = MappingsParser()
                mapping_results_list = mappings_parser.parse_mapping_file_by_pos(map_intervals, dataset_map_path, chrom_dict, map_config, map_sort_by)
                
                for mapping_result in mapping_results_list:
                    marker_id = mapping_result.get_marker_id()
                    
                    feature_mapping = FeaturesFactory.get_feature(marker_id, dataset, dataset_name, feature_type, mapping_result)
                    features.append(feature_mapping)
                
                #features.extend(dataset_features)
        
        return features
    
    ## This method searches features in each map_interval
    ## independently of the other map_intervals
    def retrieve_datasets_on_pos(self, map_intervals, dataset_list, map_config, chrom_dict,
                                 multiple_param, map_sort_by, feature_type = DatasetsConfig.DATASET_TYPE_GENETIC_MARKER):
        
        map_id = map_config.get_id()
        
        # Look for markers for each dataset
        for dataset in dataset_list:
            
            sys.stderr.write("\t dataset: "+dataset+"\n")
            
            # Check if map and dataset do share databases
            dataset_config = self._datasets_config.get_dataset_config(dataset)
            if not self.common_dbs(dataset_config, map_config):
                continue
            
            dataset_type = dataset_config.get_dataset_type()
            dataset_name = dataset_config.get_dataset_name()#datasets_dict[dataset]["dataset_name"]
            
            ####### If dataset type is the type requested, pass, else (dataset type does not match the one requested) continue
            ###### Note that MAP type is a subtype of ANCHORED and therefore MAP types are accepted with ANCHORED filtering
            if dataset_type == feature_type or (dataset_type == DatasetsConfig.DATASET_TYPE_MAP and feature_type == DatasetsConfig.DATASET_TYPE_ANCHORED):
                pass
            else:
                continue
            
            if self._verbose: sys.stderr.write("\t dataset: "+dataset+"\n")
            
            ########## Retrieve markers within intervals
            ##########
            dataset_map_path = self.get_dataset_path(dataset, map_id, dataset_type)
            
            sys.stderr.write("\t\t path: "+dataset_map_path+"\n")
            
            if os.path.exists(dataset_map_path) and os.path.isfile(dataset_map_path):
                if self._verbose: sys.stderr.write("DatasetsRetriever: loading features from map data: "+dataset_map_path+"\n")
                
                mappings_parser = MappingsParser()
                featured_map_intervals = mappings_parser.parse_mapping_file_on_pos(map_intervals, dataset_map_path, chrom_dict, map_config, map_sort_by,
                                                                                   dataset, dataset_name, feature_type)
        
        return featured_map_intervals

## END
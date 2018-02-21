#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DatasetsConfig.py is part of Barleymap.
# Copyright (C)  2016  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys

from barleymapcore.m2p_exception import m2pException
from barleymapcore.utils.data_utils import load_conf

class DatasetConfig(object):
    
    _dataset_name = ""
    _dataset_id = ""
    _dataset_type = ""
    _file_path = ""
    _file_type = ""
    _db_list = []
    _synonyms = ""
    _prefixes = []
    
    _ignore_build = False
    
    def __init__(self, dataset_name, dataset_id, dataset_type, file_path, file_type, db_list, synonyms, prefixes):
        self._dataset_name = dataset_name
        self._dataset_id = dataset_id
        self._dataset_type = dataset_type
        self._file_path = file_path
        self._file_type = file_type
        self._db_list = db_list
        self._synonyms = synonyms
        self._prefixes = prefixes
    
    def set_dataset_name(self, dataset_name):
        self._dataset_name = dataset_name
    
    def get_dataset_name(self):
        return self._dataset_name
    
    def get_dataset_id(self):
        return self._dataset_id
    
    def get_dataset_type(self):
        return self._dataset_type
    
    def get_file_path(self):
        return self._file_path
    
    def get_file_type(self):
        return self._file_type
    
    def get_db_list(self):
        return self._db_list
    
    def get_synonyms(self):
        return self._synonyms
    
    def get_prefixes(self, ):
        return self._prefixes
    
    def set_ignore_build(self, ignore_build):
        self._ignore_build = ignore_build
        
    def get_ignore_build(self, ):
        return self._ignore_build
    
    def __str__(self):
        return self._dataset_name+" - "+self._dataset_id+" - "+self._dataset_type+" - "+\
                self._file_path+" - "+self._file_type+" - "+",".join(self._db_list)+\
                self._synonyms+" - "+",".join(self._prefixes)
    
class DatasetsConfig(object):
    
    # Space separated fields in configuration file
    DATASET_NAME = 0
    DATASET_ID = 1
    DATASET_TYPE = 2 # genetic_markers, genes, other
    FILE_PATH = 3
    FILE_TYPE = 4 # fna, gtf, other
    DATABASES = 5 # ANY, [db,...]
    SYNONYMS = 6 # no, file path
    PREFIXES = 7
    
    # DATASET_TYPE values
    DATASET_TYPE_GENETIC_MARKER = "genetic_marker"
    DATASET_TYPE_GENE = "gene"
    DATASET_TYPE_ANCHORED = "anchored"
    DATASET_TYPE_MAP = "map" # It is a subtype of anchored feature
    #DATASET_TYPE_OTHER = "other"
    
    # FILE_TYPE values
    FILE_TYPE_FNA = "fna"
    FILE_TYPE_GTF = "gtf"
    FILE_TYPE_BED = "bed"
    FILE_TYPE_MAP = "map"
    FILE_TYPE_GFF3 = "gff3"
    #FILE_TYPE_OTHER = "other"
    
    # DATABASES values
    DATABASES_ANY = "ANY"
    #DATABASES --> list of "," separated db identifiers
    
    # SYNONYMS values
    SYNONYMS_NO = "no"
    #SYNONYMS --> file path with text tabular data, each row: 1st column is marker id, 2nd and next columns are synonyms
    
    _config_file = ""
    _verbose = False
    _config_dict = {} # dict with data from configuration file (default: conf/datasets.conf
    _config_list = [] # to store the order of datasets in the config file
    
    def __init__(self, config_file, verbose = True):
        self._config_file = config_file
        self._verbose = verbose
        self._load_config(config_file)
    
    def _load_config(self, config_file):
        self._config_dict = {}
        self._config_list = []
        
        conf_rows = load_conf(config_file, self._verbose) # data_utils.load_conf
        
        #self._config_dict = load_maps(self._config_file, self._verbose) # data_utils.load_maps
        for conf_row in conf_rows:
            
            dataset_name = conf_row[DatasetsConfig.DATASET_NAME]
            dataset_id = conf_row[DatasetsConfig.DATASET_ID]
            dataset_type = conf_row[DatasetsConfig.DATASET_TYPE]
            file_path = conf_row[DatasetsConfig.FILE_PATH]
            file_type = conf_row[DatasetsConfig.FILE_TYPE]
            databases = conf_row[DatasetsConfig.DATABASES].strip().split(",")
            synonyms = conf_row[DatasetsConfig.SYNONYMS]
            prefixes = conf_row[DatasetsConfig.PREFIXES].strip().split(",")
            
            dataset = DatasetConfig(dataset_name, dataset_id, dataset_type, file_path, file_type, databases, synonyms, prefixes)
            
            if dataset_name.startswith(">"):
                dataset.set_dataset_name(dataset_name[1:]) # remove the ">" from the name
                dataset.set_ignore_build(True) # mark the dataset as to be ignored in the build datasets script
                
            if dataset_id in self._config_dict:
                raise m2pException("Duplicated dataset "+dataset_id+" in configuration file "+config_file+".")
            else:
                self._config_dict[dataset_id] = dataset
                self._config_list.append(dataset_id)
        
        return
    
    def get_datasets(self):
        return self._config_dict
    
    def get_datasets_list(self):
        return self._config_list
    
    def get_dataset_config(self, dataset_id):
        return self._config_dict[dataset_id]
    
    def get_datasets_ids(self):
        return self._config_dict.keys()
    
    def get_datasets_configs(self):
        return self._config_dict.values()
    
    def get_datasets_names(self, datasets_ids = None):
        datasets_names = []
        
        if datasets_ids:
            for dataset_id in datasets_ids:
                found = False
                if dataset_id in self.get_datasets():
                    dataset_name = self.get_dataset_config(dataset_id).get_dataset_name()
                    datasets_names.append(dataset_name)
                    found = True
                
                if not found:
                    sys.stderr.write("WARNING: DatasetsConfig: dataset ID "+dataset+" not found in config.\n")
                    datasets_names.append(dataset)
        else:
            datasets_names = [dataset_config.get_dataset_name() for dataset_config in self.get_datasets_configs()]
        
        return datasets_names

## END    
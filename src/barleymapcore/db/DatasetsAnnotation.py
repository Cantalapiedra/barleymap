#!/usr/bin/env python
# -*- coding: utf-8 -*-

# DatasetAnnotation.py is part of Barleymap.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys
from barleymapcore.utils.data_utils import load_conf

class DatasetAnnotation(object):
    _name = ""
    _dsann_id = ""
    _dataset_id = ""
    _filename = None
    _anntype_id = None
    
    def __init__(self, name, dsann_id, dataset_id, dsann_filename, anntype_id):
        self._name = name
        self._dsann_id = dsann_id
        self._dataset_id = dataset_id
        self._filename = dsann_filename
        self._anntype_id = anntype_id
    
    def __str__(self, ):
        return " - ".join([self._name, self._dsann_id, self._dataset_id, self._filename, self._anntype_id])
    
    def get_name(self):
        return self._name
    
    def get_dataset_id(self):
        return self._dataset_id
    
    def get_anntype_id(self):
        return self._anntype_id
    
    def get_filename(self):
        return self._filename

class DatasetsAnnotation(object):
    
    # Space separated fields in configuration file
    DSANN_NAME = 0
    DSANN_ID = 1
    DSANN_DATASET_ID = 2
    DSANN_FILENAME = 3
    DSANN_TYPE_ID = 4

    _config_file = None
    _verbose = False
    
    _config_dict = {}
    _config_list = []
    
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
            
            dsann_name = conf_row[DatasetsAnnotation.DSANN_NAME]
            dsann_id = conf_row[DatasetsAnnotation.DSANN_ID]
            dsann_dataset_id = conf_row[DatasetsAnnotation.DSANN_DATASET_ID]
            dsann_filename = conf_row[DatasetsAnnotation.DSANN_FILENAME]
            dsann_type_id = conf_row[DatasetsAnnotation.DSANN_TYPE_ID]
            
            dsann = DatasetAnnotation(dsann_name, dsann_id, dsann_dataset_id, dsann_filename, dsann_type_id)
            
            self._config_dict[dsann_id] = dsann
            self._config_list.append(dsann_id)
        
        return
    
    def get_dsann_list(self):
        return self._config_list
    
    def get_dsann_config(self, dsann_id):
        return self.get_dsann()[dsann_id]
    
    def get_dsann(self):
        return self._config_dict
    
    
## END
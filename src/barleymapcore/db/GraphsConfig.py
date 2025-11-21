#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GraphsConfig.py is part of Barleymap.
# Copyright (C) 2025 Bruno Contreras, Joan Sarria
# (terms of use can be found within the distributed LICENSE file).

import sys

from barleymapcore.m2p_exception import m2pException
from barleymapcore.utils.data_utils import load_conf

# Fields in graphs.conf file
REF_NAME = 0
REF_ID = 1
REF_MAP = 2

class GraphsConfig(object):
    
    _config_file = ""
    _verbose = False
    _config_dict = {}
    
    def __init__(self, config_file, verbose = True):
        self._config_file = config_file
        self._verbose = verbose
        self._load_config(config_file)
    
    def _load_config(self, config_file):
        self._config_dict = {}
        conf_rows = load_conf(config_file, self._verbose) # data_utils.load_conf
        
        for conf_row in conf_rows:
            ref_id = conf_row[REF_ID]
            ref_name = conf_row[REF_NAME]
            ref_map = conf_row[REF_MAP]
            
            self._config_dict[ref_id] = {REF_NAME:ref_name, REF_MAP:ref_map}
        
    
    def get_graphs(self):
        return self._config_dict
    
    def get_graph(self, database_id):
        if self.database_exists(database_id):
            return self._config_dict[database_id]
        else:
            return None
    
    def get_graph_name(self, database_id):
        if self.database_exists(database_id):
            return self._config_dict[database_id][REF_NAME]
        else:
            return database_id
    
    def get_graph_map(self, database_id):
        if self.database_exists(database_id):
            return self._config_dict[database_id][REF_MAP]
        else:
            return None
  
    # for compatibility
    def get_database_type(self, database_id):
        if self.database_exists(database_id):
            return 'std'
        else:
            return None    

    def get_graphs_ids(self, databases_names = None):
        databases_ids = []
        
        if databases_names:
            # Doing this in a loop to conserve order
            for database_name in databases_names:
                found = False
                for database in self._config_dict:
                    if self._config_dict[database][REF_NAME] == database_name:
                        databases_ids.append(database)
                        found = True
                        break
                
                if not found:
                    sys.stderr.write("WARNING: GraphsConfig: database name "+database_name+" not found in config.\n")
        else:
            databases_ids = self._config_dict.keys()
        
        return databases_ids
    
    def get_graphs_names(self, databases_ids):
        databases_names = []
        
        for database in databases_ids:
            found = False
            if database in self._config_dict:
                databases_names.append(self._config_dict[database][REF_NAME])
                found = True
            
            if not found:
                sys.stderr.write("WARNING: GraphsConfig: database ID "+database+" not found in config.\n")
                databases_names.append(database)
        
        return databases_names
   
    # compatibility
    def database_exists(self, database):
        return database in self._config_dict

## END

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MapsConfig.py is part of Barleymap.
# Copyright (C)  2016  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys

from barleymapcore.m2p_exception import m2pException
from barleymapcore.utils.data_utils import load_conf
from barleymapcore.maps.MapsBase import MapTypes

class MapConfig(object):
    _name = ""
    _id = ""
    _has_cm_pos = False
    _has_bp_pos = False
    _default_sort_by = ""
    _as_physical = False
    _search_type = ""
    _db_list = None
    _map_dir = None
    _main_datasets = None
    
    def __init__(self, name, map_id, has_cm_pos, has_bp_pos, default_sort_by,
                 as_physical, search_type, db_list, map_dir, main_datasets):
        
        self._name = name
        self._id = map_id
        self._has_cm_pos = has_cm_pos
        self._has_bp_pos = has_bp_pos
        self._default_sort_by = default_sort_by
        self._as_physical = as_physical
        self._search_type = search_type
        self._db_list = db_list
        self._map_dir = map_dir
        self._main_datasets = main_datasets
        
        return
    
    # These are wrappers to use the config_dict fields just within MapsConfig class
    def get_name(self):
        return self._name
    
    def get_id(self):
        return self._id
    
    def has_cm_pos(self):
        return self._has_cm_pos
    
    def has_bp_pos(self):
        return self._has_bp_pos
    
    def get_default_sort_by(self):
        return self._default_sort_by
    
    def as_physical(self):
        return self._as_physical
    
    def get_search_type(self):
        return self._search_type
    
    def get_db_list(self):
        return self._db_list
    
    def get_map_dir(self):
        return self._map_dir
    
    def get_main_datasets(self, ):
        return self._main_datasets
    
    def check_sort_param(self, map_config, sort_param, DEFAULT_SORT_PARAM):
        sort_by = ""
        
        map_name = map_config.get_name()
        map_has_cm_pos = map_config.has_cm_pos()
        map_has_bp_pos = map_config.has_bp_pos()
        map_default_sort_by = map_config.get_default_sort_by()
        
        if sort_param == map_default_sort_by:
            sort_by = sort_param
        else:
            # sort_param has priority
            if sort_param == MapTypes.MAP_SORT_PARAM_CM and map_has_cm_pos:
                sort_by = sort_param
            elif sort_param == MapTypes.MAP_SORT_PARAM_BP and map_has_bp_pos:
                sort_by = sort_param
            # else, check map_default_sort_by
            else:
                if sort_param != DEFAULT_SORT_PARAM:
                    sys.stderr.write("WARNING: the sort parameter "+sort_param+" is not compatible with map "+map_name+". Using default map sort parameter...\n")
                if map_default_sort_by == MapTypes.MAP_SORT_PARAM_CM and map_has_cm_pos:
                    sort_by = map_default_sort_by
                elif map_default_sort_by == MapTypes.MAP_SORT_PARAM_BP and map_has_bp_pos:
                    sort_by = map_default_sort_by
                else:
                    raise m2pException("Map default sort configure as \""+map_default_sort_by+"\" assigned to a map which has not such kind of position.")
        
        return sort_by

class MapsConfig(object):
    
    # Field number (space delimited)
    # in configuration file
    MAP_NAME = 0
    MAP_ID = 1
    HAS_CM_POS = 2
    HAS_BP_POS = 3
    DEFAULT_SORT_BY = 4 # bp, cm
    AS_PHYSICAL = 5
    SEARCH_TYPE = 6
    DB_LIST = 7
    MAP_DIR = 8 # usually the same as ID, but this is really the folder name within maps_path
    MAIN_DATASETS = 9
    
    # HAS_CM_POS values
    #HAS_CM_POS_FALSE = "cm_false"
    HAS_CM_POS_TRUE = "cm_true"
    
    # HAS_BP_POS values
    #HAS_BP_POS_FALSE = "bp_false"
    HAS_BP_POS_TRUE = "bp_true"
    
    # DEFAULT_SORT_BY values
    # see
    # MapTypes.MAP_SORT_PARAM_CM and
    # MapTypes.MAP_SORT_PARAM_BP
    
    # AS_PHYSICAL values
    AS_PHYSICAL_TRUE = "physical"
    #AS_PHYSICAL_FALSE = "genetic"
    
    # SEARCH_TYPE values
    SEARCH_TYPE_GREEDY = "greedy"
    SEARCH_TYPE_HIERARCHICAL = "hierarchical"
    SEARCH_TYPE_EXHAUSTIVE = "exhaustive"

    _config_file = ""
    _verbose = False
    _config_dict = {} # dict with data from maps configuration file (default: conf/maps.conf)
    _config_list = []
    
    def __init__(self, config_file, verbose = True):
        self._config_file = config_file
        self._verbose = verbose
        self._load_config(config_file)
    
    def _load_config(self, config_file):
        self._config_dict = {}
        self._config_list = []
        conf_rows = load_conf(config_file, self._verbose) # data_utils.load_conf
        
        for conf_row in conf_rows:
            
            map_name = conf_row[self.MAP_NAME]
            map_id = conf_row[self.MAP_ID]
            
            if conf_row[self.HAS_CM_POS] == self.HAS_CM_POS_TRUE: map_has_cm = True
            else: map_has_cm = False
            
            if conf_row[self.HAS_BP_POS] == self.HAS_BP_POS_TRUE: map_has_bp = True
            else: map_has_bp = False
            
            map_default_sort_by = conf_row[self.DEFAULT_SORT_BY]
            
            if conf_row[self.AS_PHYSICAL] == self.AS_PHYSICAL_TRUE: map_physical = True
            else: map_physical = False
            
            search_type = conf_row[self.SEARCH_TYPE]
            
            map_db_list = conf_row[self.DB_LIST].split(",")
            
            map_dir = conf_row[self.MAP_DIR]
            
            main_datasets = conf_row[self.MAIN_DATASETS].split(",")
            
            map_config = MapConfig(map_name, map_id, map_has_cm, map_has_bp, map_default_sort_by,
                        map_physical, search_type, map_db_list, map_dir, main_datasets)
            
            self._config_dict[map_id] = map_config
            self._config_list.append(map_id)
    
    def get_config_file(self):
        return self._config_file
    
    def get_maps(self):
        return self._config_dict
    
    def get_maps_list(self, ):
        return self._config_list
    
    # Return tuples (map_id, map_name)
    def get_maps_tuples(self, ):
        maps_tuples = []
        
        for map_id in self._config_list:
            maps_tuples.append((map_id, self.get_map_config(map_id).get_name()))
        
        return maps_tuples
    
    def get_map_config(self, map_id):        
        if map_id in self._config_dict:#self._config_dict:
            map_config = self._config_dict[map_id]
        else:
            sys.stderr.write("WARNING: MapsConfig: map ID "+map_id+" is not in config file.\n")
        
        return map_config
    
    def get_maps_names(self, maps_ids):
        maps_names = []
        
        for map_id in maps_ids:
            if map_id in self._config_dict:
                map_config = self.get_map_config(map_id)
                maps_names.append(map_config.get_name())
            else:
                sys.stderr.write("WARNING: MapsConfig: map ID "+database+" not found in config.\n")
                maps_names.append(map_id)
        
        return maps_names
    
    def get_maps_ids(self, maps_names = None):
        maps_ids = []
        
        if maps_names:
            # changing dict[id]-->name to dict[name]-->id
            # This means that both id and name must be unique in configuration
            
            map_names_set = dict([
                                (self.get_map_config(map_id).get_name(),map_id)
                                for map_id in self.get_maps()
                                ])
            
            # Doing this in a loop to conserve order
            for map_name in maps_names:
                if map_name in map_names_set:
                    map_id = map_names_set[map_name]
                    maps_ids.append(map_id)
                else:
                    sys.stderr.write("MapsConfig: map name "+map_name+" not found in config.\n")
        else:
            maps_ids = self._config_dict.keys()
        
        return maps_ids
    
## END
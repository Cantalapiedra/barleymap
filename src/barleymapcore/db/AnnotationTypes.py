#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AnnotationTypes.py is part of Barleymap.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys
from barleymapcore.utils.data_utils import load_conf

class AnnotationType(object):
    _name = ""
    _anntype_id = ""
    _anntype_type = ""
    _anntype_attr = []
    
    def __init__(self, name, anntype_id, anntype_type, anntype_attr):
        self._name = name
        self._anntype_id = anntype_id
        self._anntype_type = anntype_type
        self._anntype_attr = anntype_attr
        
    def __str__(self):
        return " - ".join([self._name, self._anntype_id, self._anntype_type, ",".join(self._anntype_attr)])
    
    def get_anntype_id(self):
        return self._anntype_id
    
    def get_name(self):
        return self._name
    
    
class AnnotationTypes(object):
    
    # Space separated fields in configuration file
    ANNTYPE_NAME = 0
    ANNTYPE_ID = 1
    ANNTYPE_TYPE = 2 # url, text, ...
    ANNTYPE_ATTR = 3 # attrib_1,...,attrib_n
    
    # AnnotationTypes behaviour
    ANNTYPE_TYPE_URL = "url" # has a master url to link IDs in anntype_attr
    ANNTYPE_TYPE_TEXT = "text" # it just prints the text (usually, annotation description)
    
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
            
            anntype_name = conf_row[AnnotationTypes.ANNTYPE_NAME]
            anntype_id = conf_row[AnnotationTypes.ANNTYPE_ID]
            anntype_type = conf_row[AnnotationTypes.ANNTYPE_TYPE]
            anntype_attr = conf_row[AnnotationTypes.ANNTYPE_ATTR].strip().split(",")
            
            anntype = AnnotationType(anntype_name, anntype_id, anntype_type, anntype_attr)
            
            self._config_dict[anntype_id] = anntype
            self._config_list.append(anntype_id)
        
        return
    
    def get_anntype(self, anntype_id):
        return self._config_dict[anntype_id]
    
    def get_anntypes_list(self):
        return self._config_list
    
    

## END
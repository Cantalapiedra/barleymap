#!/usr/bin/env python
# -*- coding: utf-8 -*-

# PathsConfig.py is part of Barleymap.
# Copyright (C)  2016  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

from barleymapcore.utils.data_utils import read_paths
from barleymapcore.db.ConfigBase import ConfigBase

class PathsConfig(object):
    
    _config_path_dict = None
    
    # Keys in config file
    _APP_PATH = "app_path"
    _DATASETS_PATH = "datasets_path"
    _MAPS_PATH = "maps_path"
    _ANNOTATION_PATH = "annot_path"
    
    # Aux apps
    _GENMAP_PATH = "genmap_path"
    _SPLIT_BLAST_PATH = "split_blast_path"
    _BLASTN_APP_PATH = "blastn_app_path"
    _BLASTN_DBS_PATH = "blastn_dbs_path"
    _GMAP_APP_PATH = "gmap_app_path"
    _GMAP_DBS_PATH = "gmap_dbs_path"
    _GMAPL_APP_PATH = "gmapl_app_path"
    _HSBLASTN_APP_PATH = "hsblastn_app_path"
    _HSBLASTN_DBS_PATH = "hsblastn_dbs_path"
    
    # Aux dirs
    _TMP_FILES_PATH = "tmp_files_path"
    
    _CITATION = "citation"
    _STDALONE_APP = "stdalone_app"
    
    # Values read from config file
    _app_path = ""
    _genmap_path = ""
    _split_blast_path = ""
    _tmp_files_path = ""
    _datasets_path = ""
    _maps_path = ""
    _annot_path = ""
    _blastn_app_path = ""
    _blastn_dbs_path = ""
    _gmap_app_path = ""
    _gmap_dbs_path = ""
    _gmapl_app_path = ""
    _hsblastn_app_path = ""
    _hsblastn_dbs_path = ""
    _citation = ""
    _stdalone_app = ""
    
    def __init__(self):
        return
    
    def load_config(self, app_abs_path):
        paths_conf_file = app_abs_path+"/"+ConfigBase.PATHS_CONF
        self._config_path_dict = read_paths(paths_conf_file)
        
        self._app_path = self._config_path_dict[self._APP_PATH]
        self._genmap_path = self._config_path_dict[self._GENMAP_PATH]
        self._split_blast_path = self._config_path_dict[self._SPLIT_BLAST_PATH]
        self._tmp_files_path = self._config_path_dict[self._TMP_FILES_PATH]
        self._datasets_path = self._config_path_dict[self._DATASETS_PATH]
        self._maps_path = self._config_path_dict[self._MAPS_PATH]
        self._annot_path = self._config_path_dict[self._ANNOTATION_PATH]
        self._blastn_app_path = self._config_path_dict[self._BLASTN_APP_PATH]
        self._blastn_dbs_path = self._config_path_dict[self._BLASTN_DBS_PATH]
        self._gmap_app_path = self._config_path_dict[self._GMAP_APP_PATH]
        self._gmap_dbs_path = self._config_path_dict[self._GMAP_DBS_PATH]
        self._gmapl_app_path = self._config_path_dict[self._GMAPL_APP_PATH]
        self._hsblastn_app_path = self._config_path_dict[self._HSBLASTN_APP_PATH]
        self._hsblastn_dbs_path = self._config_path_dict[self._HSBLASTN_DBS_PATH]
        self._citation = self._config_path_dict[self._CITATION]
        self._stdalone_app = self._config_path_dict[self._STDALONE_APP]
        
        return
    
    def as_dict(self):
        paths_config_dict = {self._APP_PATH:self._app_path,
                             self._GENMAP_PATH:self._genmap_path,
                             self._SPLIT_BLAST_PATH:self._split_blast_path,
                             self._TMP_FILES_PATH:self._tmp_files_path,
                             self._DATASETS_PATH:self._datasets_path,
                             self._MAPS_PATH:self._maps_path,
                             self._ANNOTATION_PATH:self._annot_path,
                             self._BLASTN_APP_PATH:self._blastn_app_path,
                             self._BLASTN_DBS_PATH:self._blastn_dbs_path,
                             self._GMAP_APP_PATH:self._gmap_app_path,
                             self._GMAP_DBS_PATH:self._gmap_dbs_path,
                             self._GMAPL_APP_PATH:self._gmapl_app_path,
                             self._HSBLASTN_APP_PATH:self._hsblastn_app_path,
                             self._HSBLASTN_DBS_PATH:self._hsblastn_dbs_path,
                             self._CITATION:self._citation,
                             self._STDALONE_APP:self._stdalone_app}
        
        return paths_config_dict
    
    @staticmethod
    def from_dict(config_path_dict):
        
        paths_config = PathsConfig()
        
        paths_config._app_path = config_path_dict[paths_config._APP_PATH]
        paths_config._genmap_path = config_path_dict[paths_config._GENMAP_PATH]
        paths_config._split_blast_path = config_path_dict[paths_config._SPLIT_BLAST_PATH]
        paths_config._tmp_files_path = config_path_dict[paths_config._TMP_FILES_PATH]
        paths_config._datasets_path = config_path_dict[paths_config._DATASETS_PATH]
        paths_config._maps_path = config_path_dict[paths_config._MAPS_PATH]
        paths_config._annot_path = config_path_dict[paths_config._ANNOTATION_PATH]
        paths_config._blastn_app_path = config_path_dict[paths_config._BLASTN_APP_PATH]
        paths_config._blastn_dbs_path = config_path_dict[paths_config._BLASTN_DBS_PATH]
        paths_config._gmap_app_path = config_path_dict[paths_config._GMAP_APP_PATH]
        paths_config._gmap_dbs_path = config_path_dict[paths_config._GMAP_DBS_PATH]
        paths_config._gmapl_app_path = config_path_dict[paths_config._GMAPL_APP_PATH]
        paths_config._hsblastn_app_path = config_path_dict[paths_config._HSBLASTN_APP_PATH]
        paths_config._hsblastn_dbs_path = config_path_dict[paths_config._HSBLASTN_DBS_PATH]
        paths_config._citation = config_path_dict[paths_config._CITATION]
        paths_config._stdalone_app = config_path_dict[paths_config._STDALONE_APP]
        
        return paths_config
    
    def get_app_path(self):
        return self._app_path
    
    # Relative paths
    def get_genmap_path(self):
        return self._app_path+"/"+self._genmap_path
    
    def get_split_blast_path(self):
        return self._app_path+"/"+self._split_blast_path
    
    # Absolute paths
    
    def get_tmp_files_path(self):
        return self._tmp_files_path
    
    def get_datasets_path(self):
        return self._datasets_path
    
    def get_maps_path(self):
        return self._maps_path
    
    def get_annot_path(self):
        return self._annot_path
    
    def get_blastn_app_path(self):
        return self._blastn_app_path
    
    def get_blastn_dbs_path(self):
        return self._blastn_dbs_path
    
    def get_gmap_app_path(self):
        return self._gmap_app_path
    
    def get_gmap_dbs_path(self):
        return self._gmap_dbs_path
    
    def get_gmapl_app_path(self):
        return self._gmapl_app_path
    
    def get_hsblastn_app_path(self):
        return self._hsblastn_app_path
    
    def get_hsblastn_dbs_path(self):
        return self._hsblastn_dbs_path
    
    # Other
    def get_citation(self):
        return self._citation
    
    def get_stdalone_app(self):
        return self._stdalone_app
    
## END

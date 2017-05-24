#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GenesAnnotator.py is part of Barleymap.
# Copyright (C)  2016-2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys

from barleymapcore.maps.enrichment.FeatureMapping import GeneMapping
from barleymapcore.db.DatasetsAnnotation import DatasetsAnnotation
from barleymapcore.db.AnnotationTypes import AnnotationTypes

from AnnotationFileReader import AnnotationFileReader

## Class to obtain the Annotator, from configuration files,
## including the DatasetsAnnotation and AnnotationTypes instances
class AnnotatorsFactory(object):
    @staticmethod
    def get_annotator(dsannot_conf_file, anntypes_conf_file, annot_path, verbose = False):
        annotator = None
        
        dsann_config = DatasetsAnnotation(dsannot_conf_file, verbose)
        anntypes_config = AnnotationTypes(anntypes_conf_file, verbose)
        
        annotator = GenesAnnotator(dsann_config, anntypes_config, annot_path)
        
        return annotator
    
## This class reads annotations for a given gene from a dataset
## and appends them to the GeneMapping object
class GenesAnnotator(object):
    _dsann_config = ""
    _anntypes_config = ""
    
    _annot_reader = None
    _loaded_anntypes = set()
    
    _verbose = False
    
    def __init__(self, dsann_config, anntypes_config, annot_path, verbose = False):
        self._dsann_config = dsann_config
        self._anntypes_config = anntypes_config
        self._annot_reader = AnnotationFileReader(annot_path)
        self._loaded_anntypes = set()
        self._verbose = verbose
    
    ## Filter out the dictionary of annotations (DatasetsAnnotation)
    ## to keep only those from the given dataset
    def get_dataset_annots(self, dataset_id):
        dsannots = self._dsann_config.get_dsann()
        dataset_annots = dict([(dsannot_id, dsannots[dsannot_id]) for dsannot_id in dsannots if dsannots[dsannot_id].get_dataset_id()==dataset_id])
        
        return dataset_annots
    
    ## This is the main method to add annotations to a list
    ## of features (GeneMappings)
    def annotate_features(self, features):
        
        sys.stderr.write("GenesAnnotator: annotate_features\n")
        
        for gene_mapping in features:
            
            # Obtain the annotations of this dataset (DatasetsAnnotation)
            dataset_id = gene_mapping.get_dataset_id()
            dataset_annots = self.get_dataset_annots(dataset_id)
            
            if self._verbose:
                if len(dataset_annots)>0:
                    sys.stderr.write(str(gene_mapping)+"\n\t"+str(dataset_annots)+"\n")
                else:
                    sys.stderr.write("No annotation for dataset "+dataset_id+"\n")
            
            # Obtain the records of this particular gene (GeneMapping)
            gene_id = gene_mapping.get_feature_id()
            
            for dataset_annot_id in dataset_annots:
                
                dataset_annot = dataset_annots[dataset_annot_id]
                
                anntype_id = dataset_annot.get_anntype_id()
                anntype = self._anntypes_config.get_anntype(anntype_id)
                
                # Load the records of the annotation files
                if not dataset_annot_id in self._annot_reader.get_loaded_annots():
                    dataset_annot_filename = dataset_annot.get_filename()
                    self._annot_reader.load_annots(dataset_annot_id, dataset_annot_filename, anntype)
                    
                dataset_annot_data = self._annot_reader.get_loaded_annot(dataset_annot_id)
                
                if gene_id in dataset_annot_data:
                    gene_annotation = dataset_annot_data[gene_id]
                    gene_mapping.add_annot(gene_annotation)
                    
                    #sys.stderr.write("Gene:\t"+str(gene_id)+"\t"+str(anntype_id)+"\t"+str(gene_annotation)+"\n")
                    
                    # It was not registered previously,
                    # mark that data from this AnnotationType
                    # has been included in results (features)
                    if anntype_id not in self._loaded_anntypes:
                        self._loaded_anntypes.add(anntype_id)
                    
                #else: continue
        
        return features
    
    def get_loaded_anntypes(self):
        return self._loaded_anntypes
    
    def get_anntypes_config(self):
        return self._anntypes_config
    
    def get_dsann_config(self):
        return self._dsann_config
    
    def get_annot_reader(self):
        return self._annot_reader
    
    
## END
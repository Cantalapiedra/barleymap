#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AnnotationFileReader.py is part of Barleymap.
# Copyright (C)  2016-2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

from GeneAnnotation import GeneAnnotation

class AnnotationFile(object):
    
    # Column numbers (tab separated) in annotation files
    ANNOT_FILE_GENE_ID = 0
    ANNOT_FILE_FEATURE = 1
    
class AnnotationFileReader(object):
    
    _annot_path = ""
    _loaded_annots = {}
    
    def __init__(self, annot_path):
        self._annot_path = annot_path
        self._loaded_annots = {}
    
    ## Creates a dict for a single DatasetAnnotation
    ## with the data from the AnnotationFile
    ## {gene_id, ...} --> [annot_feature (GO ID, PFAM ID, etc), ...]
    ## includes it within loaded_annots dict
    def load_annots(self, dsannot_id, dsannot_filename, anntype):
        
        dataset_annot_data = {}
        
        for annot_line in open(self._annot_path+"/"+dsannot_filename, 'r'):
            annot_data = annot_line.strip().split("\t")
            
            annot_gene_id = annot_data[AnnotationFile.ANNOT_FILE_GENE_ID]
            annot_feature = annot_data[AnnotationFile.ANNOT_FILE_FEATURE]
            
            if annot_gene_id in dataset_annot_data:
                gene_annotation = dataset_annot_data[annot_gene_id]
            else:
                gene_annotation = GeneAnnotation(anntype)
                dataset_annot_data[annot_gene_id] = gene_annotation
                
            gene_annotation.add_feature(annot_feature)
            
        self._loaded_annots[dsannot_id] = dataset_annot_data
        
        return
    
    def get_loaded_annots(self):
        return self._loaded_annots
    
    def get_loaded_annot(self, dataset_annot_id):
        if dataset_annot_id in self._loaded_annots:
            retvalue = self._loaded_annots[dataset_annot_id]
        else:
            retvalue = None
        return retvalue

## END
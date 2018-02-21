#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GeneAnnotation.py is part of Barleymap.
# Copyright (C)  2016-2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

# This class represents a single annotation of a GeneMapping
#
class GeneAnnotation(object):
    _annot_data = [] # has the list of annotations
    _anntype = None # has the type (AnnotationType) of the annotation
    
    def __init__(self, anntype):
        self._annot_data = []
        self._anntype = anntype
    
    def __str__(self):
        return " - ".join([str(self._anntype), ",".join(self._annot_data)])
    
    def add_feature(self, annot_feature):
        self._annot_data.append(annot_feature)
        return
    
    def get_annot_data(self):
        return self._annot_data
    
    def get_anntype(self):
        return self._anntype

## END
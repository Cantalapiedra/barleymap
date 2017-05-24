#!/usr/bin/env python
# -*- coding: utf-8 -*-

# CSVWriter.py is part of Barleymap web app.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys, os, tempfile

from barleymapcore.output.OutputFacade import OutputFacade
#from barleymapcore.maps.MapsBase import MapFields, MapHeaders
#from barleymapcore.genes.GenesBase import GenesFields, AnnotFields
#from barleymapcore.maps.MarkersBase import MarkersFields

class MapCSVFiles(object):
    
    _map_id = None
    
    _mapped = None
    _map_with_markers = None
    _map_with_genes = None
    _map_with_anchored = None
    _unmapped = None
    _unaligned = None
    
    def __init__(self, map_id):
        self._map_id = map_id
        
    def get_mapped(self, ):
        return self._mapped
    
    def set_mapped(self, mapped):
        self._mapped = mapped
    
    def get_map_with_markers(self, ):
        return self._map_with_markers
    
    def set_map_with_markers(self, map_with_markers):
        self._map_with_markers = map_with_markers
    
    def get_map_with_genes(self, ):
        return self._map_with_genes
    
    def set_map_with_genes(self, map_with_genes):
        self._map_with_genes = map_with_genes
    
    def get_map_with_anchored(self, ):
        return self._map_with_anchored
    
    def set_map_with_anchored(self, map_with_anchored):
        self._map_with_anchored = map_with_anchored
    
    def get_unmapped(self, ):
        return self._unmapped
    
    def set_unmapped(self, unmapped):
        self._unmapped = unmapped
    
    def get_unaligned(self, ):
        return self._unaligned
    
    def set_unaligned(self, unaligned):
        self._unaligned = unaligned

class CSVFiles(object):
    
    _map_csv_files = {}
    
    def __init__(self, ):
        pass
    
    def get_maps_csv_files(self, ):
        return self._map_csv_files
    
    def get_map_csv_files(self, map_id):
        return self._map_csv_files[map_id]
    
    def set_map_csv_files(self, map_id, map_csv_files):
        self._map_csv_files[map_id] = map_csv_files

##
class CSVWriter(object):
    
    _paths_config = None
    _verbose = False
    
    def __init__(self, paths_config, verbose = False):
        self._paths_config = paths_config
        self._verbose = verbose
    
    def _output_map(self, mapping_results, output_printer, multiple_param):
        
        file_name = None
        
        try:
            tmp_files_path = self._paths_config.get_tmp_files_path()
            
            (file_desc, file_name) = tempfile.mkstemp(suffix="_csv", dir=tmp_files_path)
            
            csv_file = os.fdopen(file_desc, 'wb')
            
            output_printer.set_output_desc(csv_file)
            
            positions = mapping_results.get_mapped()
            map_config = mapping_results.get_map_config()
            
            rows = output_printer.print_map(positions, map_config, multiple_param)
            
        except Exception:
            raise
        finally:
            csv_file.close()
        
        return file_name
    
    def _output_map_with_markers(self, mapping_results, output_printer, multiple_param):
        
        file_name = None
        
        try:
            tmp_files_path = self._paths_config.get_tmp_files_path()
            
            (file_desc, file_name) = tempfile.mkstemp(suffix="_csv", dir=tmp_files_path)
            
            csv_file = os.fdopen(file_desc, 'wb')
            
            output_printer.set_output_desc(csv_file)
            
            positions = mapping_results.get_map_with_markers()
            map_config = mapping_results.get_map_config()
            
            rows = output_printer.print_map_with_markers(positions, map_config, multiple_param)
            
        except Exception:
            raise
        finally:
            csv_file.close()
        
        return file_name
    
    def _output_map_with_genes(self, mapping_results, output_printer, multiple_param, annotator):
        
        file_name = None
        
        try:
            tmp_files_path = self._paths_config.get_tmp_files_path()
            
            (file_desc, file_name) = tempfile.mkstemp(suffix="_csv", dir=tmp_files_path)
            
            csv_file = os.fdopen(file_desc, 'wb')
            
            output_printer.set_output_desc(csv_file)
            
            positions = mapping_results.get_map_with_genes()
            map_config = mapping_results.get_map_config()
            
            load_annot = True # always True
            rows = output_printer.print_map_with_genes(positions, map_config, multiple_param, load_annot, annotator)
            
        except Exception:
            raise
        finally:
            csv_file.close()
        
        return file_name
    
    def _output_map_with_anchored(self, mapping_results, output_printer, multiple_param):
        
        file_name = None
        
        try:
            tmp_files_path = self._paths_config.get_tmp_files_path()
            
            (file_desc, file_name) = tempfile.mkstemp(suffix="_csv", dir=tmp_files_path)
            
            csv_file = os.fdopen(file_desc, 'wb')
            
            output_printer.set_output_desc(csv_file)
            
            positions = mapping_results.get_map_with_anchored()
            map_config = mapping_results.get_map_config()
            
            rows = output_printer.print_map_with_anchored(positions, map_config, multiple_param)
            
        except Exception:
            raise
        finally:
            csv_file.close()
        
        return file_name
    
    def _output_unmapped(self, mapping_results, output_printer):
        
        file_name = None
        
        try:
            tmp_files_path = self._paths_config.get_tmp_files_path()
            
            (file_desc, file_name) = tempfile.mkstemp(suffix="_csv", dir=tmp_files_path)
            
            csv_file = os.fdopen(file_desc, 'wb')
            
            output_printer.set_output_desc(csv_file)
            
            unmapped = mapping_results.get_unmapped()
            map_config = mapping_results.get_map_config()
            
            rows = output_printer.print_unmapped(unmapped, map_config)
            
        except Exception:
            raise
        finally:
            csv_file.close()
        
        return file_name
    
    def _output_unaligned(self, mapping_results, output_printer):
        
        file_name = None
        
        try:
            tmp_files_path = self._paths_config.get_tmp_files_path()
            
            (file_desc, file_name) = tempfile.mkstemp(suffix="_csv", dir=tmp_files_path)
            
            csv_file = os.fdopen(file_desc, 'wb')
            
            output_printer.set_output_desc(csv_file)
            
            unaligned = mapping_results.get_unaligned()
            map_config = mapping_results.get_map_config()
            
            rows = output_printer.print_unaligned(unaligned, map_config)
            
        except Exception:
            raise
        finally:
            csv_file.close()
        
        return file_name
    
    def output_maps(self, all_mapping_results, form):
        
        csv_files = CSVFiles()
        
        ## Obtain OutputPrinter: out file set to None. CSV file will be asigned later
        beauty_nums = True
        show_headers = True
        if form.get_collapsed_view():
            output_printer = OutputFacade.get_collapsed_printer(None, self._verbose, beauty_nums, show_headers)
        else:
            output_printer = OutputFacade.get_expanded_printer(None, self._verbose, beauty_nums, show_headers)
        
        ## Output the different maps
        multiple_param = form.get_multiple()
        
        for mapping_results in all_mapping_results:
            
            map_config = mapping_results.get_map_config()
            map_id = map_config.get_id()
            
            map_csv_files = MapCSVFiles(map_id)
            csv_files.set_map_csv_files(map_id, map_csv_files)
            
            ## Map positions
            csv_file = self._output_map(mapping_results, output_printer, multiple_param)
            map_csv_files.set_mapped(csv_file)
            
            ## Enriched
            if form.get_show_markers() and mapping_results.get_map_with_markers():
                csv_file = self._output_map_with_markers(mapping_results, output_printer, multiple_param)
                map_csv_files.set_map_with_markers(csv_file)
            
            if form.get_show_genes() and mapping_results.get_map_with_genes():
                annotator = mapping_results.get_annotator()
                csv_file = self._output_map_with_genes(mapping_results, output_printer, multiple_param, annotator)
                map_csv_files.set_map_with_genes(csv_file)
            
            if form.get_show_anchored() and mapping_results.get_map_with_anchored():
                csv_file = self._output_map_with_anchored(mapping_results, output_printer, multiple_param)
                map_csv_files.set_map_with_anchored(csv_file)
            
            ## Unmapped
            if mapping_results.get_unmapped():
                csv_file = self._output_unmapped(mapping_results, output_printer)
                map_csv_files.set_unmapped(csv_file)
            ## Unaligned
            if mapping_results.get_unaligned():
                csv_file = self._output_unaligned(mapping_results, output_printer)
                map_csv_files.set_unaligned(csv_file)
        
        return csv_files

## END
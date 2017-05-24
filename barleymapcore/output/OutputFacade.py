#!/usr/bin/env python
# -*- coding: utf-8 -*-

# OutputFacade.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys

from barleymapcore.db.DatasetsConfig import DatasetsConfig
from barleymapcore.maps.MapsBase import MapTypes
from barleymapcore.m2p_exception import m2pException

from barleymapcore.alignment.AlignmentEngines import ALIGNMENT_TYPE_GREEDY, ALIGNMENT_TYPE_HIERARCHICAL, ALIGNMENT_TYPE_BEST_SCORE

MAPPED_TITLE = ""
UNMAPPED_TITLE = "_Unmapped"
UNALIGNED_TITLE = "_Unaligned"
MAP_WITH_GENES_TITLE = "_with_genes"
MAP_WITH_MARKERS_TITLE = "_with_markers"
MAP_WITH_ANCHORED_TITLE = "_with_anchored_features"

class MapHeaders(object):
    
    MARKER_NAME_POS = 0
    MARKER_CHR_POS = 1
    MARKER_CM_POS = 2
    MARKER_BP_POS = 3
    MULTIPLE_POS = 4
    OTHER_ALIGNMENTS = 5
    MAP_NAME = 6
    
    PHYSICAL_ID = 0
    PHYSICAL_CHR = 1
    PHYSICAL_START_POS = 2
    PHYSICAL_END_POS = 3
    PHYSICAL_STRAND = 4
    PHYSICAL_MULTIPLE_POS = 5
    PHYSICAL_OTHER_ALIGNMENTS = 6
    PHYSICAL_MAP_NAME = 7
    
    OUTPUT_HEADERS = ["Marker", "chr", "cM", "base_pairs", "multiple_positions", "other_alignments", "Map"]
    PHYSICAL_HEADERS = ["Marker", "chr", "start", "end", "strand", "multiple_positions", "other_alignments", "Map"]
    FEATURE_HEADERS = ["Feature", "Feature_type", "Dataset", "chr", "cM", "bp"]
    
    ANNOT_HEADERS = ["Description", "InterPro", "Signatures", "PFAM server", "GO terms"]

class MarkersFields(object):
    
    MARKER_ID_POS = 0
    MARKER_DATASET_POS = 1
    MARKER_CHR_POS = 2
    MARKER_CM_POS = 3
    MARKER_BP_POS = 4
    MARKER_GENES_POS = 5
    MARKER_GENES_CONFIGURED_POS = 6
    
    MARKERS_FIELDS = 7

class GenesFields(object):
    
    GENES_ID_POS = 0
    GENES_TYPE_POS = 1
    GENES_DATASET_NAME_POS = 2
    GENES_CHR_POS = 3
    GENES_CM_POS = 4
    GENES_BP_POS = 5
    
    GENES_FIELDS = 6

class AnnotFields(object):
    
    GENES_ANNOT_DESC = 0
    GENES_ANNOT_INTERPRO = 1
    GENES_ANNOT_PFAM = 2
    GENES_ANNOT_SERVER = 3
    GENES_ANNOT_GO = 4
    
    GENES_ANNOT_FIELDS = 5

class OutputFacade(object):
    
    @staticmethod
    def get_alignments_printer(search_type, databases_config):
        alignments_printer = None
        
        if search_type == ALIGNMENT_TYPE_GREEDY:
            alignments_printer = AlignmentsGreedyPrinter(databases_config)
        elif search_type == ALIGNMENT_TYPE_HIERARCHICAL:
            alignments_printer = AlignmentsHierarchicalPrinter(databases_config)
        elif search_type == ALIGNMENT_TYPE_BEST_SCORE:
            alignments_printer = AlignmentsBestScorePrinter(databases_config)
        else:
            raise m2pException("Unrecognized search type "+search_type+".")
        
        return alignments_printer
    
    @staticmethod
    def get_expanded_printer(output_desc, verbose = False, beauty_nums = False, show_headers = True):
        output_printer = ExpandedPrinter(output_desc, verbose, beauty_nums, show_headers)
        
        return output_printer
    
    @staticmethod
    def get_collapsed_printer(output_desc, verbose = False, beauty_nums = False, show_headers = True):
        output_printer = CollapsedPrinter(output_desc, verbose, beauty_nums, show_headers)
        
        return output_printer

########## AlignmentsPrinter
class AlignmentsPrinter(object):
    
    _databases_config = None
    
    def __init__(self, databases_config):
        self._databases_config = databases_config
    
    def output_results(self, aligned, databases_ids = None):
        raise Exception("To be implemented in child classes inheriting from AlignmentsPrinter")
    
    def print_header(self):
        sys.stdout.write("#"+"\t".join(["query_id", "subject_id", "identity", "query_coverage", \
                                        "score", "strand", "qstart", "qend", "sstart", "send",
                                        "database", "algorithm"])+"\n")
    
    def print_records_db(self, aligned, db_entry, db_name):
        # records
        for alignment_result in aligned: #db_results:
            
            if alignment_result.get_db_id() != db_entry: continue
            
            self.print_record(alignment_result, db_name)
        
        return
    
    def print_records(self, aligned):
        # records
        for alignment_result in aligned: #db_results:
            
            db_name = self._databases_config.get_database_name(alignment_result.get_db_id())
            
            self.print_record(alignment_result, db_name)
        
        return
    
    def print_record(self, alignment_result, db_name = None):
        sys.stdout.write("\t".join([
                alignment_result.get_query_id(),
                alignment_result.get_subject_id(),
                str("%0.2f" % float(alignment_result.get_align_ident())),
                str("%0.2f" % float(alignment_result.get_query_cov())),
                str(alignment_result.get_align_score()),
                str(alignment_result.get_strand()),
                str(alignment_result.get_qstart_pos()),
                str(alignment_result.get_qend_pos()),
                str(alignment_result.get_local_position()),
                str(alignment_result.get_end_position()),
                str(db_name),
                str(alignment_result.get_algorithm())
            ]))
        sys.stdout.write("\n")
        
        return

class AlignmentsGreedyPrinter(AlignmentsPrinter):
    
    def output_results(self, aligned, databases_ids = None):
        
        if not databases_ids: raise m2pException("AlignmentsGreedyPrinter needs a list of DBs.")
        
        for db_entry in databases_ids:
            
            db_name = self._databases_config.get_database_name(db_entry)
            
            sys.stdout.write(">"+str(db_name)+"\n")
            self.print_header()
            self.print_records_db(aligned, db_entry, db_name)
        
        return

class AlignmentsHierarchicalPrinter(AlignmentsPrinter):
    
    def output_results(self, aligned, databases_ids = None):
        sys.stdout.write(">Alignments\n")
        self.print_header()
        self.print_records(aligned)
        
        return
    
class AlignmentsBestScorePrinter(AlignmentsPrinter):
    
    def output_results(self, aligned, databases_ids = None):
        sys.stdout.write(">Alignments\n")
        self.print_header()
        self.print_records(aligned)
        
        return

########## OutputPrinter base output printer class
########## This should be treated as an Abstract class
########## to be fully implemented in children classes
class OutputPrinter(object):
    
    _output_desc = None
    _verbose = False
    _beauty_nums = False
    _show_headers = True
    
    def __init__(self, output_desc, verbose = False, beauty_nums = False, show_headers = True):
        self._output_desc = output_desc
        self._verbose = verbose
        self._beauty_nums = beauty_nums
        self._show_headers = show_headers
    
    def set_output_desc(self, output_desc):
        self._output_desc = output_desc
    
    # Methods to be implemented in the child class
    def output_features_header(self, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param, load_annot = False, annotator = None):
        raise m2pException("Method has to be implemented in child class inheriting from OutputPrinter")
    
    def output_features_pos(self, pos, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param, load_annot = False, annotator = None):
        raise m2pException("Method has to be implemented in child class inheriting from OutputPrinter")
    
    def print_maps(self, maps_dict, show_genes, show_markers, show_anchored, show_unmapped, show_unaligned, multiple_param, load_annot, annotator):
        
        for map_id in maps_dict:
            mapping_results = maps_dict[map_id]
            map_config = mapping_results.get_map_config()
            
            if not (show_genes or show_markers or show_anchored):
                ########## OUTPUT FOR ONLY MAP
                
                self.print_map(mapping_results.get_mapped(), map_config, multiple_param)
            
            elif show_genes:
                ########## OUTPUT FOR MAP WITH GENES IF REQUESTED
                
                self.print_map_with_genes(mapping_results.get_map_with_genes(), map_config, multiple_param, load_annot, annotator)
            
            elif show_markers:
                ########### OUTPUT FOR MAP WITH MARKERS
                
                self.print_map_with_markers(mapping_results.get_map_with_markers(), map_config, multiple_param)
                
            elif show_anchored:
                ########### OUTPUT FOR MAP WITH ANCHORED FEATURES
                
                self.print_map_with_anchored(mapping_results.get_map_with_anchored(), map_config, multiple_param)
                
            # else: this could never happen!?
            
            if show_unmapped:
                self.print_unmapped(mapping_results.get_unmapped(), map_config)
                
            if show_unaligned:
                self.print_unaligned(mapping_results.get_unaligned(), map_config)
        
        ######
    
    def _print_map_header(self, map_name, map_title = ""):
        self._output_desc.write(">"+map_name+map_title+"\n")
        
        return
    
    def print_map(self, mapping_results, map_config, multiple_param):
        map_name = map_config.get_name()
        
        sys.stderr.write("OutputFacade: creating output for map "+str(map_name)+"\n")
        
        map_title = MAPPED_TITLE
        self._print_map_header(map_name, map_title)
        
        map_as_physical = map_config.as_physical()
        map_has_cm_pos = map_config.has_cm_pos()
        map_has_bp_pos = map_config.has_bp_pos()
        
        sys.stderr.write("\tprinting plain genetic map...\n")
        
        ## Header
        if self._show_headers:
            headers_row = self.output_base_header(map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            self._output_desc.write("#"+"\t".join(headers_row)+"\n")
        
        ## Rows
        positions = mapping_results#.get_mapped()
        for pos in positions:
            current_row = self.output_base_pos(pos, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            self._output_desc.write("\t".join([str(x) for x in current_row])+"\n")
        
        sys.stderr.write("\tgenetic maps printed.\n")
        
        if self._verbose: sys.stderr.write("\tlines printed "+str(len(positions))+"\n")
        
        return
    
    def print_map_with_genes(self, mapping_results, map_config, multiple_param, load_annot, annotator):
        
        map_name = map_config.get_name()
        
        sys.stderr.write("OutputFacade: creating output for map with genes "+str(map_name)+"\n")
        
        map_title = MAP_WITH_GENES_TITLE
        self._print_map_header(map_name, map_title)
        
        map_as_physical = map_config.as_physical()
        #map_sort_by = mapping_results.get_sort_by()
        map_has_cm_pos = map_config.has_cm_pos()
        map_has_bp_pos = map_config.has_bp_pos()
        
        ## Header
        if self._show_headers:
            
            headers_row = self.output_features_header(map_as_physical, map_has_cm_pos, map_has_bp_pos,
                                                      multiple_param, load_annot, annotator)
            
            self._output_desc.write("#"+"\t".join(headers_row)+"\n")
        
        ## Rows
        positions = mapping_results#.get_map_with_genes()
        for pos in positions:
            
            current_row = self.output_features_pos(pos, map_as_physical, map_has_cm_pos, map_has_bp_pos,
                                                    multiple_param, load_annot, annotator)
            
            self._output_desc.write("\t".join([str(x) for x in current_row])+"\n")
            
        sys.stderr.write("OutputFacade: map with genes printed.\n")
        
        if self._verbose: sys.stderr.write("\tlines printed "+str(len(positions))+"\n")
        
        return
    
    def print_map_with_markers(self, mapping_results, map_config, multiple_param):
        
        map_name = map_config.get_name()
        
        sys.stderr.write("OutputFacade: creating output for map with markers "+str(map_name)+"\n")
        
        map_title = MAP_WITH_MARKERS_TITLE
        self._print_map_header(map_name, map_title)
        
        map_as_physical = map_config.as_physical()
        #map_sort_by = mapping_results.get_sort_by()
        map_has_cm_pos = map_config.has_cm_pos()
        map_has_bp_pos = map_config.has_bp_pos()
        
        ## Header
        if self._show_headers:
            
            headers_row = self.output_features_header(map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            self._output_desc.write("#"+"\t".join(headers_row)+"\n")
        
        ## Rows
        positions = mapping_results#.get_map_with_markers()
        for pos in positions:
            
            current_row = self.output_features_pos(pos, map_as_physical, map_has_cm_pos, map_has_bp_pos,
                                                    multiple_param)
            
            self._output_desc.write("\t".join([str(x) for x in current_row])+"\n")
            
        sys.stderr.write("OutputFacade: map with markers printed.\n")
        
        if self._verbose: sys.stderr.write("\tlines printed "+str(len(positions))+"\n")
        
        return
    
    def print_map_with_anchored(self, mapping_results, map_config, multiple_param):
        
        map_name = map_config.get_name()
        
        sys.stderr.write("OutputFacade: creating output for map with anchored features "+str(map_name)+"\n")
        
        map_title = MAP_WITH_ANCHORED_TITLE
        self._print_map_header(map_name, map_title)
        
        map_as_physical = map_config.as_physical()
        #map_sort_by = mapping_results.get_sort_by()
        map_has_cm_pos = map_config.has_cm_pos()
        map_has_bp_pos = map_config.has_bp_pos()
        
        ## Header
        if self._show_headers:
            
            headers_row = self.output_features_header(map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            self._output_desc.write("#"+"\t".join(headers_row)+"\n")
        
        ## Rows
        positions = mapping_results#.get_map_with_markers()
        for pos in positions:
            
            current_row = self.output_features_pos(pos, map_as_physical, map_has_cm_pos, map_has_bp_pos,
                                                    multiple_param)
            
            self._output_desc.write("\t".join([str(x) for x in current_row])+"\n")
            
        sys.stderr.write("OutputFacade: map with anchored features printed.\n")
        
        if self._verbose: sys.stderr.write("\tlines printed "+str(len(positions))+"\n")
        
        return
    
    # OutputPrinter base methods
    def print_unmapped(self, mapping_results, map_config):
        
        map_name = map_config.get_name()
        map_as_physical = map_config.as_physical()
        
        sys.stderr.write("OutputFacade: creating output for unmapped of "+str(map_name)+" map\n")
        
        # physical maps do not have anchored contigs, and thus contigs
        # never lack map position
        if not map_as_physical:
            ############ UNMAPPED
            map_title = UNMAPPED_TITLE
            self._print_map_header(map_name, map_title)
            
            unmapped_records = mapping_results#.get_unmapped()
            if unmapped_records != None: # those obtained from mapping results have no unmapped records
                self._output_unmapped(unmapped_records)
        
        return
    
    def _output_unmapped(self, unmapped_records):
        sys.stderr.write("\tprinting unmapped...\n")
        
        #self._output_desc.write("##"+section_name+"\n")
        if self._show_headers:
            self._output_desc.write("#marker\tcontig\thas_pos_maps\n")
        for pos in unmapped_records:
            self._output_desc.write("\t".join([str(a) for a in pos])+"\n")
            
        sys.stderr.write("\tunmapped printed.\n")
        if self._verbose: sys.stderr.write("\tUnmapped records: "+str(len(unmapped_records))+"\n")
        
        return
    
    # OutputPrinter base methods
    def print_unaligned(self, mapping_results, map_config):
        
        map_name = map_config.get_name()
        map_as_physical = map_config.as_physical()
        
        sys.stderr.write("OutputFacade: creating output for unaligned of "+str(map_name)+" map\n")
        
        ########### UNALIGNED
        map_title = UNALIGNED_TITLE
        self._print_map_header(map_name, map_title)
        
        unaligned_records = mapping_results#.get_unaligned()
        self._output_unaligned(unaligned_records)
        
        return
    
    def _output_unaligned(self, unaligned_records):
        sys.stderr.write("\tprinting unaligned...\n")
        
        #self._output_desc.write("##"+section_name+"\n")
        if self._show_headers:
            self._output_desc.write("#marker\n")
        for pos in unaligned_records:
            self._output_desc.write(str(pos)+"\n")
        
        sys.stderr.write("\tunaligned printed.\n")
        if self._verbose: sys.stderr.write("Unaligned records: "+str(len(unaligned_records))+"\n")
        
        return
    
    ## OUTPUT FOR BASIC MAP FIELDS
    def output_base_header(self, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param):
        
        current_row = []
        
        if map_as_physical:
            current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_ID])
            current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_CHR])
            current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_START_POS])
            current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_END_POS])
            current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_STRAND])
            
            if multiple_param:
                current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_MULTIPLE_POS])
            
            current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_OTHER_ALIGNMENTS])
            
        else:
            current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MARKER_NAME_POS])
            current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MARKER_CHR_POS])
            if map_has_cm_pos:
                current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MARKER_CM_POS])
            
            if map_has_bp_pos:
                current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MARKER_BP_POS])
            
            if multiple_param:
                current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MULTIPLE_POS])
            
            current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.OTHER_ALIGNMENTS])
        
        return current_row
    
    def output_base_pos(self, pos, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param):
        
        current_row = []
        
        ## Marker ID
        current_row.append(str(pos.get_marker_id())) #[MapFields.MARKER_NAME_POS]))
        
        ## Chromosome
        chrom = pos.get_chrom_name() #[MapFields.MARKER_CHR_POS]
        current_row.append(str(chrom))
        
        # Physical map
        if map_as_physical:
            current_row.append(pos.get_bp_pos())
            current_row.append(pos.get_bp_end_pos())
            current_row.append(pos.get_strand())
            
        else:
            ## cM
            if map_has_cm_pos:
                cm = pos.get_cm_pos() #[MapFields.MARKER_CM_POS]
                if cm != "-":
                    if self._beauty_nums:
                        current_row.append(str("%0.2f" % float(cm)))
                    else:
                        current_row.append(cm)
                else:
                    current_row.append(cm)
            
            ## bp
            if map_has_bp_pos:
                bp = pos.get_bp_pos() #[MapFields.MARKER_BP_POS]
                current_row.append(str(bp))
        
        if pos.is_empty():
            if multiple_param:
                current_row.append("-") # multiple positions
            current_row.append("-") # other alignments
        else:
            ## Multiple
            if multiple_param:
                mult = pos.has_multiple_pos() #[MapFields.MULTIPLE_POS]
                if mult: current_row.append("Yes")
                else: current_row.append("No")
                
            ## Other alignments
            if pos.has_other_alignments(): current_row.append("Yes")
            else: current_row.append("No")
        
        return current_row
    
## A printer to show MappingResults to the left
## and FeatureMappings (genes, markers, ) to the right
class ExpandedPrinter(OutputPrinter):
    
    def output_features_header(self, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param, load_annot = False, annotator = None):
        
        headers_row = ["Row_type"]
        base_headers_row = self.output_base_header(map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
        headers_row.extend(base_headers_row)
        
        headers_row.append(MapHeaders.FEATURE_HEADERS[GenesFields.GENES_ID_POS])
        #headers_row.append(MapHeaders.FEATURE_HEADERS[GenesFields.GENES_TYPE_POS])
        headers_row.append(MapHeaders.FEATURE_HEADERS[GenesFields.GENES_DATASET_NAME_POS])
        headers_row.append(MapHeaders.FEATURE_HEADERS[GenesFields.GENES_CHR_POS])
        
        if map_as_physical:
            headers_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_START_POS])
            headers_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_END_POS])
        else:
            if map_has_cm_pos:
                headers_row.append(MapHeaders.FEATURE_HEADERS[GenesFields.GENES_CM_POS])
            
            if map_has_bp_pos:
                headers_row.append(MapHeaders.FEATURE_HEADERS[GenesFields.GENES_BP_POS])
        
        if load_annot:
            anntypes_config = annotator.get_anntypes_config()
            anntypes_list = anntypes_config.get_anntypes_list()
            loaded_anntypes = annotator.get_loaded_anntypes()
            
            for anntype_id in anntypes_list:
                if anntype_id in loaded_anntypes:
                    anntype = anntypes_config.get_anntype(anntype_id)
                    headers_row.append(anntype.get_name())
        
        return headers_row
    
    def output_features_pos(self, pos, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param,
                            load_annot = False, annotator = None):
        
        #current_row = []
        feature = pos.get_feature()
        current_row = [feature.get_row_type()]
        base_row = self.output_base_pos(pos, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
        current_row.extend(base_row)
        
        feature_data = []
        
        feature_data.append(feature.get_feature_id())
        #feature_data.append(feature.get_feature_type())
        feature_data.append(feature.get_dataset_name())
        feature_data.append(feature.get_chrom_name())
        
        if map_as_physical:
            feature_data.append(str(feature.get_bp_pos()))
            feature_data.append(str(feature.get_bp_end_pos()))
        else:
            if map_has_cm_pos:
                feature_cm = feature.get_cm_pos()
                if feature_cm != "-":
                    if self._beauty_nums:
                        cm_pos = str("%0.2f" % float(feature_cm))
                    else:
                        cm_pos = feature_cm
                else:
                    cm_pos = feature_cm
                feature_data.append(cm_pos)
                
            if map_has_bp_pos:
                feature_data.append(str(feature.get_bp_pos()))
            
        if load_annot:
            gene_annots = feature.get_annots()
            
            anntypes_list = annotator.get_anntypes_config().get_anntypes_list()
            loaded_anntypes = annotator.get_loaded_anntypes()
            
            # This is read like this to keep the same order of annotation types
            # in all the records so that they can share column (and header title)
            for anntype_id in [anntype_id for anntype_id in anntypes_list if anntype_id in loaded_anntypes]:
                    
                    # load gene_annots only of that anntype
                    gene_annots_anntype = [gene_annot for gene_annot in gene_annots if gene_annot.get_anntype().get_anntype_id()==anntype_id]
                    if len(gene_annots_anntype)>0:
                        for gene_annot_anntype in gene_annots_anntype:
                            data_line = ",".join(gene_annot_anntype.get_annot_data())
                            feature_data.append(data_line)
                    else:
                        feature_data.append("-")
        
        current_row.extend(feature_data)
        
        return current_row

## A printer to show MappingResults and FeatureMappings (markers, genes,)
## in rows at the same level
class CollapsedPrinter(OutputPrinter):
    def output_features_header(self, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param, load_annot = False, annotator = None):
        
        headers_row = ["Row_type"]
        base_headers_row = self.output_base_header(map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
        headers_row.extend(base_headers_row)
        
        #sys.stderr.write("CollapsedViewPrinter: "+str(load_annot)+" - "+str(annotator)+"\n")
        
        if load_annot:
            anntypes_config = annotator.get_anntypes_config()
            anntypes_list = anntypes_config.get_anntypes_list()
            loaded_anntypes = annotator.get_loaded_anntypes()
            
            sys.stderr.write("\tanntypes_list: "+str(anntypes_list)+"\n")
            sys.stderr.write("\tloaded_anntypes: "+str(loaded_anntypes)+"\n")
            
            for anntype_id in anntypes_list:
                if anntype_id in loaded_anntypes:
                    anntype = anntypes_config.get_anntype(anntype_id)
                    headers_row.append(anntype.get_name())
        
        #sys.stderr.write("\theaders_row: "+str(headers_row)+"\n")
        
        return headers_row
    
    def output_features_pos(self, pos, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param,
                            load_annot = False, annotator = None):
        
        #sys.stderr.write("CollapsedViewPrinter: "+str(load_annot)+" - "+str(annotator)+"\n")
        
        current_row = [pos.get_row_type()]
        base_row = self.output_base_pos(pos, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
        current_row.extend(base_row)
        feature_data = []
        
        feature_type = pos.get_feature_type()
        
        if load_annot and feature_type == DatasetsConfig.DATASET_TYPE_GENE:
            gene_annots = pos.get_annots()
            
            anntypes_list = annotator.get_anntypes_config().get_anntypes_list()
            loaded_anntypes = annotator.get_loaded_anntypes()
            
            # This is read like this to keep the same order of annotation types
            # in all the records so that they can share column (and header title)
            for anntype_id in [anntype_id for anntype_id in anntypes_list if anntype_id in loaded_anntypes]:
                    
                    # load gene_annots only of that anntype
                    gene_annots_anntype = [gene_annot for gene_annot in gene_annots if gene_annot.get_anntype().get_anntype_id()==anntype_id]
                    if len(gene_annots_anntype)>0:
                        for gene_annot_anntype in gene_annots_anntype:
                            data_line = ",".join(gene_annot_anntype.get_annot_data())
                            feature_data.append(data_line)
                    else:
                        feature_data.append("-")
        
        #sys.stderr.write("\tfeature_data: "+str(feature_data)+"\n")
        
        current_row.extend(feature_data)
        
        return current_row

## END
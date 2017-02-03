#!/usr/bin/env python
# -*- coding: utf-8 -*-

# OutputFacade.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys

from barleymapcore.maps.MapsBase import MapTypes

MAPPED_TITLE = "Map"
UNMAPPED_TITLE = "Alignments without map position"
UNALIGNED_TITLE = "Unaligned markers"
MAP_WITH_GENES_TITLE = "Map with genes"
MAP_WITH_MARKERS_TITLE = "Map with markers"

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
    GENES_MAP_POS = 2
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
    
    _output_desc = None
    _verbose = False
    _beauty_nums = False
    
    def __init__(self):        
        return
    
    def get_plain_printer(self, output_desc, verbose = False, beauty_nums = False):
        self._output_desc = output_desc
        self._verbose = verbose
        self._beauty_nums = beauty_nums
        
        return self
    
    def print_maps(self, maps_dict, show_genes, show_markers, show_unmapped, multiple_param_text, load_annot, show_headers = True):
        
        for map_id in maps_dict:
            mapping_results = maps_dict[map_id]
            map_config = mapping_results.get_map_config()
            map_name = map_config.get_name()
            map_is_physical = map_config.as_physical()
            map_sort_by = mapping_results.get_sort_by()
            
            sys.stderr.write("OutputFacade: creating output for map "+str(map_name)+"\n")
            
            map_has_cm_pos = map_config.has_cm_pos()
            map_has_bp_pos = map_config.has_bp_pos()
            
            if not (show_genes or show_markers):
                ########## OUTPUT FOR ONLY MAP
                
                map_title = MAPPED_TITLE
                self.print_genetic_map_header(map_name, show_unmapped, map_title)
                
                sorted_positions = mapping_results.get_mapped()
                
                self.print_genetic_map(sorted_positions, map_is_physical, map_has_cm_pos, map_has_bp_pos, \
                                                multiple_param_text, show_headers)
            
            elif show_genes:
                ########## OUTPUT FOR MAP WITH GENES IF REQUESTED
                
                map_title = MAP_WITH_GENES_TITLE
                self.print_genetic_map_header(map_name, show_unmapped, map_title)
                
                genes_enriched_positions = mapping_results.get_map_with_genes()
                
                self.print_map_with_genes(genes_enriched_positions, map_sort_by, map_is_physical, map_has_cm_pos, map_has_bp_pos, \
                                                   multiple_param_text, load_annot, show_headers)
            
            elif show_markers:
                ########### OUTPUT FOR MAP WITH MARKERS
                
                map_title = MAP_WITH_MARKERS_TITLE
                self.print_genetic_map_header(map_name, show_unmapped, map_title)
                
                marker_enriched_positions = mapping_results.get_map_with_markers()
                
                self.print_map_with_markers(marker_enriched_positions, map_sort_by, map_is_physical, map_has_cm_pos, map_has_bp_pos, \
                                                     multiple_param_text, show_headers)
                
            # else: this could never happen!?
            
            if show_unmapped:
                # physical maps do not have anchored contigs, and thus contigs
                # never lack map position
                if not map_is_physical:
                    ############ UNMAPPED
                    map_title = UNMAPPED_TITLE
                    unmapped_records = mapping_results.get_unmapped()
                    
                    if unmapped_records != None: # those obtained from mapping results have no unmapped records
                        self.output_unmapped(map_title, unmapped_records, show_headers)
                
                ########### UNALIGNED
                map_title = UNALIGNED_TITLE
                unaligned_records = mapping_results.get_unaligned()
                
                self.output_unaligned(map_title, unaligned_records, show_headers)
        
        ######
    
    def print_genetic_map_header(self, map_name, show_unmapped = False, map_title = ""):
        
        self._output_desc.write(">"+map_name+"\n")
        if show_unmapped: self._output_desc.write("##"+map_title+"\n")
        
        return
    
    ## OUTPUT FOR BASIC MAP FIELDS
    def __output_base_pos(self, current_row, pos, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param):
        
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
            current_row.append("-") # multiple positions
            current_row.append("-") # other alignments
        else:
            ## Multiple
            if multiple_param == "yes":
                mult = pos.has_multiple_pos() #[MapFields.MULTIPLE_POS]
                if mult: current_row.append("Yes")
                else: current_row.append("No")
                
            ## Other alignments
            if pos.has_other_alignments(): current_row.append("Yes")
            else: current_row.append("No")
        
        return
    
    def __output_base_header(self, current_row, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param):
        
        if map_as_physical:
            current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_ID])
            current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_CHR])
            current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_START_POS])
            current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_END_POS])
            current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_STRAND])
            
            if multiple_param == "yes":
                current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_MULTIPLE_POS])
            
            current_row.append(MapHeaders.PHYSICAL_HEADERS[MapHeaders.PHYSICAL_OTHER_ALIGNMENTS])
            
        else:
            current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MARKER_NAME_POS])
            current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MARKER_CHR_POS])
            if map_has_cm_pos:
                current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MARKER_CM_POS])
            
            if map_has_bp_pos:
                current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MARKER_BP_POS])
            
            if multiple_param == "yes":
                current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MULTIPLE_POS])
            
            current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.OTHER_ALIGNMENTS])
        
        return
    
    def print_genetic_map(self, positions, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param, show_headers = False):
        
        sys.stderr.write("\tprinting plain genetic map...\n")
        
        if show_headers:
            headers_row = []
            self.__output_base_header(headers_row, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            self._output_desc.write("#"+"\t".join(headers_row)+"\n")
        
        for pos in positions:
            current_row = []
            self.__output_base_pos(current_row, pos, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            self._output_desc.write("\t".join([str(x) for x in current_row])+"\n")
        
        sys.stderr.write("\tgenetic maps printed.\n")
        
        if self._verbose: sys.stderr.write("\tlines printed "+str(len(positions))+"\n")
        
        return
    
    def __output_features_header(self, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param):
        headers_row = []
        self.__output_base_header(headers_row, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
        
        headers_row.append(MapHeaders.FEATURE_HEADERS[GenesFields.GENES_ID_POS])
        headers_row.append(MapHeaders.FEATURE_HEADERS[GenesFields.GENES_TYPE_POS])
        headers_row.append(MapHeaders.FEATURE_HEADERS[GenesFields.GENES_CHR_POS])
        
        if map_has_cm_pos:
            headers_row.append(MapHeaders.FEATURE_HEADERS[GenesFields.GENES_CM_POS])
        
        if map_has_bp_pos:
            headers_row.append(MapHeaders.FEATURE_HEADERS[GenesFields.GENES_BP_POS])
        
        return headers_row
    
    def __output_features_pos(self, pos, map_has_cm_pos, map_has_bp_pos, map_sort_by):
        feature_data = []
        
        feature_data = []
        feature = pos.get_feature()
        feature_data.append(feature.get_feature_id())
        feature_data.append(feature.get_feature_type())
        feature_data.append(feature.get_dataset_name())
        feature_data.append(feature.get_chrom_name())
        
        if map_has_cm_pos and map_has_bp_pos:
            if map_sort_by == MapTypes.MAP_SORT_PARAM_CM:
                feature_cm = feature.get_pos()
                if feature_cm != "-":
                    if self._beauty_nums:
                        cm_pos = str("%0.2f" % float(feature_cm))
                    else:
                        cm_pos = feature_cm
                else:
                    cm_pos = feature_cm
                feature_data.append(cm_pos)
            elif map_sort_by == MapTypes.MAP_SORT_PARAM_BP:
                feature_data.append(str(feature.get_pos()))
            else:
                raise m2pException("Unrecognized sort by "+map_sort_by+".")
        
        elif map_has_cm_pos:
            feature_cm = feature.get_pos()
            if feature_cm != "-":
                if self._beauty_nums:
                    cm_pos = str("%0.2f" % float(feature_cm))
                else:
                    cm_pos = feature_cm
            else:
                cm_pos = feature_cm
            feature_data.append(cm_pos)
            
        elif map_has_bp_pos:
            feature_data.append(str(feature.get_pos()))
        else:
            raise m2pException("Map configuration indicates that has no cm nor bp positions.")
        
        return feature_data
    
    def print_map_with_genes(self, positions, map_sort_by, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param, load_annot, show_headers = False):
        
        sys.stderr.write("\tprinting map with genes...\n")
        
        if show_headers:
            
            headers_row = self.__output_features_header(map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            if load_annot:
                headers_row.append(MapHeaders.ANNOT_HEADERS[AnnotFields.GENES_ANNOT_DESC])
                headers_row.append(MapHeaders.ANNOT_HEADERS[AnnotFields.GENES_ANNOT_INTERPRO])
                headers_row.append(MapHeaders.ANNOT_HEADERS[AnnotFields.GENES_ANNOT_PFAM])
                headers_row.append(MapHeaders.ANNOT_HEADERS[AnnotFields.GENES_ANNOT_GO])
            
            self._output_desc.write("#"+"\t".join(headers_row)+"\n")
        
        for pos in positions:
            current_row = []
            self.__output_base_pos(current_row, pos, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            feature_data = self.__output_features_pos(pos, map_has_cm_pos, map_has_bp_pos, map_sort_by)
            
            current_row.extend(feature_data)
            
            #if load_annot:
            #    annot = gene[len(MapHeaders.FEATURE_HEADERS):]
            #    current_row.append(annot[AnnotFields.GENES_ANNOT_DESC]) # Readable description
            #    # InterPro
            #    current_row.append(annot[AnnotFields.GENES_ANNOT_INTERPRO])
            #    current_row.append(annot[AnnotFields.GENES_ANNOT_PFAM]) # PFAM ID
            #    #output_buffer.append("<td>"+x[7]+"</td>") # PFAM source
            #    current_row.append(annot[AnnotFields.GENES_ANNOT_GO]) # GO terms
            
            self._output_desc.write("\t".join([str(x) for x in current_row])+"\n")
            
        sys.stderr.write("OutputFacade: map with genes printed.\n")
        
        if self._verbose: sys.stderr.write("\tlines printed "+str(len(positions))+"\n")
        
        return
    
    def print_map_with_markers(self, positions, map_sort_by, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param, show_headers = False):
        
        sys.stderr.write("\tprinting map with markers...\n")
        
        if show_headers:
            
            headers_row = self.__output_features_header(map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            self._output_desc.write("#"+"\t".join(headers_row)+"\n")
        
        for pos in positions:
            current_row = []
            self.__output_base_pos(current_row, pos, map_as_physical, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            feature_data = self.__output_features_pos(pos, map_has_cm_pos, map_has_bp_pos, map_sort_by)
            
            current_row.extend(feature_data)
            
            self._output_desc.write("\t".join([str(x) for x in current_row])+"\n")
            
        sys.stderr.write("OutputFacade: map with markers printed.\n")
        
        if self._verbose: sys.stderr.write("\tlines printed "+str(len(positions))+"\n")
        
        return
    
        #def print_map_with_genes(self, positions, map_has_cm_pos, map_has_bp_pos, multiple_param, load_annot, show_headers = False):
    #    
    #    sys.stderr.write("\tprinting map with genes...\n")
    #    
    #    if show_headers:
    #        headers_row = []
    #        self.__output_base_header(headers_row, map_has_cm_pos, map_has_bp_pos, multiple_param)
    #        
    #        headers_row.append(MapHeaders.GENES_HEADERS[GenesFields.GENES_ID_POS])
    #        headers_row.append(MapHeaders.GENES_HEADERS[GenesFields.GENES_TYPE_POS])
    #        headers_row.append(MapHeaders.GENES_HEADERS[GenesFields.GENES_CHR_POS])
    #        
    #        if map_has_cm_pos:
    #            headers_row.append(MapHeaders.GENES_HEADERS[GenesFields.GENES_CM_POS])
    #        
    #        if map_has_bp_pos:
    #            headers_row.append(MapHeaders.GENES_HEADERS[GenesFields.GENES_BP_POS])
    #            
    #        if load_annot:
    #            headers_row.append(MapHeaders.ANNOT_HEADERS[AnnotFields.GENES_ANNOT_DESC])
    #            headers_row.append(MapHeaders.ANNOT_HEADERS[AnnotFields.GENES_ANNOT_INTERPRO])
    #            headers_row.append(MapHeaders.ANNOT_HEADERS[AnnotFields.GENES_ANNOT_PFAM])
    #            headers_row.append(MapHeaders.ANNOT_HEADERS[AnnotFields.GENES_ANNOT_GO])
    #        
    #        self._output_desc.write("#"+"\t".join(headers_row)+"\n")
    #    
    #    for pos in positions:
    #        current_row = []
    #        self.__output_base_pos(current_row, pos, map_has_cm_pos, map_has_bp_pos, multiple_param)
    #        
    #        gene = pos[MapPosition.MAP_FIELDS:]
    #        
    #        gene_cm = gene[GenesFields.GENES_CM_POS]
    #        if gene_cm != "-":
    #            if self._beauty_nums:
    #                cm_pos = str("%0.2f" % float(gene_cm))
    #            else:
    #                cm_pos = gene_cm
    #        else:
    #            cm_pos = gene_cm
    #        
    #        gene_data = []
    #        gene_data.append(gene[GenesFields.GENES_ID_POS])
    #        gene_data.append(gene[GenesFields.GENES_TYPE_POS])
    #        gene_data.append(str(gene[GenesFields.GENES_CHR_POS]))
    #        
    #        if map_has_cm_pos:
    #            gene_data.append(cm_pos)
    #        
    #        if map_has_bp_pos:
    #            gene_data.append(str(gene[GenesFields.GENES_BP_POS]))
    #        
    #        current_row.extend(gene_data)
    #        
    #        if load_annot:
    #            annot = gene[len(MapHeaders.GENES_HEADERS):]
    #            current_row.append(annot[AnnotFields.GENES_ANNOT_DESC]) # Readable description
    #            # InterPro
    #            current_row.append(annot[AnnotFields.GENES_ANNOT_INTERPRO])
    #            current_row.append(annot[AnnotFields.GENES_ANNOT_PFAM]) # PFAM ID
    #            #output_buffer.append("<td>"+x[7]+"</td>") # PFAM source
    #            current_row.append(annot[AnnotFields.GENES_ANNOT_GO]) # GO terms
    #        
    #        self._output_desc.write("\t".join([str(x) for x in current_row])+"\n")
    #        
    #    sys.stderr.write("\tmap with genes printed.\n")
    #    
    #    if self._verbose: sys.stderr.write("\tlines printed "+str(len(positions))+"\n")
    #    
    #    return
    
    def output_unmapped(self, section_name, unmapped_records, show_headers = False):
        sys.stderr.write("\tprinting unmapped...\n")
        
        self._output_desc.write("##"+section_name+"\n")
        if show_headers:
            self._output_desc.write("#marker\tcontig\thas_pos_maps\n")
        for pos in unmapped_records:
            self._output_desc.write("\t".join([str(a) for a in pos])+"\n")
            
        sys.stderr.write("\tunmapped printed.\n")
        if self._verbose: sys.stderr.write("\tUnmapped records: "+str(len(unmapped_records))+"\n")
        
        return
    
    def output_unaligned(self, section_name, unaligned_records, show_headers = False):
        sys.stderr.write("\tprinting unaligned...\n")
        
        self._output_desc.write("##"+section_name+"\n")
        if show_headers:
            self._output_desc.write("#marker\n")
        for pos in unaligned_records:
            self._output_desc.write(str(pos)+"\n")
        
        sys.stderr.write("\tunaligned printed.\n")
        if self._verbose: sys.stderr.write("Unaligned records: "+str(len(unaligned_records))+"\n")
        
        return
    
## END
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# OutputFacade.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys

from barleymapcore.db.MapsConfig import MapsConfig
from barleymapcore.maps.MapsBase import MapHeaders, MapPosition, MapTypes
from barleymapcore.genes.GenesBase import GenesFields, AnnotFields
from barleymapcore.maps.MarkersBase import MarkersFields

MAPPED_TITLE = "Map"
UNMAPPED_TITLE = "Alignments without map position"
UNALIGNED_TITLE = "Unaligned markers"
MAP_WITH_GENES_TITLE = "Map with genes"
MAP_WITH_MARKERS_TITLE = "Map with markers"

class OutputFacade(object):
    
    _output_desc = None
    _verbose = False
    
    def __init__(self):        
        return
    
    def get_plain_printer(self, output_desc, verbose = False):
        self._output_desc = output_desc
        self._verbose = verbose
        
        return self
    
    def print_maps(self, maps_dict, show_genes, show_markers, show_unmapped, multiple_param_text, load_annot, show_headers = True):
        
        for map_id in maps_dict:
            mapping_results = maps_dict[map_id]
            map_config = mapping_results.get_map_config() #[MapTypes.MAP_CONFIG]
            map_name = map_config.get_name()
            map_is_physical = map_config.as_physical()
            map_sort_by = mapping_results.get_sort_by()
            
            sys.stderr.write("OutputFacade: creating output for map "+str(map_name)+"\n")
            
            map_has_cm_pos = map_config.has_cm_pos()
            map_has_bp_pos = map_config.has_bp_pos()
            
            if not (show_genes or show_markers):
                ########## OUTPUT FOR ONLY MAP
                
                map_title = MAPPED_TITLE #MapTypes.RESULTS_DICT[MapTypes.MAP_MAPPED]
                self.print_genetic_map_header(map_name, show_unmapped, map_title)
                
                sorted_positions = mapping_results.get_mapped()
                
                self.print_genetic_map(sorted_positions, map_has_cm_pos, map_has_bp_pos, \
                                                multiple_param_text, show_headers)
            
            elif show_genes:
                ########## OUTPUT FOR MAP WITH GENES IF REQUESTED
                
                map_title = MAP_WITH_GENES_TITLE #MapTypes.RESULTS_DICT[MapTypes.MAP_WITH_GENES]
                self.print_genetic_map_header(map_name, show_unmapped, map_title)
                
                genes_enriched_positions = mapping_results.get_map_with_genes()
                
                self.print_map_with_genes(genes_enriched_positions, map_has_cm_pos, map_has_bp_pos, \
                                                   multiple_param_text, load_annot, show_headers)
            
            elif show_markers:
                ########### OUTPUT FOR MAP WITH MARKERS
                
                map_title = MAP_WITH_MARKERS_TITLE #MapTypes.RESULTS_DICT[MapTypes.MAP_WITH_MARKERS]
                self.print_genetic_map_header(map_name, show_unmapped, map_title)
                
                marker_enriched_positions = mapping_results.get_map_with_markers()
                
                self.print_map_with_markers(marker_enriched_positions, map_sort_by, map_has_cm_pos, map_has_bp_pos, \
                                                     multiple_param_text, show_headers)
                
            # else: this could never happen!?
            
            if show_unmapped:
                # physical maps do not have anchored contigs, and thus contigs
                # never lack map position
                if not map_is_physical:
                    ############ UNMAPPED
                    map_title = UNMAPPED_TITLE #MapTypes.RESULTS_DICT[MapTypes.MAP_UNMAPPED]
                    unmapped_records = mapping_results.get_unmapped()
                    
                    self.output_unmapped(map_title, unmapped_records, show_headers)
                
                ########### UNALIGNED
                map_title = UNALIGNED_TITLE #MapTypes.RESULTS_DICT[MapTypes.MAP_UNALIGNED]
                unaligned_records = mapping_results.get_unaligned()
                
                self.output_unaligned(map_title, unaligned_records, show_headers)
        
        ######
    
    def print_genetic_map_header(self, map_name, show_unmapped = False, map_title = ""):
        
        self._output_desc.write(">"+map_name+"\n")
        if show_unmapped: self._output_desc.write("##"+map_title+"\n")
        
        return
    
    ## OUTPUT FOR BASIC MAP FIELDS
    def __output_base_pos(self, current_row, pos, map_has_cm_pos, map_has_bp_pos, multiple_param):
        
        ## Marker ID
        current_row.append(str(pos.get_marker_id())) #[MapFields.MARKER_NAME_POS]))
        
        ## Chromosome
        chrom = pos.get_chrom_name() #[MapFields.MARKER_CHR_POS]
        current_row.append(str(chrom))
        
        ## cM
        if map_has_cm_pos:
            cm = pos.get_cm_pos() #[MapFields.MARKER_CM_POS]
            if cm != "-": current_row.append(str("%0.2f" % float(cm)))
            else: current_row.append(cm)
        
        ## bp
        if map_has_bp_pos:
            bp = pos.get_bp_pos() #[MapFields.MARKER_BP_POS]
            current_row.append(str(bp))
        
        ## Multiple
        if multiple_param == "yes":
            mult = pos.has_multiple_pos() #[MapFields.MULTIPLE_POS]
            if mult: current_row.append("Yes")
            else: current_row.append("No")
        
        ## Other alignments
        if pos.has_other_alignments(): current_row.append("Yes")
        else: current_row.append("No")
        
        return
    
    def __output_base_header(self, current_row, map_has_cm_pos, map_has_bp_pos, multiple_param):
        
        current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MARKER_NAME_POS])
        current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MARKER_CHR_POS])
        
        if map_has_cm_pos:
            current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MARKER_CM_POS])
        
        if map_has_bp_pos:
            current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MARKER_BP_POS])
        
        if multiple_param == "yes":
            current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.MULTIPLE_POS])
        
        current_row.append(MapHeaders.OUTPUT_HEADERS[MapHeaders.OTHER_ALIGNMENTS_POS])
        
        return
    
    def print_genetic_map(self, positions, map_has_cm_pos, map_has_bp_pos, multiple_param, show_headers = False):
        
        sys.stderr.write("\tprinting plain genetic map...\n")
        
        if show_headers:
            headers_row = []
            self.__output_base_header(headers_row, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            self._output_desc.write("#"+"\t".join(headers_row)+"\n")
        
        for pos in positions:
            current_row = []
            self.__output_base_pos(current_row, pos, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            self._output_desc.write("\t".join(current_row)+"\n")
        
        sys.stderr.write("\tgenetic maps printed.\n")
        
        if self._verbose: sys.stderr.write("\tlines printed "+str(len(positions))+"\n")
        
        return
    
    def print_map_with_genes(self, positions, map_has_cm_pos, map_has_bp_pos, multiple_param, load_annot, show_headers = False):
        
        sys.stderr.write("\tprinting map with genes...\n")
        
        if show_headers:
            headers_row = []
            self.__output_base_header(headers_row, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            headers_row.append(MapHeaders.GENES_HEADERS[GenesFields.GENES_ID_POS])
            headers_row.append(MapHeaders.GENES_HEADERS[GenesFields.GENES_TYPE_POS])
            headers_row.append(MapHeaders.GENES_HEADERS[GenesFields.GENES_CHR_POS])
            
            if map_has_cm_pos:
                headers_row.append(MapHeaders.GENES_HEADERS[GenesFields.GENES_CM_POS])
            
            if map_has_bp_pos:
                headers_row.append(MapHeaders.GENES_HEADERS[GenesFields.GENES_BP_POS])
                
            if load_annot:
                headers_row.append(MapHeaders.ANNOT_HEADERS[AnnotFields.GENES_ANNOT_DESC])
                headers_row.append(MapHeaders.ANNOT_HEADERS[AnnotFields.GENES_ANNOT_INTERPRO])
                headers_row.append(MapHeaders.ANNOT_HEADERS[AnnotFields.GENES_ANNOT_PFAM])
                headers_row.append(MapHeaders.ANNOT_HEADERS[AnnotFields.GENES_ANNOT_GO])
            
            self._output_desc.write("#"+"\t".join(headers_row)+"\n")
        
        for pos in positions:
            current_row = []
            self.__output_base_pos(current_row, pos, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            gene = pos[MapPosition.MAP_FIELDS:]
            
            gene_cm = gene[GenesFields.GENES_CM_POS]
            if gene_cm != "-":
                cm_pos = str("%0.2f" % float(gene_cm))
            else:
                cm_pos = gene_cm
            
            gene_data = []
            gene_data.append(gene[GenesFields.GENES_ID_POS])
            gene_data.append(gene[GenesFields.GENES_TYPE_POS])
            gene_data.append(str(gene[GenesFields.GENES_CHR_POS]))
            
            if map_has_cm_pos:
                gene_data.append(cm_pos)
            
            if map_has_bp_pos:
                gene_data.append(str(gene[GenesFields.GENES_BP_POS]))
            
            current_row.extend(gene_data)
            
            if load_annot:
                annot = gene[len(MapHeaders.GENES_HEADERS):]
                current_row.append(annot[AnnotFields.GENES_ANNOT_DESC]) # Readable description
                # InterPro
                current_row.append(annot[AnnotFields.GENES_ANNOT_INTERPRO])
                current_row.append(annot[AnnotFields.GENES_ANNOT_PFAM]) # PFAM ID
                #output_buffer.append("<td>"+x[7]+"</td>") # PFAM source
                current_row.append(annot[AnnotFields.GENES_ANNOT_GO]) # GO terms
            
            self._output_desc.write("\t".join(current_row)+"\n")
            
        sys.stderr.write("\tmap with genes printed.\n")
        
        if self._verbose: sys.stderr.write("\tlines printed "+str(len(positions))+"\n")
        
        return
    
    def print_map_with_markers(self, positions, map_sort_by, map_has_cm_pos, map_has_bp_pos, multiple_param, show_headers = False):
        
        sys.stderr.write("\tprinting map with markers...\n")
        
        if show_headers:
            headers_row = []
            self.__output_base_header(headers_row, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            headers_row.append(MapHeaders.MARKERS_HEADERS[MarkersFields.MARKER_ID_POS])
            headers_row.append(MapHeaders.MARKERS_HEADERS[MarkersFields.MARKER_DATASET_POS])
            headers_row.append(MapHeaders.MARKERS_HEADERS[MarkersFields.MARKER_CHR_POS])
            if map_has_cm_pos:
                headers_row.append(MapHeaders.MARKERS_HEADERS[MarkersFields.MARKER_CM_POS])
            if map_has_bp_pos:
                headers_row.append(MapHeaders.MARKERS_HEADERS[MarkersFields.MARKER_BP_POS])
            
            #headers_row.append(MapHeaders.MARKERS_HEADERS[MarkersFields.MARKER_GENES_POS])
            
            self._output_desc.write("#"+"\t".join(headers_row)+"\n")
        
        for pos in positions:
            current_row = []
            self.__output_base_pos(current_row, pos, map_has_cm_pos, map_has_bp_pos, multiple_param)
            
            marker_data = []
            marker = pos.get_feature()
            marker_data.append(marker.get_marker_id())
            marker_data.append(marker.get_dataset_name())
            marker_data.append(marker.get_chrom_name())
            
            if map_has_cm_pos and map_has_bp_pos:
                if map_sort_by == MapTypes.MAP_SORT_PARAM_CM:
                    marker_cm = marker.get_pos() #marker[MarkersFields.MARKER_CM_POS]
                    if marker_cm != "-":
                        cm_pos = str("%0.2f" % float(marker_cm))
                    else:
                        cm_pos = marker_cm
                    marker_data.append(cm_pos)
                elif map_sort_by == MapTypes.MAP_SORT_PARAM_BP:
                    marker_data.append(str(marker.get_pos()))
                else:
                    raise m2pException("Unrecognized sort by "+map_sort_by+".")
            
            elif map_has_cm_pos:
                marker_cm = marker.get_pos() #marker[MarkersFields.MARKER_CM_POS]
                if marker_cm != "-":
                    cm_pos = str("%0.2f" % float(marker_cm))
                else:
                    cm_pos = marker_cm
                marker_data.append(cm_pos)
                
            elif map_has_bp_pos:
                marker_data.append(str(marker.get_pos()))
            else:
                raise m2pException("Map configuration indicates that has no cm nor bp positions.")
            
            #if marker[MarkersFields.MARKER_GENES_CONFIGURED_POS]:
            #    if len(marker[MarkersFields.MARKER_GENES_POS]) > 0:
            #        marker_data.append(",".join(marker[MarkersFields.MARKER_GENES_POS]))
            #    else:
            #        marker_data.append("no hits")
            #else:
            #    marker_data.append("nd")
            
            current_row.extend(marker_data)
            
            self._output_desc.write("\t".join(current_row)+"\n")
            
        sys.stderr.write("OutputFacade: map with markers printed.\n")
        
        if self._verbose: sys.stderr.write("\tlines printed "+str(len(positions))+"\n")
        
        return
    
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
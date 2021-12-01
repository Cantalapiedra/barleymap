#!/usr/bin/env python
# -*- coding: utf-8 -*-

# MappingsParser.py is part of Barleymap.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys, os
import cPickle

from barleymapcore.maps.MappingResults import MappingResult
from barleymapcore.maps.MapInterval import MapInterval
from barleymapcore.maps.enrichment.FeatureMapping import FeaturesFactory

from MapFiles import MapFile

### Class to obtain mapping results from pre-calculated datasets
### "mapping results" are those which have already map positions
### like those resulting from running bmap_align to a map
class MappingsParser(object):
    
    def parse_mapping_file(self, data_path, map_config, chrom_dict):
        mapping_results_list = []
        
        map_name = map_config.get_name()
        map_has_cm_pos = map_config.has_cm_pos()
        map_has_bp_pos = map_config.has_bp_pos()
        map_is_physical = map_config.as_physical()
        
        for hit in open(data_path, 'r'):
            if hit.startswith(">") or hit.startswith("#"): continue
            hit_data = hit.strip().split("\t")
            
            mapping_result = MappingResult.init_from_data(hit_data, map_name, chrom_dict, map_is_physical, map_has_cm_pos, map_has_bp_pos)
            mapping_results_list.append(mapping_result)
        
        return mapping_results_list
    
    def _parse_mapping_file_by_id(self, query_ids_dict, data_path, map_config, chrom_dict,
                                        multiple_param, dataset_synonyms = {}, test_set = None):
        mapping_results_list = []
        
        map_name = map_config.get_name()
        map_has_cm_pos = map_config.has_cm_pos()
        map_has_bp_pos = map_config.has_bp_pos()
        map_is_physical = map_config.as_physical()
        
        for hit in open(data_path, 'r'):
            #sys.stderr.write(" ONE**************************\n")
            #sys.stderr.write(str(hit)+"\n")
            if hit.startswith(">") or hit.startswith("#"): continue
            hit_data = hit.strip().split("\t")
            
            #sys.stderr.write("data\n")
            
            if test_set:
                
                hit_query = hit_data[0]
                
                #if hit_query == "12_30924":
                #    sys.stderr.write(str(test_set)+"\n")
                    
                #sys.stderr.write("CHECK TESTSET\n")
                if hit_query in dataset_synonyms:
                    #if hit_query == "12_30924":
                    #    sys.stderr.write("IS IN SYNONYMS\n")
                    hit_synonyms = dataset_synonyms[hit_query]
                    synonyms_found = test_set.intersection(hit_synonyms)
                    
                    if len(synonyms_found) > 0:
                        #if hit_query == "12_30924":
                        #    sys.stderr.write("-".join(synonyms_found)+"\n")
                        mapping_result = MappingResult.init_from_data(hit_data, map_name, chrom_dict, map_is_physical,
                                                                      map_has_cm_pos, map_has_bp_pos)
                        
                        for synonym in synonyms_found: # all found
                            query_ids_dict[synonym] = 1
                        
                        if mapping_result.has_multiple_pos():
                            if multiple_param == False:
                                continue
                        else: # just for sake of readability
                            for synonym in synonyms_found: # all found
                                if synonym in test_set:
                                    test_set.remove(synonym)
                                
                        mapping_result.set_marker_id("|".join(synonyms_found))
                        mapping_results_list.append(mapping_result)
                else:
                    #if hit_query == "12_30924":
                    #    sys.stderr.write("IS NOT IN SYNONYMS\n")
                    if hit_query in test_set:
                        #sys.stderr.write("create mapping data\n")
                        mapping_result = MappingResult.init_from_data(hit_data, map_name, chrom_dict, map_is_physical, map_has_cm_pos, map_has_bp_pos)
                        
                        query_ids_dict[hit_query] = 1 # found
                        
                        #sys.stderr.write("append\n")
                        if mapping_result.has_multiple_pos():
                            if multiple_param == False:
                                continue
                        else: # just for sake of readability
                            test_set.remove(hit_query)
                            
                        mapping_results_list.append(mapping_result)
                        
            else: # retrieve all mapping results
                mapping_result = MappingResult.init_from_data(hit_data, map_name, chrom_dict, map_is_physical, map_has_cm_pos, map_has_bp_pos)
                
                query_ids_dict[hit_query] = 1 # found
                
                if mapping_result.has_multiple_pos():
                    if multiple_param == False:
                        continue
                
                mapping_results_list.append(mapping_result)
            
            #sys.stderr.write("**********NEXT\n")
            if len(test_set) == 0: break
        
        return mapping_results_list
    
    def _parse_index_file_by_id(self, query_ids_dict, index_path, data_path, map_config, chrom_dict,
                                                                    multiple_param, dataset_synonyms, test_set):
        mapping_results_list = []
        
        ## TODO: DO SOMETHING WITH THE SYNONYMS!!!
        ##
        
        map_name = map_config.get_name()
        map_has_cm_pos = map_config.has_cm_pos()
        map_has_bp_pos = map_config.has_bp_pos()
        map_is_physical = map_config.as_physical()
        
        sys.stderr.write("MappingsParser: loading index "+str(index_path)+"...\n")
        
        with open(index_path, 'r') as index_f:
            index = cPickle.load(index_f)
        
        sys.stderr.write("MappingsParser: loaded index with "+str(len(index))+" entries.\n")
        
        sys.stderr.write("MappingsParser: obtaining index of queries...\n")
        queries_bytes = []
        for query in test_set:
            if query in index:
                query_bytes = index[query]
                
                query_ids_dict[query] = 1 # found
                
                queries_bytes.append(query_bytes)
        
        with open(data_path, 'r') as data_f:
            for query_bytes in queries_bytes:
                data_f.seek(query_bytes)
                mapping_line = data_f.readline()
                mapping_data = mapping_line.strip().split("\t")
                mapping_result = MappingResult.init_from_data(mapping_data, map_name, chrom_dict, map_is_physical, map_has_cm_pos, map_has_bp_pos)
                
                if mapping_result.has_multiple_pos():
                    if multiple_param == False:
                        continue
                
                mapping_results_list.append(mapping_result)
        
        return mapping_results_list
    
    def parse_mapping_file_by_id(self, query_ids_dict, data_path, map_config, chrom_dict,
                                        multiple_param, dataset_synonyms = {}, test_set = None):
        mapping_results_list = []
        
        # check if there is an index
        index_path = data_path+".idx"
        if os.path.exists(index_path) and os.path.isfile(index_path):
            mapping_results_list = self._parse_index_file_by_id(query_ids_dict, index_path, data_path, map_config, chrom_dict,
                                                                    multiple_param, dataset_synonyms, test_set)
        else:
            mapping_results_list = self._parse_mapping_file_by_id(query_ids_dict, data_path, map_config, chrom_dict,
                                                                    multiple_param, dataset_synonyms, test_set)
        
        return mapping_results_list
    
    def parse_mapping_file_by_pos(self, map_intervals, data_path, chrom_dict, map_config, map_sort_by):
        mapping_results_list = []
        
        map_name = map_config.get_name()
        map_is_physical = map_config.as_physical()
        map_has_cm_pos = map_config.has_cm_pos()
        map_has_bp_pos = map_config.has_bp_pos()
        
        current_interval_pos = 0
        current_interval = map_intervals[current_interval_pos]
        
        # Find all the hits for this map within intervals of interest
        # Note: hits/map features are pre-computed & sorted along chroms, chroms are in chrom_dict order
        # Note: intervals are pre-sorted as well
        for hit in open(data_path, 'r'):
            if hit.startswith(">") or hit.startswith("#"): continue
            hit_data = hit.strip().split("\t")
            
            #sys.stderr.write(hit+"\n")
            #sys.stderr.write("\t"+str(current_interval)+"\n")
            
            mapping_result = MappingResult.init_from_data(hit_data, map_name, chrom_dict, map_is_physical, map_has_cm_pos, map_has_bp_pos)
            
            chrom_name = mapping_result.get_chrom_name()
            
            # move to next interval to match chrom (only if previous mappings exist)
            # Note: needed when last mapping matched exactly the last gene of a chrom
            while len(mapping_results_list) > 0 and \
                current_interval_pos < len(map_intervals)-1 and \
                int(chrom_dict[chrom_name]) > int(chrom_dict[current_interval.get_chrom()]):
                current_interval_pos += 1
                current_interval = map_intervals[current_interval_pos]
            
            if chrom_name != current_interval.get_chrom(): continue
            
            map_end_pos = mapping_result.get_sort_end_pos(map_sort_by)
            
            if float(map_end_pos) < float(current_interval.get_ini_pos()): continue
            
            marker_id = mapping_result.get_marker_id()
            chrom_order = mapping_result.get_chrom_order()
            map_pos = mapping_result.get_sort_pos(map_sort_by)#float(mapping_result.get_sort_pos(map_sort_by))
            
            while (float(map_pos) > float(current_interval.get_end_pos())):
                current_interval_pos += 1
                if current_interval_pos >= len(map_intervals):
                    break
                current_interval = map_intervals[current_interval_pos]
                if current_interval.get_chrom() != chrom_name:
                    break
            
            if current_interval_pos >= len(map_intervals): break
            
            if chrom_name != current_interval.get_chrom(): continue
            
            if float(map_end_pos) < float(current_interval.get_ini_pos()): continue
            
            dataset_interval = MapInterval(chrom_name, map_pos, map_end_pos)
            
            #sys.stderr.write("MappingsParser: by_pos "+str(dataset_interval)+" - "+str(current_interval)+"\n")
            
            does_overlap = MapInterval.intervals_overlap(dataset_interval, current_interval)
            
            # Check if alignment overlaps with some mapping interval
            if does_overlap:
                mapping_results_list.append(mapping_result)
        
        return mapping_results_list
    
    def parse_mapping_file_on_pos(self, map_intervals, data_path, chrom_dict, map_config, map_sort_by,
                                  dataset, dataset_name, feature_type):
        
        map_name = map_config.get_name()
        map_is_physical = map_config.as_physical()
        map_has_cm_pos = map_config.has_cm_pos()
        map_has_bp_pos = map_config.has_bp_pos()
        
        current_interval_pos = 0
        featured_current_interval = map_intervals[current_interval_pos]
        current_interval = featured_current_interval.get_map_interval()
        current_features = featured_current_interval.get_features()
        
        #sys.stderr.write("MappingsParser \n")
        #sys.stderr.write("\t"+str(current_interval)+"\n")
        #sys.stderr.write("\t"+str(len(current_features))+"\n")
        #for feature in current_features:
        #    sys.stderr.write("\t\t"+str(feature)+"\n")
        
        # Find all the hits for this map
        for hit in open(data_path, 'r'):
            if hit.startswith(">") or hit.startswith("#"): continue
            hit_data = hit.strip().split("\t")
            
            #sys.stderr.write(hit+"\n")
            #sys.stderr.write("\t"+str(current_interval)+"\n")
            
            mapping_result = MappingResult.init_from_data(hit_data, map_name, chrom_dict, map_is_physical, map_has_cm_pos, map_has_bp_pos)
            
            chrom_name = mapping_result.get_chrom_name()
            
            if chrom_name != current_interval.get_chrom(): continue
            
            map_end_pos = mapping_result.get_sort_end_pos(map_sort_by)
            
            if float(map_end_pos) < float(current_interval.get_ini_pos()): continue
            
            marker_id = mapping_result.get_marker_id()
            chrom_order = mapping_result.get_chrom_order()
            map_pos = mapping_result.get_sort_pos(map_sort_by)#float(mapping_result.get_sort_pos(map_sort_by))
            
            dataset_interval = MapInterval(chrom_name, map_pos, map_end_pos)
            
            does_overlap = MapInterval.intervals_overlap(dataset_interval, current_interval)
            # This if-else could be unnecessary, but hopefully is useful to read the code
            if does_overlap:
                next_interval_pos = current_interval_pos
                next_interval = current_interval
                next_features = current_features
                while (does_overlap):
                    feature = FeaturesFactory.get_feature(marker_id, dataset, dataset_name, feature_type, mapping_result)
                    next_features.append(feature)
                    
                    next_interval_pos += 1
                    if next_interval_pos >= len(map_intervals):
                        break
                    featured_next_interval = map_intervals[next_interval_pos]
                    next_interval = featured_next_interval.get_map_interval()
                    next_features = featured_next_interval.get_features()
                    
                    does_overlap = MapInterval.intervals_overlap(dataset_interval, next_interval)
                    
            else:
                while (float(map_pos) > float(current_interval.get_end_pos())):
                    current_interval_pos += 1
                    if current_interval_pos >= len(map_intervals):
                        break
                    featured_current_interval = map_intervals[current_interval_pos]
                    current_interval = featured_current_interval.get_map_interval()
                    current_features = featured_current_interval.get_features()
        
        #sys.stderr.write("MappingsParser generated intervals\n")
        #for featured_map_interval in map_intervals:
        #    map_interval = featured_map_interval.get_map_interval()
        #    sys.stderr.write("\tinterval: "+str(map_interval)+"\n")
        #    features = featured_map_interval.get_features()
        #    for feature in features:
        #        sys.stderr.write("\t\tfeature: "+str(feature)+"\n")
        
        return map_intervals
    
    ## This is an old function used in Mappers
    ## to build the final maps
    ## It could be refactored to use MappingsResults
    ## but this should be handled in Mappers also
    def parse_mapping_file_by_contig(self, contig_set, map_config, maps_path, verbose):
        positions_dict = {}
        # [contig_id] = {"chr", "cm_pos", "bp_pos"}
        
        map_id = map_config.get_id()
        map_db_list = map_config.get_db_list()
        map_dir = map_config.get_map_dir()
        
        #contig_set = set(contig_list) # A clone of contig_list. Used to shorten the search of contigs
        
        # For this genetic_map, read the info related to each database of contigs
        for db in map_db_list:
            db_records_read = 0
            
            # File with map-DB positions
            map_path = maps_path+map_dir+"/"+map_dir+"."+db
            if verbose: sys.stderr.write("\tMappingsParser: map file --> "+map_path+"\n")
            
            # Map data for this database
            for map_line in open(map_path, 'r'):
                db_records_read += 1
                map_data = map_line.strip().split("\t")
                
                contig_id = map_data[MapFile.MAP_FILE_CONTIG]
                
                # Create positions for this contig
                if contig_id in contig_set:
                    
                    map_pos_chr = map_data[MapFile.MAP_FILE_CHR]
                    
                    if not contig_id in positions_dict:
                        positions_dict[contig_id] = {}
                    
                    positions_dict[contig_id]["chr"] = map_pos_chr
                    
                    map_has_cm_pos = map_config.has_cm_pos()
                    if map_has_cm_pos:
                        positions_dict[contig_id]["cm_pos"] = map_data[MapFile.MAP_FILE_CM]#float(map_data[MapFile.MAP_FILE_CM])
                    else:
                        positions_dict[contig_id]["cm_pos"] = -1.0
                    
                    map_has_bp_pos = map_config.has_bp_pos()
                    if map_has_bp_pos: # "has_bp_pos"
                        positions_dict[contig_id]["bp_pos"] = map_data[MapFile.MAP_FILE_BP]#long(map_data[MapFile.MAP_FILE_BP])
                    else:
                        positions_dict[contig_id]["bp_pos"] = -1
                        
                    contig_set.remove(contig_id)
                    
                    if len(contig_set) == 0:
                        if verbose: sys.stderr.write("\t\t all sequences found -->")
                        break
            
            if verbose: sys.stderr.write("\t\t records read: "+str(db_records_read)+"\n")
            
        return positions_dict

## END

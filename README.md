README is part of Barleymap.
Copyright (C)  2013-2014  Carlos P Cantalapiedra.
(terms of use can be found within the distributed LICENSE file).

## Contents

 - 1: Barleymap overview
 - 2: Prerequisites
 - 3: Installation and configuration
 - 4: Tools
 - 5: Usage examples
 - 6: Default resources
 - 7: Customization
 
## 1) Barleymap overview

   Barleymap is a tool that allows to search the position of sequences
   in sequence-enriched genetic/physical maps.

   Although Barleymap is distributed with resources related to barley data,
   the application can be used with data from other organisms, if similar
   data is available and Barleymap is properly configured.

   There are two main commands to work with Barleymap:
   barleymap_align_seqs and barleymap_find_markers.

   #) The barleymap_align_seqs tool allows to search FASTA formatted
   sequences by means of sequence alignments, performed
   with Blast and/or GMAP, to different databases.

   #) The barleymap_find_markers uses a list of identifiers as input, to retrieve the
   targets associated to those identifiers, based on alignments performed previously
   and stored as precalculated datasets. Therefore, barleymap_find_markers does not need
   to perform any alignment; in other words, there is no need to use Blast or GMAP.

   Once Barleymap has obtained a list of targets, either from alignment to databases or
   from precalculated datasets, it will retrieve the position of such targets from
   map information. A map is basically a list of targets and their associated positions.

   Hence, Barleymap performs several steps, in which it queries different resources:

   - Databases: in the alignment step, Barleymap needs sequence databases created
       with Blast and/or GMAP.
       Therefore, Barleymap can associate the identifier of a
       query sequence to the identifier of a target in the database.

       FASTA sequences (queries) --> alignment to databases (targets) --> list of query-target

   - Datasets: the barleymap_find_markers tool uses precalculated datasets: lists of
       tuples query-target, that have been obtained previously from alignments.

       Identifiers (queries) --> find identifier in precalculated datasets (targets) --> list of query-target

   - Maps: once Barleymap has the query-target results from one of the previous steps, the
       target identifier can be used to retrieve the map position. This information is
       retrieved from map files.

       List query-target --> find target position on map --> associate position to query --> list of query-position

   Finally, Barleymap can enrich the resulting maps. This is achieved by either adding
   genes and their annotation to the results, based on position of genes on each
   genetic/physical map; or by adding other markers found in the region.
   For the enrichment with genes, Barleymap needs a list of gene-position for each map, and a file
   with gene annotations (see HOWTO_ADD_GENE_INFORMATION).
   To further relate markers and genes, and a list of marker-gene pairs, obtained by alignment,
   can be used by Barleymap to ameliorate the report (see HOWTO_ADD_DATASETS 2.1).

# 1) Prerequisites
#   - Python 2.x.x (Python 2.6 or superior)
#
#   - For tools based on sequence alignment (bmaux_align_external, bmaux_align_fasta, barleymap_align_seqs)
#   to work Blast and/or GMAP are needed.
#
#   For the current Barleymap version, the following builds have been tested:
#   Blast: ncbi-blast-2.2.27+
#   GMAP: gmap-2013-11-27
#
#   For barleymap_find_markers there is no other prerequisite than Python,
#   so you should be able to query different datasets by using Barleymap alone.
#
# 2) Installation and configuration
#
#   First, read INSTALL file.
#
#   After installing Barleymap you should be able to see a conf/ directory under
#   the main barleymap directory (eg.: barleymap/conf/).
#   In the conf/ directory, Barleymap has several configuration files.
#
#   You should first create working files by coping the ".example" files
#   to files without such suffix (eg.: barleymap/conf/paths.conf).
#   
#   Then, you should update "paths.conf" file with paths in your machine
#   (especially those fields indicated with values in capitals). For example,
#   change the "app_path" value to the current barleymap directory (absolute path)
#   For example: app_path /home/current_user/apps/barleymap_popseq/
#
#   To configure the other ".conf" files, read section "6) Customization".
#
# 3) Tools
#
#   The main tools that can be used with Barleymap are located in the bin/ directory.
#   There are two main tools: barleymap_align_seqs and barleymap_find_markers;
#   and others that are secondary or auxiliar, prefixed with "bmaux" (BarleyMapAUXiliar tools):
#   bmaux_check_config, bmaux_align_fasta, bmaux_align_external, bmaux_retrieve_datasets
#   and bmaux_obtain_positions.
#
#   Usage and info about any script can be obtained by typing "-h/--help" as command parameter. Example:
#
#   barleymap_find_markers -help
#
# 3.1) Auxiliar scripts
#
# - bmaux_check_config: allows to check the content of the config files and directories of the application.
#
#   It is run without parameters.
#   Output: paths, databases, datasets, maps, genes and annotation configured.
#
# - bmaux_align_fasta: intended to align fasta sequences to references and obtain the identifier of targets.
#
#   input: sequences in FASTA format.
#   resource: Blast and/or GMAP databases configured in the application.
#   output: list of query-target.
#
#           The alignment pipeline is explained at http://floresta.eead.csic.es/barleymap/help/
#
#           Some major parameters are "--hierarchical" and "--best-score".
#
#           "--hierarchical" is important when several databases are queried.
#
#           With "--hierarchical=no", each database results (if any) are reported separatedly
#           after a line with the database name prefixed with ">DB:".
#
#           When "--hierarchical=yes" is used, the sequence references are queried in the order
#           specified in the "--databases" parameter or, if not specified, configured in conf/references.conf.
#           When a query is found in one database, it is not further aligned againt the remaining
#           databases.
#
#           The "--best-score" parameter can be used to obtain all the alignments for every database
#           ("--best-score=no"), to obtain only the best alignment for every database ("--best-score=db"),
#           or to obtain only the best alignment for each query ("--best-score=yes").
#
#           Note that the score used is the bit score, for Blast results, and a function of query aligned
#           segment length and identity, in the case of GMAP alignments.
#
#   A simple example to execute the command would be:
#
#   ./bmaux_align_fasta --align-info=yes test_align.fa
#
#   IMPORTANT: remember that this script will work only if some sequence database has been previously configured.
#
#   NOTE: this tool can be used to create precalculated datasets with queries that are commonly used,
#   so that alignments are performed only once with this tool, and the data could be used
#   afterwards with barleymap_find_markers (see HOWTO_ADD_DATASETS).
#
# - bmaux_align_external: allows to align fasta sequences to any sequence dataset,
#                         obtaining the results as with bmaux_align_fasta.
#
#   input: sequences in FASTA format.
#   resource: Blast and/or GMAP databases. There is no need to have these databases configured in the application,
#             so they can be "external" to Barleymap, BUT THEY MUST reside under the path specified in
#             "blastn_dbs_path" entry in paths.conf file under conf/ directory.
#             NOTE that in this case, --databases parameter MUST be specified with a database or comma-separated
#             list of databases. In addition, as it is thought to be used with non-configured databases,
#             database identifier must be supplied instead of the database names that are used with bmaux_align_fasta,
#             even if the database to query has been already configured.
#   output: the same as align_fasta.
#
#   The algorithm steps and parameters are analog to those in bmaux_align_fasta.
#   This tool can be used, for example, to create the markers-genes datasets, so that genes that are hit by each marker
#   will be shown in the marker enriched map.
#   In general, it can be used to align FASTA sequences to any FASTA database using the Barleymap pipeline.
#
#   ./bmaux_align_external --hierarchical=yes --databases=genes_HC,genes_LC test_align.fa
#
#   IMPORTANT: remember that this script will work only if the sequence database resides under "blastn_dbs_path".
#
# - bmaux_retrieve_datasets: can be used to check the target of the alignment of sequences
#                            by using only the query ID, without need to realign the sequence
#
#   input: list of query identifiers.
#   resource: precalculated datasets.
#   output: list of query-target.
#
#   Regarding the behaviour of parameters and output format this script is analog to bmaux_align_fasta.
#
#   Can be used to check the data from a precalculated dataset.
#
#   A simple example:
#
#   ./bmaux_retrieve_datasets test_find.ids
#
# - bmaux_obtain_positions: to check the position of a target in a genetic/physical map
#
#   input: list of target identifiers.
#   resource: genetic/physical map.
#   output: list of target-position.
#           If several maps are queried, each map results begin after a line with the map name
#           prefixed with ">". If there are no results for a map, only that line will appear.
#
#   Can be used to check the results that can be obtained from a map.
#
#   An example:
#
#   ./bmaux_obtain_positions test_map.ids
#
# 3.2) Main tools
#
# - barleymap_align_seqs: main program to obtain map positions from FASTA sequences.
#
#   input: sequences in FASTA format.
#   resources: Blast and/or GMAP databases, and genetic/physical maps.
#   output: list of query-position, which can be enriched with genes or markers.
#           See 3.3) section for output format specification.
#
#   Can be used to obtain the position of sequences,
#   and the information of genes or markers associated to such positions.
#
#   The alignment step and parameters are analog to those of bmaux_align_fasta,
#   while the mapping parameters are similar to those of bmaux_obtain_positions.
#
#   IMPORTANT: remember that this script will work if some sequence database
#         has been previously configured, and its contigs have position
#         associated to a reference map.
#
# - barleymap_find_markers: main program to obtain map positions from marker IDs.
#
#   input: list of query identifiers.
#   resources: precalculated datasets, and genetic/physical maps.
#   output: list of query-position, which can be enriched with genes or markers.
#           See 3.3) section for output format specification.
#
#   Can be used to obtain the position of identifiers that have been previously aligned and stored in precalculated datasets,
#   and the information of genes or markers associated to such positions.
#
#   The retrieval step and parameters are analog to those of bmaux_retrieve_datasets,
#   while the mapping parameters are similar to those of bmaux_obtain_positions.
#
# 3.3) Main tools output
#
#   Results for each map are preceded by a line with map name prefixed with ">".
#   When only the main map is requested, output includes a line of headers prefixed with "#" (see below the format).
#   When the unmapped and unaligned results are requested too, three different tables of results
#   are reported, each starting with a line prefixed with "##":
#
#           - "##Map", "##Map with genes" or "##Map with markers" data, followed by usual mapping positions in the format explained below.
#
#           - "##Hits without pos", for query-target pairs without position. A third field indicates
#           whether the query has other alignments with map position.
#
#           - "##Unmapped": queries without both position and alignment data. That is, not target
#           was found when aligning with Blast and/or GMAP.
#   
#   Format of header (without genes info, tab separated) ("##Map" table):
#               ·Marker: marker identifier (ID).
#               ·chr: chromosome.
#               ·cM: centimorgan position. Shown only for maps with cM information available.
#               ·base pairs: basepairs position. Shown only for maps with base pairs information available.
#               ·multiple positions: whether the marker has more than one position. Only shown when "--show-multiples=yes".
#               ·other alignments: if marker has alignments without map position.
#
#   Fields that are added when genes info is requested (without annotation) ("##Map with genes" table):
#               ·Gene: gene identifier.
#               ·HC/LC: whether are High Confidence or Low Confidence genes.
#               ·chr: chromosome assigned to gene.
#               ·cM: centimorgan position associated to gene. Only shown for those maps with cM information available.
#               ·bp: basepairs position of gene. Only shown for those maps with base pairs information available.
#
#   Fields that are added when annotation for genes is requested  ("##Map with genes" table):
#               ·Description: human readable description.
#               ·InterPro: annotation results from InterPro.
#               ·Signatures: annotation results from family annotation databases (NOT only PFAM).
#               ·GO terms: Gene Ontology results.
#
#   Fields that are added when markers info is requested ("##Map with markers" table):
#               ·Marker: marker found in the interval.
#               ·Dataset: dataset source of the marker.
#               ·chr: chromosome assigned to such marker.
#               ·cM: centimorgan position associated to the marker. Only shown for those maps with cM information available.
#               ·bp: base pairs position of marker. Only shown for those maps with base pairs information available.
#               ·genes: a comma-separated list of genes to which this marker hit by sequence alignment. This data is optional
#                      and is shown only if Barleymap detects a "'dataset'.genes.hits" file in the directory of the marker's dataset.
#                       See HOWTO_ADD_DATASETS for details.
#
#   For other details about how Barleymap works, go to:
#   http://floresta.eead.csic.es/barleymap/help/
#   check the "-h/--help" option of commands
#   or contact the authors.
#
# 4) Usage examples (from inside bin/ directory)
#
# 4.1) bmaux_check_config
#
#   #) Show help
#
#       ./bmaux_check_config -h
#
#   #) Show Barleymap configuration
#
#       ./bmaux_check_config
#
# 4.2) bmaux_align_fasta
#
#   #) Perform a hierarchical alignment of test_align.fa against all configured databases
#
#       ./bmaux_align_fasta --hierarchical=yes test_align.fa
#
#   #) Align hierarchically test_align.fa against MorexWGS and BACs databases, using only Blast,
#       with 2 threads, and changing identity and coverage thresholds
#
#       ./bmaux_align_fasta --hierarchical=yes --databases=MorexWGS,SequencedBACs --query-mode=genomic --thres-id=96 --thres-cov=94 --threads=2 test_align.fa
#
# 4.3) bmaux_retrieve_datasets
#
#   #) Obtain targets from a non-hierarchical alignment of test_find.ids to three databases.
#
#       ./bmaux_retrieve_datasets --hierarchical=no --databases=MorexWGS,SequencedBACs,BACEndSequences test_find.ids
#
# 4.4) bmaux_obtain_positions
#
#   #) Obtain positions for test_map.ids, from both IBSC_2012 and POPSEQ maps
#
#       ./bmaux_obtain_positions --maps=IBSC_2012,POPSEQ test_map.ids
#
# 4.5) barleymap_align_seqs
#
#   #) Align test_align.fa against all databases, showing all mapped results
#
#       ./barleymap_align_seqs --show-multiples=yes --show-unmapped=no test_align.fa
#
#   #) Obtain alignment against MorexWGS, using only GMAP database (--query-mode=cdna), with genes and annotation data
#
#       ./barleymap_align_seqs --databases=MorexWGS --query-mode=cdna --show-multiples=no --show-unmapped=no --genes=between --annot=yes test_align.fa
#
#   #) As the previous example, but reporting unmapped queries as well.
#
#       ./barleymap_align_seqs --databases=MorexWGS --query-mode=cdna --show-multiples=no --show-unmapped=yes --genes=between --annot=yes test_align.fa
#
#   #) Retrieve only best hits from each database
#
#       ./barleymap_align_seqs --best-score=db --show-multiples=yes --show-unmapped=no test_align.fa
#
#   #) Retrieve only the best hits for each query
#
#       ./barleymap_align_seqs --best-score=yes --show-multiples=yes --show-unmapped=no test_align.fa
#
# 4.6) barleymap_find_markers
#
#   #) Analog to barley_align_seqs, without alignment parameters (--databases, --query-mode, --threads, --thres-id, --thres-cov)
#
#       ./barleymap_find_markers --show-multiples=no --show-unmapped=yes --genes=between --annot=yes test_find.ids
#
#   #) Show map with markers in the region, and extend search to 1.0 cM upstream and downstream for each chromosome bin.
#
#       ./barleymap_find_markers --markers=yes --extend=yes --genes-window=1.0 test_find.ids
#       
#
# 5) Default resources
#
# Although Barleymap can be configured to be used with data from other projects and organisms,
# it is distributed with a series of default resources and configuration files ready to use with barley genomics data.
#
# You can use Barleymap to retrieve positions from precalculated datasets directly.
# However, in the case of databases, being huge resources, you will need to download the original FASTA
# sequences and create the Blast and GMAP databases (see 5.1 and the file HOWTO_ADD_DATABASES).
#
# However, several sample databases are already included so that the user should:
#
#   - Update paths.conf file (see above), "blastn_app_path" and "gmap_app_path",
#     to point to the directory where blastn and gmap binaries reside.
#   - Extract the fasta sequences that are compressed under app_std/db_samples/fasta_samples.tar.gz
#     (e.g.: tar -zxf fasta_samples.tar.gz)
#   - Create the indexes with either Blast, GMAP or both.
#     Please, see app_std/db_samples/README file for further information.
#
# Next, the different barley datasets used by default by Barleymap are explained.
#
# 5.1) Databases
#
#   IBSC generated sequences are used as default sequence databases, and can be downloaded from:
#   ftp://ftpmips.helmholtz-muenchen.de/plants/barley/public_data/
#
#   #) Three Whole Genome Shotgun datasets from three cultivars: Morex, Bowman and Barke.
#   #) BAC End Sequences.
#   #) Sequenced BACs.
#
#   Both Blast and GMAP databases were created for those resources (see HOWTO_ADD_DATABASES for further info).
#
# 5.2) Datasets
#
#   These are mainly sets of genetic markers that are commonly used to genotype barley mapping populations.
#   flcDNAs and ESTs are mRNA derived sequences. Alignment data for each dataset has been calculated
#   separatedly for each database, so that data can be queried independently, or through hierarchical method.
#
#   #) Illumina Infinium iSelect 9K: array platform of barley SNPs
#   #) DArTs: Diversity Arrays presence/absence (PAVs) markers obtained after enzymatic digestion.
#   #) DArTseq SNPs and PAVs: Diversity Arrays' GBS markers (both SNPs and PAVs).
#       * NOTE that some SNPs and PAVs are in fact the same sequence, so that the identifier is the same
#           for both markers and the alignment results should be equal.
#   #) Oregon Wolfe Barley population GBS data. 
#   #) flcDNA from cultivar Haruna nijo.
#   #) HarvEST assembly 36
#
#   You can find further information about these datasets
#   and the identifiers to use at
#   http://floresta.eead.csic.es/barleymap/help/
#
#   These datasets were created as shown in HOWTO_ADD_DATASETS.
#
# 5.3) Genetic/Physical maps
#
#   #) IBSC 2012 map: positions for all the databases. ftp://ftpmips.helmholtz-muenchen.de/plants/barley/public_data/
#   #) POPSEQ map (2013): positions only for Morex WGS database. ftp://ftp.ipk-gatersleben.de/barley-popseq/
#
#   These maps were configured as explained in HOWTO_ADD_MAPS.
#
# 5.4) Genes information and annotation
#
#   #) IBSC high confidence (HC) and low confidence (LC) genes from IBSC transcriptome (see IBSC 2012 map reference above).
#   #) Functional annotation of genes from the same IBSC 2012 source.
#
#   These resources were added as shown in HOWTO_ADD_GENE_INFORMATION.
#
# 6) Customization
#
# Barleymap is flexible and can be configured to retrieve data from different databases, datasets and/or genetic/physical maps.
# This way, it can be adapted even to use data from an organism other than barley. Moreover, this means that you could
# add new datasets and re-distribute the application with them, so that there is no need to perform the alignments again.
#
# To be able to customize Barleymap you should read the "HOWTO" files:
# HOWTO_ADD_DATABASES
# HOWTO_ADD_DATASETS
# HOWTO_ADD_MAPS
# HOWTO_ADD_GENE_INFORMATION
##

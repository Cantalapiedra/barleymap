
## Contents

 - 1: [Barleymap overview](https://github.com/Cantalapiedra/barleymap#1-barleymap-overview)
 - 2: Prerequisites
 - 3: Installation and configuration
 - 4: Tools
 - 5: Usage examples
 - 6: Default resources
 - 7: Customization
 
## 1) Barleymap overview

**Barleymap** is a tool which allows searching the position of sequences
in sequence-enriched genetic/physical maps.

Barleymap was designed with **3 main goals** in mind:
- Provide the position of sequences in a map, hiding from the user the details of the alignment and mapping steps.
- Facilitate inspecting the region surrounding the queried sequence.
- Perform alignments in a multi-reference or pan-genome fashion, allowing to query several databases at a time.

Therefore, there are three basic **tasks** which can be carried out with barleymap,
depending on the input data to be used:

- Locate FASTA formatted sequences in a map through sequence alignment.
- Retrieve the position of common-use markers (or other features, like genes) of known ID,
whose positions have been pre-computed.
- Inspect the features (markers, genes, etc) in the surroundings of a given map position.

To do this, barleymap works with the following **resources**:

- Databases: FASTA sequences from sequence-enriched maps, genomes, or any other sequence reference.
- Maps: tables with positions of every FASTA sequence from the databases. Note that a map can store positions
of sequences from one or several databases.
- Datasets: tables which store the result of alignment of a given query to a specific map.

Barleymap has 3 different groups of **tools**, which are further explained in following sections:
- Main tools:
  - bmap_align ("Align sequences" in the web version).
  - bmap_find ("Find markers" in the web version).
  - bmap_locate ("Locate by position" in the web version).
- Secondary tools:
  - bmap_align_to_db (only in the standalone version).
  - bmap_align_to_map (only in the standalone version).
- Configuration tools:
  - bmap_build_datasets
  - bmap_datasets_index
  - bmap_config

## 2) Prerequisites

- Python 2.6 or superior.
- To perform sequence alignments barleymap will need either Blast, HS-blastn and/or GMAP.

For the current barleymap version, the following builds have been tested:
- Blast: ncbi-blast-2.2.27+
- GMAP: gmap-2013-11-27 and gmap-2013-08-31
- HS-blastn: hs-blastn-0.0.5+

## 3) Installation and configuration

### 3.1) Installation

Either:
- clone barleymap github repository.
- download a release, uncompress it.

Configure PATH and PYTHONPATH as needed.

For example:
```
mkdir /home/$USER/apps;
cd /home/$USER/apps;
tar -zxf barleymap.tar.gz
export PATH=$PATH:/home/$USER/apps/barleymap/bin/
export PYTHONPATH=$PYTHONPATH:/home/$USER/apps/barleymap/
```

### 3.2) Configuration

To configure barleymap you will need to edit the following **configuration files**
under the barleymap/conf directory:

- paths.conf
- databases.conf
- maps.conf
- datasets.conf

Note that barleymap is distributed with *.sample files, which are just examples of the previous configuration
files. You could use them as templates to create you own configuration files.
Just remember that the "good" ones must not have the ".sample" suffix.

#### 3.2.1 The paths.conf file

The first thing you will need to do is configuring the **paths.conf** file under the barleymap/conf directory.
The content of the paths.conf file must have the next fields (shown as in paths.conf.sample file):

```
# App absolute path
app_path PATH_TO_BARLEYMAP_DIR

# Relative paths to auxiliary apps
genmap_path app_aux/
split_blast_path app_aux/

# Absolute paths to temporary and datasets folders
tmp_files_path PATH_TO_BARLEYMAP_DIR/tmp_files
datasets_path PATH_TO_BARLEYMAP_DIR/datasets/
annot_path PATH_TO_BARLEYMAP_DIR/datasets_annotation/
maps_path PATH_TO_BARLEYMAP_DIR/maps/

########### Aligners
# Blast
blastn_app_path PATH_TO_NCBI_BLAST/bin/blastn
blastn_dbs_path PATH_TO_BLAST_DATABASES
# GMAP
gmap_app_path PATH_TO_GMAP/bin/gmap
gmap_dbs_path PATH_TO_GMAP_DATABASES
gmapl_app_path PATH_TO_GMAP/bin/gmapl
# HS-Blastn
hsblastn_app_path PATH_TO_HSBLASTN/hs-blastn-src/hs-blastn
hsblastn_dbs_path PATH_TO_HSBLASTN_DATABASES

########### Other
citation Cantalapiedra_CP,_Boudiar_R,_Casas_AM,_Igartua_E,_Contreras-Moreira_B._BARLEYMAP:_physical_and_genetic_mapping_of_nucleotide_sequences_and_annotation_of_surrounding_loci_in_barley._Mol_Breeding_(2015)_35:13_DOI_10.1007/s11032-015-0253-1
stdalone_app http://eead.csic.es/compbio/soft/barleymap/
```

First, you will need to edit the *app_path* field to point
to the **absolute path** in which barleymap has been installed.

The fields *genmap_path* and *split_blast_path*, and also those under
the section *Other* ("citation" and "stdalone_app") should be left **unmodified**.

For most of the other fields, the directories they reference will most likely be empty at the moment.
Thus, you could configure them already or wait until you decide where the data will be stored.

The *tmp_files_path* indicates barleymap where should write temporary files to.
The *datasets_path*, *annot_path* and *maps_path* tells barleymap from which directories
should read data corresponding to datasets, annotation and maps.

Regarding the section *Aligners*, you will need to edit only the fields corresponding to the aligner
or aligners which will be used by your barleymap. For each aligner to be used, barleymap needs:

- The **path to the binary** file of the aligner. You will need to change the corresponding strings 
(PATH_TO_NCBI_BLAST, PATH_TO_GMAP and/or PATH_TO_HSBLASTN).

- The **path to the sequence databases** (genome, sequence-enriched map, or any other sequence reference).
You will need to change the corresponding strings
(PATH_TO_BLAST_DATABASES, PATH_TO_GMAP_DATABASES and/or PATH_TO_HSBLASTN_DATABASES).

#### 3.2.2 Creating and configuring databases: the databases.conf file

A database represents a sequence reference (a genome, a WGS assembly, or similar), which can be queried
with an alignment tool (Blastn, GMAP or HS-Blastn in the current version of barleymap).

Barleymap requires at least one database to work with. There are 2 steps to add a database to barleymap:

- First: create the database (with the corresponding tool from Blast, GMAP or HS-Blastn).
Note that the database should be accesible from the corresponding path indicated in the "paths.conf" file
(fields "blastn_dbs_path", "gmap_dbs_path" or "hsblastn_dbs_path").

- Secondly: configure the database in barleymap. To do that, the "databases.conf" file,
under the barleymap/conf directory, must be edited.
Each database should be added as a single row with 3 space-separated fields:
  - Database name: an arbitrary name for the database, used by the user for referencing it and for printing purposes.
  - Database unique ID: a unique identifier of the database. This should match the folder or files where the actual
database is stored, depending on the aligner (see "paths.conf" "Aligners" section).
  - Database type: either "std" or "big". It just tells barleymap whether to use the gmap or the gmapl binary
  when using the GMAP aligner. Check GMAP documentation for size of databases supported with gmap or gmapl.
  
The "databases.conf.sample" file shows 3 databases as examples:

```
# name unique_id type
SpeciesAGenome speciesA std
SpeciesBGenome speciesB std
PolyploidGenome polyploid big
```

Note that the aligner to be used with each database is not specified.
For a single barleymap database, you could actually have Blast, GMAP and HS-Blastn sequence databases.

Once at least one database has been correctly configured,
the following tools can already be used:
- bmap_align_to_db

#### 3.2.3 Creating and configuring maps: the maps.conf file

A map stores the positional arrangement of sequences, either physical or genetical, from one or several databases.

There are several steps to add a map to barleymap:

- Choose an identifier to be used as unique ID for this map ("map_ID").
- Create a folder "map_ID", under the path indicated by the "maps_path" entry in the "paths.conf" file
 (e.g. barleymap/maps/map_ID/).
- If the map is of type "anchored" (see below), create a file with the name "map_ID.database_ID",
 for each database which will be included in such map, and put it
in the folder created for the map in the previous step (e.g. barleymap/maps/map_ID/map_ID.database_ID).
See format of the map-database files below for details.
- Create a file with the name "map_ID.chrom" and put it in the folder created for the map
(e.g. barleymap/maps/map_ID/map_ID.chrom). See format of the "chrom" file below for details.
- Create a row in the conf/maps.conf file, with 10 space-separated fields.
  - Map name: an arbitrary name for the map, used by the user for referencing it and for printing purposes.
  - Map ID: the "map_ID" chosen above.
  - Has cM positions: either "cm_true" or "cm_false", indicating whether the map has genetic positions or not.
  - Has bp positions: either "bp_true" or "bp_false", indicating whether the map has physical positions or not.
  - Default position type: either "cm" or "bp". Used only when a map has both cM and bp positions.
  - Map type: either "physical" or "anchored".
    - A "physical" map (e.g. a genome) does not have a file for positions
  since the positions are those from the database and are already obtained
  from the alignment result (e.g. chr1H position 133002).
    - An "anchored" map (e.g. a sequence-enriched genetic map) requires files for positions,
  since the positions from the databases, obtained through alignment (e.g. contig_1300 position 12430),
  need to be translated to map positions (e.g. chr1H position 44.1 cM).
  - Search type: it states which type of algorithm will be performed when searching sequences in this map.
  Either "greedy", "hierarchical" or "exhaustive".
    - The "greedy" algorithm searches all the queries in all the databases of the current map.
    - The "hierarchical" algorithm keeps searching in further databases only those queries
    which have not been aligned to a database yet.
    - The "exhaustive" algorithm keeps searching in further database only those queries
    which still lack map position, independently of whether have already been aligned or not.
  - DB list: a comma-separated list of database IDs which are associated to this map. These are the databases which
  will be used as sequence references when this map is queried.
  - Folder: the folder name for this map, usually the same as the map ID.
  - Main datasets: a comma-separated list of datasets IDs which are associated to this map. These datasets will be always
  shown when looking for surrounding features, whereas other datasets will be shown only when explicitly requested.

##### Format of the map-database files

A map-database file contain the map position of the sequences of a database.

Rows starting with ">" or "#" will be ignored, so that it can be used for comments, map name or header fields.
Data rows have 5 or 6 (depending whether the map has cM, bp or both types of position) tab-delimited fields:
- Database entry: name of the chromosome, contig, etc. from the database.
- chr: chromosome identifier, corresponding to the map position of this database entry.
- cM, bp or both: 1 or 2 fields with numeric position within the chromosome.
- Multiple positions: either "Yes" or "No", to indicate whether this database entry has more than one
position in this map.
- Other alignments: either "Yes" or "No", to indicate whether this database entry has more than one
alignment in this map, independently of whether has more than one position or not.

##### Format of the "chrom" file

A "chrom" file has the information about the name and size of the chromosomes of a map.

Each row has 3 or 4 (depending whether the map has cM, bp or both types of position) tab-delimited fields:
- Chromosome name: an arbitrary name for the chromosome, used for printing purposes.
- Chromosome ID: a unique identifier for this chromosome in this map.
- cM, bp or both: 1 or 2 fields with the maximum position of this chromosome (i.e. its length in cM or bp).

Once that at least one database and one map have been correctly configured,
the following tools can already be used:
- bmap_align_to_db
- bmap_align_to_map
- bmap_align

The bmap_find and bmap_locate could be used, but lack interest without having configured datasets.

#### 3.2.4 Creating and configuring datasets: the datasets.conf file

Some genes or markers are often searched in sequence databases, genomes or maps.
Therefore, it is advantageous to search them once and store the result, so that
this position can be recovered in sucessive searches.
This is the main purpose of datasets.

The other use of datasets is showing which features (genes, markers, etc) are present in the region
in which a query of interest (e.g. a QTL) has been found.

Therefore, a dataset contains the map positions of markers, genes or other features, which have been
previously aligned and mapped. These positions can be retrieved using just the gene or marker identifiers, avoiding
to repeat demanding processes (specially alignment).

To create a dataset there are several steps to follow:
- Choose a unique identifier for your dataset ("dataset_ID").
- Create a folder "dataset_ID" under the path indicated by the "datasets_path" entry in the "paths.conf" file
 (e.g. barleymap/datasets/dataset_ID/).
- Create a file with the name "dataset_ID.map_ID",
 for each map which will be associated to such dataset, and put it
in the folder created for the dataset in the previous step (e.g. barleymap/datasets/dataset_ID/dataset_ID.map_ID).
See format of the dataset-map files below for details.
- Create a row in the conf/datasets.conf file, with 8 space-separated fields.
  - Dataset name: an arbitrary name for the dataset, used by the user to reference it and for printing purposes.
  - Dataset ID: a unique identifier for this dataset.
  - Type: either "genetic_marker", "gene", "map" or "anchored".
  - Filename: the raw data for the dataset (it is not required to use barleymap, but it is convenient to
  create the dataset automatically, as explained later).
  - File type: either "fna", "bed", "gtf", or "map". The file type of the previous filename.
  - Database list: either "ANY" or a database ID to which this dataset will be associated.
  - Synonyms file: path to the file of synonyms. This file can be used to store more than one name for each
  feature in this dataset.
  - Prefix for indexing: if all the features of the dataset are expected to start their names with the same characteres,
  this can be used to create and retrieve data from indexes.

Once that at least one database, one map and one dataset have been correctly configured,
the following tools can already be used:
- bmap_align_to_db
- bmap_align_to_map
- bmap_align
- bmap_find
- bmap_locate

## 3) Tools

The main tools that can be used with Barleymap are located in the bin/ directory.
There are two main tools: barleymap_align_seqs and barleymap_find_markers;
and others that are secondary or auxiliar, prefixed with "bmaux" (BarleyMapAUXiliar tools):
bmaux_check_config, bmaux_align_fasta, bmaux_align_external, bmaux_retrieve_datasets
and bmaux_obtain_positions.

Usage and info about any script can be obtained by typing "-h/--help" as command parameter. Example:

barleymap_find_markers -help

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

README is part of Barleymap.
Copyright (C)  2013-2014  Carlos P Cantalapiedra.
(terms of use can be found within the distributed LICENSE file).
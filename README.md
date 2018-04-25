
## Contents

 - 1: [Barleymap overview](https://github.com/Cantalapiedra/barleymap#1-barleymap-overview)
 - 2: [Prerequisites](https://github.com/Cantalapiedra/barleymap#2-prerequisites)
 - 3: [Installation and configuration](https://github.com/Cantalapiedra/barleymap#3-installation-and-configuration)
 - 4: [Tools and algorithms](https://github.com/Cantalapiedra/barleymap#4-tools-and-algorithms)
 
## 1) Barleymap overview

**Barleymap** is a tool which allows searching the position of sequences
in sequence-enriched genetic/physical maps.

Barleymap was designed with **3 main goals** in mind:
- Provide the position of sequences in a map, hiding from the user the details of the alignment and mapping steps.
- Facilitate inspecting the region surrounding the queried sequence. ¿Which other markers, genes, etc are in the region?
- Perform alignments in a multi-reference or pan-genome fashion, allowing to query several databases at a time.

Therefore, there are three basic **tasks** which can be carried out with barleymap,
depending on the input data used:

- Obtain the map position of FASTA formatted sequences by alignment.
- Find the map position of common-use loci (like markers, genes, etc.) of known ID,
whose positions have been pre-computed.
- Locate other loci (markers, genes, etc) in the surroundings of a given map position.

To do this, barleymap works with the following **resources**:

- Databases: sequences from genomes, sequence-enriched maps, or any other sequence reference,
in FASTA format.
- Maps: tables with map positions of the FASTA sequences from the databases.
Note that a map can store positions of sequences from one or more databases.
- Datasets: tables which store the map position of loci often used as queries (markers, genes, etc.)
to a specific map, so that it can be queried without repeating the alignment step.

Barleymap has 3 different groups of **tools**, which are further explained in following sections:
- Main tools:
  - bmap_align ("Align sequences" in the web version).
  - bmap_find ("Find markers" in the web version).
  - bmap_locate ("Locate by position" in the web version).
- Secondary tools (only in the standalone version):
  - bmap_align_to_db 
  - bmap_align_to_map
- Configuration tools (only in the standalone version):
  - bmap_build_datasets
  - bmap_datasets_index
  - bmap_config

## 2) Prerequisites

- Python 2.6 or superior.
- To perform sequence alignments barleymap will need
either BLASTN, HS-BLASTN and/or GMAP sequence aligners.

The following builds have been tested:
- Blast: ncbi-blast-2.2.27+
- GMAP: gmap-2013-11-27 and gmap-2013-08-31
- HS-blastn: hs-blastn-0.0.5+

Other versions of the previous aligners could also work with barleymap,
as long as the aligner parameters or its output format remain as in the versions above.

## 3) Installation and configuration

### 3.1) Installation

#### 3.1.1) Standalone version

Either:
- clone the barleymap github repository.
- download a [release](https://github.com/Cantalapiedra/barleymap/releases),
and uncompress it.

Configure environmental variables (e.g. PATH and PYTHONPATH in linux) as needed.

For example:
```
mkdir /home/$USER/apps;
cd /home/$USER/apps;
curl -O https://github.com/Cantalapiedra/barleymap/archive/barleymap-3.0.tar.gz
tar -zxf barleymap-3.0.tar.gz
rm barleymap-3.0.tar.gz
mv barleymap-3.0 barleymap
export PATH=$PATH:/home/$USER/apps/barleymap/bin/
export PYTHONPATH=$PYTHONPATH:/home/$USER/apps/barleymap/
```

#### 3.1.2) Web version

The barleymap web interface was designed to be used with a [CherryPy server](http://cherrypy.org/),
which should be installed and configured independently.

Those interested on running their own barleymap web servers should check the CherryPy documentation
to setup the server with their own infrastructure.
For example, when using CherryPy after an Apache server you could need to add to its configuration
files a reverse proxy, like:

```
ProxyPass /barleymap http://127.0.0.1:$CHERRYPYPORT/barleymap/
ProxyPassReverse /barleymap http://127.0.0.1:$CHERRYPYPORT/barleymap/
```

Barleymap web versions includes three shell scripts
(_START, _RESTART and _STOP) to make it easier to
start, restart and stop the application server.

Note that besides the configuration steps detailed in the next sections,
for the barleymap web application it could be required, depending on the environment,
to configure the *src/bmap.conf* and *src/server.conf* files.

### 3.2) Configuration

- 3.2.1: [Global configuration: the *paths.conf* file](https://github.com/Cantalapiedra/barleymap#321-global-configuration-the-pathsconf-file)
- 3.2.2: [Databases: the *databases.conf* file](https://github.com/Cantalapiedra/barleymap#322-databases-the-databasesconf-file)
- 3.2.3: [Maps: the *maps.conf* file](https://github.com/Cantalapiedra/barleymap#323-maps-the-mapsconf-file)
- 3.2.4: [Datasets: the *datasets.conf* file](https://github.com/Cantalapiedra/barleymap#324-datasets-the-datasetsconf-file)
- 3.2.5: [Annotations: the *datasets_annotation.conf* file](https://github.com/Cantalapiedra/barleymap#325-annotations-the-datasets_annotationconf-file)
   
To configure barleymap you will need to edit the following **configuration files**
under the *barleymap/conf* directory:

- *paths.conf*
- *databases.conf*
- *maps.conf*
- *datasets.conf*
- *datasets_annotation.conf*

Note that barleymap is distributed with *.sample* files, which are just examples of the previous configuration
files. You could use them as templates to create you own configuration files.
Just remember that the ones actually used by barleymap must not have the *.sample* suffix.

All barleymap **configuration** files have one **field** per row. Each row has 2 space-separated columns:
the *field name* and the *field value*.
To a edit a field, edit its value. Field names should be left unmodified.

#### 3.2.1 Global configuration: the *paths.conf* file

The first thing you will need to do is configuring the ***paths.conf*** file under the *barleymap/conf* directory.
The content of the *paths.conf* file must have the next fields (shown as in *paths.conf.sample* file):

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

The values of fields *genmap_path* and *split_blast_path*, and also those under
the section *Other* (*citation* and *stdalone_app*) should be left **unmodified**.

For most of the other fields, the directories they reference will most likely be empty at the moment.
Thus, you could configure them already or wait until you decide where the data will be stored.

The *tmp_files_path* field indicates to barleymap where it should write temporary files to.
The *datasets_path*, *annot_path* and *maps_path* fields tell barleymap from which directories
should read data corresponding to datasets, annotation and maps, respectively.
To be sure that barleymap is reading those paths correctly, using absolute paths are recommended.

Regarding the section *Aligners*, only the fields corresponding to the aligner
or aligners which will be used by the current barleymap instance will need to be edited.
For each aligner to be used, barleymap needs:

- The **absolute path to the binary** file of the aligner.
You will need to change the values of *blastn_app_path*, *gmap_app_path*, *gmapl_app_path*,
and *hsblastn_app_path* fields.

- The **absolute path to the sequence databases** (genome, sequence-enriched map, or any other sequence reference).
You will need to change the values of *blastn_dbs_path*, *gmap_dbs_path*, and *hsblastn_dbs_path*.

Note that although both the standalone and the web versions need their own configuration files,
the actual resources (databases, datasets and maps) can be shared by both applications by configuring
the previous fields to point to the same directories.

#### 3.2.2 Databases: the *databases.conf* file

A **database** represents a sequence reference (a genome or similar), which can be queried
with one or more alignment tools (BLASTN, GMAP or HS-BLASTN in the current version of barleymap).

To look for position of sequences through alignment,
barleymap requires at least one database to work with.
It takes 3 steps to add a database to barleymap:

1.  Create the files of the database with the corresponding tool from BLASTN, GMAP and/or HS-BLASTN
(e.g. *makeblastdb* for BLASTN, *gmap_build* for GMAP).
1. Put the database files under the path indicated in the *paths.conf* file
for the corresponding aligner.
1. Configure the database in barleymap. To do that, edit *databases.conf* file.
Each database should be added as a single row with **3 space-separated fields**:
  - Name: an arbitrary name for the database, used by the user for referencing it and for printing purposes.
  - Unique identifier (ID): a unique ID for the database. This should match the folder (GMAP)
  or prefix of files (BLASTN, HS-BLASTN) where the actual database is stored.
  - Type: either "std" or "big". It just tells barleymap whether to use the *gmap* or the *gmapl* binary
  when using the GMAP aligner. Check GMAP documentation for size of databases supported with *gmap* or *gmapl*.
  
The *databases.conf.sample* file shows 3 databases as **examples**:

```
#name            unique_id  type
SpeciesAGenome   speciesA   std
SpeciesBGenome   speciesB   std
PolyploidGenome  polyploid  big
```

Note that the aligner to be used with each database is not specified:
for a single barleymap database, you could actually have BLASTN, GMAP and HS-BLASTN sequence databases.

The first database, called "SpaciesAGenome" has the ID "speciesA", and thus its actual
files (e.g. from BLASTN) and folders (e.g. from GMAP) should be prefixed "speciesA" and placed under the
directory indicated for that aligner in the *paths.conf* file.
For example, if we created a GMAP index for this "speciesA" database, and the path for
GMAP databases was configured as */home/user/barleymap/databases/gmap/* in *paths.conf*,
we should move the "speciesA" folder created by GMAP so that the database will be at
*/home/user/barleymap/databases/gmap/speciesA*.

***

Once at least one database has been correctly configured,
the following tools can be used:
- bmap_align_to_db

#### 3.2.3 Maps: the *maps.conf* file

A **map** stores the positional arrangement, either physical or genetical, of sequences from one or several databases.

It takes 5 steps to add a map to barleymap:

1. Choose an identifier to be used as unique ID for this map (*map_ID*).
1. Create a folder called *map_ID*, under the path indicated by the *maps_path* entry in the *paths.conf* file
 (e.g. *barleymap/maps/map_ID/*).
1. If the map is of type "anchored" (see below), create a file called *map_ID.database_ID*,
 for each database to be associated to this map, and put it
under the folder created for the map in the previous step (e.g. *barleymap/maps/map_ID/map_ID.database_ID*).
See [format of the map-database files](https://github.com/Cantalapiedra/barleymap#format-of-the-map-database-files)
below for details.
1. Create a file with the name *map_ID.chrom* and put it in the folder created for the map
(e.g. *barleymap/maps/map_ID/map_ID.chrom*).
See [format of the "chrom" file](https://github.com/Cantalapiedra/barleymap#format-of-the-chrom-file) below for details.
1. Create a row in the *conf/maps.conf* file, with **10 space-separated fields**:
  - Name: an arbitrary name for the map, used by the user for referencing it and for printing purposes.
  - ID: the *map_ID* chosen above.
  - It has cM positions: either "cm_true" or "cm_false", indicating whether the map has genetic positions or not.
  - It has bp positions: either "bp_true" or "bp_false", indicating whether the map has physical positions or not.
  - Default position type: either "cm" or "bp". Used only when a map has both cM and bp positions.
  - Type: either "physical" or "anchored".
    - A "physical" map (e.g. a genome) has not files for positions
  since the positions are those from the database and are already obtained
  from the alignment result (e.g. chr1H position 133002).
    - An "anchored" map (e.g. a sequence-enriched genetic map) requires files for positions,
  since the positions from the databases, obtained through alignment (e.g. contig_1300 position 12430),
  need to be translated to map positions (e.g. chr1H position 44.1 cM).
  - Search type: it states which type of algorithm will be performed when searching sequences
  in the databases associated to this map. Can be either "greedy", "hierarchical" or "exhaustive".
  
    - The "greedy" algorithm searches all the queries in all the databases of the current map.
    - The "hierarchical" algorithm keeps searching in further databases only those queries
    which have not been aligned to a database yet.
    - The "exhaustive" algorithm keeps searching in further database only those queries
    which still lack map position, independently of whether have already a hit from alignment or not.
    
  - Database list: a comma-separated list of database IDs which are associated to this map.
  These are the databases which will be used as sequence references when this map is queried.
  - Folder: the folder name for this map, usually the same as the map ID.
  - Main datasets: a comma-separated list of datasets IDs which are associated to this map. These datasets will be always
  shown when looking for surrounding features, whereas other datasets will be shown only when explicitly requested.
  
The *maps.conf.sample* file shows 3 maps as **examples**:

```
#name         id            has_cm    has_bp    default_pos_type  map_type  search_type   db_list                                 folder_name        main_datasets
MapName       mapID         cm_false  bp_true   bp                physical  greedy        db_genome                               mapID_folder       dataset1,dataset2,dataset3
Map2          map2          cm_true   bp_false  cm                genetic   hierarchical  db_anchored1                            map2_dir           dataset4
PhysGenetMap  physgenetmap  cm_true   bp_true   cm                genetic   exhaustive    db_anchored1,db_anchored2,db_anchored3  physgenetmap_path  dataset3,dataset5
```

The first map, called "MapName", with ID "mapID", and stored in the folder *mapID_folder*,
is a physical map ("cm_false", "bp_true", "bp", "physical"),
with a single database (with ID *db_genome*) of sequences associated to it.
Having a single database makes irrelevant the "Search type" field
(which has been set to "greedy", arbitrarily).
The map has 3 datasets associated as main datasets.

The second map ("Map2") is a genetic map ("cm_true", "bp_false", "cm", "genetic")
with a single database of sequences associated to it (*db_anchored1*).
Again, the "Search type" will be irrelevant
having only one database (and thus has been configured to "hierarchical", arbitrarily).

The third map ("PhysGenetMap") is a genetical and physical map ("cm_true", "bp_true", "cm", "genetic"),
with 3 databases associated to it (*db_anchored1*, *db_anchored2* and *db_anchored3*).
Here, the "Search type" algorithm was set to "exhaustive", to keep searching each query in the next database,
until a map position has been found for the it.

##### Format of the map-database files

A map-database file contains the map position of the sequences of a database.
For example, a file called *map2.contigs_database" could have:

```
>Map2
#Marker         chr  cM                 multiple_positions  other_alignments
contig_1011389  1    0.106232294617565  No                  No
contig_1029771  1    0.106232294617565  No                  No
contig_110298   1    0.106232294617565  No                  No
contig_111381   1    0.106232294617565  No                  No
contig_1170672  1    0.106232294617565  No                  No
contig_1269062  1    0.106232294617565  No                  No
contig_13304    1    0.106232294617565  No                  No
contig_13532    1    0.106232294617565  No                  No
```

Rows starting with ">" or "#" will be ignored, so that it can be used for comments, map name or header fields.

Data rows have 5 or 6 (depending whether the map has cM, bp or both types of position) **tab-delimited fields**:

- Database entry: ID of the contig, chromosome, etc. from the database.
- chr: ID of the chromosome from the map.
- cM, bp or both: 1 or 2 fields with numeric position within the map chromosome.
- Multiple positions: either "Yes" or "No", to indicate whether this database entry has more than one
position in this map.
- Other alignments: either "Yes" or "No", to indicate whether this database entry has more than one
alignment in this map, independently of whether has more than one position or not.

##### Format of the "chrom" file

A "chrom" file has the information about the name and size of the chromosomes of a map. For example:

```
chr1H	1	558535432
chr2H	2	768075024
chr3H	3	699711114
chr4H	4	647060158
chr5H	5	670030160
chr6H	6	583380513
chr7H	7	657224000
chrUn	8	249774706
```

Each row has 3 or 4 (depending whether the map has cM, bp or both types of position) **tab-delimited fields**:
- Chromosome name: an arbitrary name for the chromosome, used for printing purposes.
- Chromosome ID: a unique identifier for this chromosome in this map.
- cM, bp or both: 1 or 2 fields with the maximum position of this chromosome (i.e. its size or length in cM or bp).
This is actually only needed for the web version of barleymap, where it is used to print the graphical chromosomes.
For the standalone version you could just leave it to any value.

***

Once that at least one database and one map have been correctly configured,
the following tools can be used:
- bmap_align_to_db
- bmap_align_to_map
- bmap_align

The bmap_find and bmap_locate could be used, but there is no interest in running them
without having configured datasets previously.

#### 3.2.4 Datasets: the *datasets.conf* file

Some genes or markers are searched in sequence databases, genomes or maps very often.
Therefore, it is advantageous to search them once and store the result, so that
this position can be retrieved in sucessive searches without repeating the alignment process.
This is the main purpose of **datasets**.

The other use of datasets is showing which other loci (genes, markers, etc)
are present in the region in which a query of interest
(e.g. a marker associated to a QTL) has been found.

Therefore, a dataset contains the map positions of markers, genes or other loci, which have been
previously aligned and mapped. These positions can be retrieved using just the loci identifiers.

Creating a dataset takes 4 steps:
1. Choose a unique identifier for your dataset (*dataset_ID*).
1. Create a folder called *dataset_ID* under the path indicated by the *datasets_path*
entry in the *paths.conf* file (e.g. *barleymap/datasets/dataset_ID/*).
1. Create a file called *dataset_ID.map_ID*,
 for each map which will be associated to such dataset, and put it
in the folder created for the dataset in the previous step (e.g. *barleymap/datasets/dataset_ID/dataset_ID.map_ID*).
Note that these files could be created using *bmap_build_datasets*, as explained in following sections.
However, if it is desired to create the files manually,
see [format of the dataset-map files](https://github.com/Cantalapiedra/barleymap#format-of-the-dataset-map-files)
below for details.

1. Create a row in the conf/datasets.conf file, with **8 space-separated fields**:

  - Name: an arbitrary name for the dataset, used by the user to reference it and for printing purposes.
  Note that you could prefix the dataset name with a ">". This annotates the dataset to be ignored by the barleymap
  tool *bmap_build_datasets*, which is explained in following sections.
  - ID: a unique identifier for this dataset.
  - Type: either "genetic_marker", "gene", "map" or "anchored". This type is generally used only to filter the results
  so that the user can request to obtain only genes, or only genetic markers, for example, in the output.
  The "map" type is used when the dataset is also a map, so that when the data for the dataset is requested,
  it is obtained from the data of the map.
  - Filename: the raw data for the dataset (it is only required by the *bmap_build_datasets* tool, as explained later).
  - File type: either "fna", "bed", "gtf", or "map". The file type of the previous file.
  - Database list: either "ANY" or a database ID to which this dataset will be associated.
  - Synonyms file: path to the file of synonyms. This file can be used to store more than one name for each
  element of this dataset, so that the user can use any of the synonyms as query.
  - Prefix: if all the names of the loci of the dataset start with the same prefix and no other dataset contains
  elements with this prefix,
  specifying here such prefix will make searches on this dataset faster than without it.
  Note that by default a query (a locus ID) is searched in all the datasets. However, if the prefix of the query
  matches the prefix of one of the datasets, this query will be searched only in such dataset.

The *datasets.conf.sample* file shows 4 datasets as examples:

```
#name      unique_id  type            filename        file_type  db_list  synonyms_file             records_prefix
DATASET1   dataset1   genetic_marker  dataset1.fasta  fna        ANY      /home/user/dataset1.syns  no
DATASET2   dataset2   gene            dataset2.gtf    gtf        DB1,DB2  no                        DAT2_
>DATASET3  dataset3   anchored        dataset3.fasta  fna        ANY      no                        no
>DATASET4  dataset4   map             "maps_path"     map        DB3      no                        DAT3_
```

The first dataset ("DATASET1"), with ID "dataset1", is of type genetic marker ("genetic_marker"),
and its source are FASTA formatted sequences ("dataset1.fasta", "fna"). It is associated to
any database ("ANY"), it has a list of synonyms ("/home/user/dataset1.syns") and there is no prefix
shared by all its loci.

In contrast, the fourth dataset ("DATASET4") is used to create a map (map).
Note that its filename is indicated as "maps_path", and thus the data for this dataset corresponds to the
same file as the one used as map. It is associated to a single database ("DB3"), it has no synonyms
and all its loci have the prefix "DAT3_".

##### Format of the dataset-map files

A dataset-map file contains the map position of a set of commonly used markers, genes, etc. For example:

```
>Map2
#Marker   chr  cM                 multiple_positions  other_alignments
S_180989  1    0.106232294617565  No                  No
S_35790   1    0.21246458923513   No                  No
i_30945   1    3.64730878186969   No                  No
S_165910  1    3.68361907676158   No                  No
S_161137  1    4.10764872521246   No                  No
S_193700  1    4.10764872521246   No                  No
S_206684  1    4.10764872521246   No                  No
i_66630   1    4.95750708215297   No                  No
```

Note that this file has the same format as that of files for maps, and, as explained above, a map
can also be configured as a dataset.

As with files for maps, rows starting with ">" or "#" will be ignored,
so that it can be used for comments, map name or header fields.

Data rows have 5 or 6 (depending whether the map has cM, bp or both types of position) tab-delimited fields:

- Element identifier: ID of the marker, gene, etc.
- chr: ID of the chromosome from the map.
- cM, bp or both: 1 or 2 fields with numeric position within the map chromosome.
- Multiple positions: either "Yes" or "No", to indicate whether this dataset entry has more than one
position in this map.
- Other alignments: either "Yes" or "No", to indicate whether this dataset entry has more than one
alignment in this map, independently of whether has more than one position or not.

***

Once that at least one database, one map and one dataset have been correctly configured,
the following tools can be used:
- bmap_align_to_db
- bmap_align_to_map
- bmap_align
- bmap_find
- bmap_locate

#### 3.2.5 Annotations: the *datasets_annotation.conf* file

Datasets of type "gene" can be enriched with annotation data,
including a description text, a class of feature (to be defined by the admin of the app),
and lists of Gene Ontologies (GO), protein families (PFAM) and InterPro (IPR) identifiers.

Creating the annotation of a dataset of genes takes 4 steps:
- Choose a unique identifier for your annotation ("dataset_annot_ID").
- Create a folder "dataset_annot_ID" under the path indicated by the *annot_path* entry in the *paths.conf* file
 (e.g. *barleymap/datasets_annotation/dataset_annot_ID/*).
- Create a file for each annotation field for that dataset,
and put it in the folder created for the dataset annotation in the previous step
(e.g. *barleymap/datasets_annotation/dataset_annot_ID.desc.tab* for description texts).
See [format of the dataset annotation files]
(https://github.com/Cantalapiedra/barleymap#format-of-the-dataset-annotation-files)
below for details.

- Create a row in the *conf/datasets_annotation.conf* file, with 5 space-separated fields.

  - Annotation name: an arbitrary name for the dataset annotation.
  - Annotation ID: a unique identifier for this dataset annotation.
  - Dataset ID: the ID of the dataset to which this annotation is associated.
  - Filename: the name of the file with the dataset annotation, as chosen in the previous step.
  - Type: either "txt", "class", "go", "pfam", "ipr"; depending on the type of annotation.
  Note that there is another configuration file, *annotation_types.conf*,
  which has information about those types, and it is intended to be used to create custom annotation fields.
  However, currently that file should be left unmodified, as its full implementation is pending.

The *datasets.conf.sample* file shows the annotation of a single dataset:

```
#name      unique_id  dataset_unique_id  filename       type
DT2_DESC   dt2_desc   dataset2           dt2.desc.tab   txt
DT2_CLASS  dt2_class  dataset2           dt2.class.tab  class
DT2_GO     dt2_go     dataset2           dt2.go.tab     go
DT2_PFAM   dt2_pfam   dataset2           dt2.pfam.tab   pfam
DT2_IPR    dt2_ipr    dataset2           dt2.ipr.tab    ipr
```

All the 5 annotation fields have been annotated for *dataset2*. Note that you could leave some fields
without annotation if desired (for example, if a dataset lacks class data).

##### Format of the dataset annotation files

A dataset annotation file contain the identifier of the gene and the annotation field,
which will be either a text (description and class) or an identifier (GO, PFAM, IPR).
For example:

```
Gene000010	GO:0008270
Gene000040	GO:0006412
Gene000040	GO:0003735
Gene000040	GO:0005622
Gene000040	GO:0005840
Gene000090	GO:0004672
Gene000090	GO:0005524
```

## 4) Tools and algorithms

NOTE: in the web version of barleymap some of the options and parameters, which can be changed in
the standalone version, have been fixed. Check
[http://floresta.eead.csic.es/barleymap/help/](http://floresta.eead.csic.es/barleymap/help/).

### 4.1) Main tools

The main tools which barleymap provides, both in the standalone and in the web version,
are for **alignment** of sequences, **finding** markers, genes, etc, or **locate** features in a given position.

#### 4.1.1) Alignment of sequences

The alignment of sequences can be performed from the *Align sequences* button in barleymap web,
or using the command ***bmap_align*** in the standalone version.

In the standalone version, info and a full list of
**parameters** can be obtained running the tool with the "-h/--help" options:

```
Usage: bmap_align.py [OPTIONS] [FASTA_FILE]

typical: bmap_align.py --maps=map queries.fasta

Options:
  -h, --help            show this help message and exit
  --aligner=ALIGNER     Alignment software to use (default "gmap"). The "gmap"
                        option means to use only GMAP. The "blastn" option
                        means to use only Blastn. The "hsblastn" option means
                        to use only HS-Blastn. The order and aligners can be
                        explicitly specified by separating the names by ","
                        (e.g.: blastn,gmap --> First Blastn, then GMAP).
  --thres-id=THRES_ID   Minimum identity for valid alignments. Float between
                        0-100 (default 98.0).
  --thres-cov=THRES_COV
                        Minimum coverage for valid alignments. Float between
                        0-100 (default 95.0).
  --threads=N_THREADS   Number of threads to perform alignments (default 1).
  --maps=MAPS_PARAM     Comma delimited list of Maps to show.
  -b, --best-score      Will return only best score hits.
  --sort=SORT_PARAM     Sort results by centimorgan (cm) or basepairs (bp)
                        (default: defined for each map in maps configuration.
  -k, --show-multiples  Queries with multiple positions will be shown (are
                        obviated by default).
  -a, --anchored        Show anchored features at positions of queries.
  -g, --genes           Genes at positions of queries will be shown.
  -m, --markers         Additional markers at positions of queries will be
                        shown. Ignored if -g.
  -d, --show-all-features
                        All features will be used to enrich a map. By default,
                        only main datasets of each map are used to enrich.
  -o, --show-on-markers
                        Additional features will shown for each query. By
                        default, they are shown by interval of markers
  -e EXTEND_WINDOW, --extend=EXTEND_WINDOW
                        Centimorgans or basepairs (depending on sort) to
                        extend the search of -g or -m.(default 0.0)
  -u, --show-unmapped   Not found (unaligned, unmapped), will be shown.
  -c, --collapse        Mapping results and features (markers, genes) will be
                        shown at the same level.
  -f                    cM positions will be output with all decimals
                        (default, 2 decimals).
  -v, --verbose         More information printed.
```

The user provides one or more **FASTA formatted sequences** to be searched, which are the **queries**.
The user will choose also one or more **maps** (*--maps*), from which to obtain the position of the queries.

*Note that the user does not choose one or more sequence databases.
In fact, when he chooses a map, he is implicitly chosing the databases associated to that map
in the map configuration.*

The user can choose **alignment thresholds**: minimum alignment identity (*--thres-id*)
and minimum query coverage (*--thres-cov*).
He can also choose whether to obtain also a list of unmapped sequences (*-u*, *--show-unmapped*),
and whether to include or not as mapped those queries with more
than one position as result (*-k*, *--show-multiples*), or instead report them as unmapped.
In the case of maps which are both genetical and physical, the user can choose whether the results
will be sorted by cM or by bp (*--sort*).

The user may also choose whether to show only the resulting map, or also **information about datasets**, 
including genes (*-g*, *--genes*), markers (*-m*, *--markers*) or anchored (*-a*, *--anchored*) features in the region.
Note that these data can be shown only when they are in the
same position as each query (*-o*, *--show-on-markers*), or all data which can be found between each two queries.
In addition, in both cases, the user can choose to extend the search of datasets up- and down-stream
of the features positions (*-e*, *--extend*). Note that if the search is not extended (by default is 0.0) no information
will be shown between markers, even without the "*-o*, *--show-on-markers*" option.
Also, the user can choose whether to show information about main datasets
only (those associated to the map in the configuration file),
or about all the datasets with information for this map (*-d*, *--show-all-features*).

There are several parameters which can be changed in the **standalone version only**, and which are fixed
in the web version. The user can choose to obtain results only from those alignments
with the best score (*-b*, *--best-score*),
among those over the alignment thresholds. This is active by default in the web version.
Also, the user of the standalone version can choose the number of threads (*--threads*) to be used during alignment.
Note that these number of threads is actually given as parameter to the actual aligner (BLASTN, GMAP, HS-BLASTN, etc.)
and the actual barleymap process runs in a single core.
In the standalone version, the user can also change the verbosity which will be output to stderr (*-v*, *--verbose*),
and also whether the cM positions will be output with full decimals (*-f*) or formatted with 2 decimals (by default).
Finally, in the standalone version the information about datasets can be shown as additional columns in the results table,
or can be shown "inline" with the map results (*-c*, *--collapse*), using the same columns from the results table.

One important parameter is the **aligner** (or aligners), which can be changed in both the standalone (*--aligner*) and
in the web version. In the latter, there are some fixed options, using BLASTN only, GMAP only, or GMAP followed by BLASTN.
In the standalone version, either a single or a comma-separated list of aligners can be specified, and the aligners will
be used in that order (check the alignment algorithm below).

##### 4.1.1.1) Alignment algorithm

For all the databases of a given map,
barleymap searches all the queries in the first database, using the first aligner.
If there are queries which have not been found, it uses the next aligner in the same database.
If all the aligners have been used in this database, try with the next database, starting with the first aligner.
Repeat until all the queries have been found or there are no more databases and aligners to use.
With each query for which alignment targets have been found, search the map position of those targets,
and associate those positions to the corresponding queries.

In sort:
```
Given a list of unmapped queries *U*, a list of databases *D* from a map *m*, and a list of aligners *A*:
For each *d* in *D*,
for each *a* in *A*,
use *a* to search a target *t* in *d*, for each *q* in *U*.
Associate *q* to *t*.
Update *U*.
Break if *U* is empty.
End of loop.

For each *q* not in *U*, that is, each *q* associated to *t*:
Find a position *p* from *m* for *t*.
Report *p* as the position of *q*.
```

<sub style="font-size: 12px !important;">
Figure. Schematic representation of the barleymap "hierarchical" algorithm.
For the "greedy" algorithm all the query sequences are aligned to next database,
instead of just the unaligned ones. For the "exhaustive" algorithm, the "align to next database" arrow
should be moved to the box "Retrieve map positions" and change the tag "unaligned" to "unmapped".
</sub>
<p align="center">
  <img width="450" height="470" src="http://floresta.eead.csic.es/barleymap/img/barleymap_popseq.pipeline_2.png">
</p>

In addition there are three **versions of the algorithm**: "greedy", "hierarchical" and "exhaustive".
These versions cannot be specified as parameter of the application.
Instead, have to be associated to each of the maps in their configuration.

- In the "greedy" version, the list of unaligned queries is only updated for each database.
Therefore, every query is searched in every database.

- In the "hierarchical" version, a query is removed from the list of unaligned queries when an alignment
hit has been found for the query, regardless of whether the query has map position or not.

- In the "exhaustive" version, a query is removed from the list of unaligned queries when the query an alignment
hit has been found for the query, and a map position has been associated to it.

#### 4.1.2) Finding markers

Finding markers (or other datasets features, like genes, etc.) can be performed from the *Find markers*
button in barleymap web, or using the command ***bmap_find*** in the standalone version.

In the standalone version, info and a full list of
**parameters** can be obtained running the tool with the "-h/--help" options:

```
Usage: bmap_find.py [OPTIONS] [IDs_FILE]

typical: bmap_find.py --maps=map queries.ids

Options:
  -h, --help            show this help message and exit
  --maps=MAPS_PARAM     Comma delimited list of Maps to show.
  --sort=SORT_PARAM     Sort results by centimorgan (cm) or basepairs (bp)
                        (default: defined for each map in maps configuration.
  -k, --show-multiples  Queries with multiple positions will be shown (are
                        obviated by default).
  -a, --anchored        Show anchored features at positions of queries.
  -g, --genes           Genes at positions of queries will be shown. Ignored
                        if -a
  -m, --markers         Additional markers at positions of queries will be
                        shown. Ignored if -g or -a.
  -d, --show-all-features
                        All features will be used to enrich a map. By default,
                        only main datasets of each map are used to enrich.
  -o, --show-on-markers
                        Additional features will shown for each query. By
                        default, they are shown by interval of markers
  -e EXTEND_WINDOW, --extend=EXTEND_WINDOW
                        Centimorgans or basepairs (depending on sort) to
                        extend the search of -g or -m.(default 0.0)
  -u, --show-unmapped   Not found (unaligned, unmapped), will be shown.
  -c, --collapse        Mapping results and features (markers, genes) will be
                        shown at the same level.
  -f                    cM positions will be output with all decimals
                        (default, 2 decimals).
  -v, --verbose         More information printed.
```

Most of the parameters work the same as in the bmap_align command or the "Align sequences" web application.
Instead of FASTA formatted sequences, the input in this tool are identifiers of features (markers names, for example).
Therefore, there are some parameters not present in this tool, like the aligner choice or the alignment thresholds.
Note that, because of this, the positions stored and returned as output by this tool
were obtained with a specific set of parameters. This includes also the list of databases and the algorithm configured
for a given map when the positions were obtained by alignment.
Check [www.floresta.eead.csic.es/barleymap/](http://floresta.eead.csic.es/barleymap/)
for details about the datasets used in the web version.

#### 4.1.3) Locating features in region

Locating features (markers, genes, etc.) in a region can be performed from the *Locate by position*
button in barleymap web, or using the command ***bmap_locate*** in the standalone version.

In the standalone version, info and a full list of
**parameters** can be obtained running the tool with the "-h/--help" options:

```
Usage: bmap_locate.py [OPTIONS] [IDs_FILE]

typical: bmap_locate.py --maps=map queries.tab

Options:
  -h, --help            show this help message and exit
  --maps=MAPS_PARAM     Comma delimited list of Maps to show.
  --sort=SORT_PARAM     Sort results by centimorgan (cm) or basepairs (bp)
                        (default: defined for each map in maps configuration.
  -k, --show-multiples  Queries with multiple positions will be shown (are
                        obviated by default).
  -a, --anchored        Show anchored features at positions of queries.
  -g, --genes           Genes at positions of queries will be shown. Ignored
                        if -a
  -m, --markers         Additional markers at positions of queries will be
                        shown. Ignored if -g or -a.
  -d, --show-all-features
                        All features will be used to enrich a map. By default,
                        only main datasets of each map are used to enrich.
  -o, --show-on-markers
                        Additional features will shown for each query. By
                        default, they are shown by interval of markers
  -e EXTEND_WINDOW, --extend=EXTEND_WINDOW
                        Centimorgans or basepairs (depending on sort) to
                        extend the search of -g or -m.(default 0.0)
  -u, --show-unmapped   Not found (unaligned, unmapped), will be shown.
  -c, --collapse        Mapping results and features (markers, genes) will be
                        shown at the same level.
  -f                    cM positions will be output with all decimals
                        (default, 2 decimals).
  -v, --verbose         More information printed.
```

In this case each query is a map position, instead of a sequence or a marker identifier,
and it has 2 tab-separated fields:
- Chromosome or contig name.
- Position within that chromosome or contig.

The user input is a list of such map positions.

For example, for a physical map:

```
chr2	711398163
chr6	376635036
chr7	4184387
chr7	227367117
```

### 4.2) Secondary tools

As explained above, the main barleymap tools, including those in the web version,
return as result map positions for the queries. The hits from the alignment step remain
hidden for the user. However, in some cases alignment results are preferred.
These can be obtained with the secondary tools, which are available **only in the standalone version**.

***

The *bmap_align_to_db* command allows obtaining the alignment results from FASTA formatted queries
to one or more databases. The parameters of *bmap_align_to_db* can be obtained running it with "-h/--help":

```
Usage: bmap_align_to_db.py [OPTIONS] [FASTA_FILE]

typical: bmap_align_to_db.py --databases=MorexGenome queries.fasta

Options:
  -h, --help            show this help message and exit
  --databases=DATABASES_PARAM
                        Comma delimited list of database names to align to
                        (default all).
  --databases-ids=DATABASES_IDS_PARAM
                        Comma delimited list of database IDs to align to
                        (default all).
  --aligner=ALIGNER     Alignment software to use (default "gmap"). The "gmap"
                        option means to use only GMAP. The "blastn" option
                        means to use only Blastn. The "hsblastn" option means
                        to use only HS-Blastn. The order and aligners can be
                        explicitly specified by separating the names by ","
                        (e.g.: blastn,gmap --> First Blastn, then GMAP).
  --thres-id=THRES_ID   Minimum identity for valid alignments. Float between
                        0-100 (default 98.0).
  --thres-cov=THRES_COV
                        Minimum coverage for valid alignments. Float between
                        0-100 (default 95.0).
  --threads=N_THREADS   Number of threads to perform alignments (default 1).
  --search=SEARCH_TYPE  Whether obtain the hits from all DBs (greedy), only
                        best score hits (best_score), or first hit found
                        (hierarchical); (default greedy).
  --ref-type=REF_TYPE   Whether use GMAP (std) or GMAPL (big), when using
                        --databases-ids only.
  -v, --verbose         More information printed.
```

Most of the parameters are the same used in the *bmap_align* command, and have already been explained above.
The *--databases* (or *--databases-ids*), *--search* and *--ref-type* parameters are the same as some of the
fields used to configure a map, and have also been explained (see Configuration of maps).

The result of *bmap_align_to_db* is a table with 12 fields:
- query_id: the name of the FASTA query.
- subject_id: the chromosome or contig from the alignment hit.
- identity: the percentage of identity from the alignment.
- query_coverage: the percentage of coverage of the query in the alignment.
- score: a score which corresponds to the bit score from blastn and to barleymap specific score for
GMAP alignments, which takes into account both identity and query coverage.
- strand: to which strand of the subject was aligned the query.
- qstart: first position of the query in the alignment.
- qend: last position of the query in the alignment.
- sstart: first position of the subject in the alignment.
- send: last position of the subject in the alignment.
- database: to which database belongs the subject.
- algorithm: which algorithm was used to perform the alignment.

Note that rows starting with ">" or "#" are for database name and column headers, respectively.
An example of the output file from bmap_align_to_db:

```
>DB:150831_barley_pseudomolecules
#query_id  subject_id  identity  query_coverage  score  strand  qstart  qend  sstart     send       database   algorithm
m_10235    chr1        100.00    100.00          120.0  -       1       121   80265474   80265594   genome2.0  gmap
m_19       chr7        100.00    100.00          196.0  -       1       197   17091119   17091315   genome2.0  gmap
m_10       chr1        100.00    100.00          210.0  +       1       211   71173958   71174168   genome2.0  gmap
m_1100     chr5        100.00    100.00          178.0  +       1       179   434303690  434303868  genome2.0  gmap
m_1012     chr2        100.00    100.00          226.0  +       1       227   29125654   29125880   genome2.0  gmap
```

***

The *bmap_align_to_map* command allows obtaining the alignment results from FASTA formatted queries
to one or more maps, i.e. to the databases which have been configured in barleymap for those maps
(see configuration of maps). The parameters of *bmap_align_to_map* can be obtained running it with "-h/--help":

```
Usage: bmap_align_to_map.py [OPTIONS] [FASTA_FILE]

typical: bmap_align_to_map.py --maps=MorexGenome queries.fasta

Options:
  -h, --help            show this help message and exit
  --maps=MAPS_PARAM     Comma delimited list of Maps to show (default all).
  --aligner=ALIGNER     Alignment software to use (default "gmap"). The "gmap"
                        option means to use only GMAP. The "blastn" option
                        means to use only Blastn. The "hsblastn" option means
                        to use only HS-Blastn. The order and aligners can be
                        explicitly specified by separating the names by ","
                        (e.g.: blastn,gmap --> First Blastn, then GMAP).
  --thres-id=THRES_ID   Minimum identity for valid alignments. Float between
                        0-100 (default 98.0).
  --thres-cov=THRES_COV
                        Minimum coverage for valid alignments. Float between
                        0-100 (default 95.0).
  --threads=N_THREADS   Number of threads to perform alignments (default 1).
  --search=SEARCH_TYPE  Whether obtain the hits from all DBs (greedy), only
                        best score hits (best_score), or first hit found
                        (hierarchical); (default greedy).
  -v, --verbose         More information printed.
```

Most of the parameters are the same used in the *bmap_align* command, and have already been explained above.
The *--search* parameter would override the algorithm configured as default for the map.

The result of *bmap_align_to_map* is a table with the same format as that of *bmap_align_to_db* (see above).

Note that rows starting with ">" correspond to maps names.
An example of the output file from bmap_align_to_map:

```
>>Map:morex_genome
#query_id   subject_id  identity  query_coverage  score   strand  qstart  qend  sstart    send      database                       algorithm
i_11_20855  chr1H       99.20     100.00          238.08  +       1       241   81133442  81133992  150831_barley_pseudomolecules  gmap
i_12_10235  chr1H       100.00    100.00          120.0   -       1       121   80265474  80265594  150831_barley_pseudomolecules  gmap
i_BK_19     chr7H       100.00    100.00          196.0   -       1       197   17091119  17091315  150831_barley_pseudomolecules  gmap
i_BK_10     chr1H       100.00    100.00          210.0   +       1       211   71173958  71174168  150831_barley_pseudomolecules  gmap
i_11_10030  chr1H       98.30     100.00          235.92  +       1       241   13590814  13591054  150831_barley_pseudomolecules  gmap
```

### 4.3) Configuration tools

These are several tools which are included with barleymap, but do not perform searches in the
barleymap configured resources. These are intended to help in the configuration of the application,
specially when dealing with datasets. Note that these tools use the barleymap main tools from the standalone version,
and therefore are included **only in the standalone version**. These tools could be used
with the standalone version to check or create resources to be used with barleymap web version though.

***

The *bmap_config* command returns a report including all the resources which have been configured with
the app, including:
- Paths (from paths.conf).
- Databases (from databases.conf).
- External databases: these are databases not included in the databases.conf file but which are found in the same
folder as configured databases. These databases can be used with the bmap_align_to_db tool
by means of the --databases-ids parameter.
- Maps (from maps.conf).
- Datasets and their annotations (from datasets.conf and datasets_annotation.conf).

***

The *bmap_build_datasets* is a script which uses the *datasets.conf* file as input, and tries to generate
the files for those datasets (markers, genes, maps, etc.), to be included as resources in barleymap.

Lets say that the user has a number of files from markers of genes which he wants to use as datasets in barleymap.
The user must configure the *datasets.conf* file, in which the files with the data for those datasets will be referenced.
Then, the user could need to generate the files with the actual positions of those
datasets to the maps, so that they can be retrieved by barleymap. Basically, we would need to perform alignments with
FASTA sequences, reformat gtf or bed files, etc. In turn, the user can use the *bmap_build_datasets*, which will
run *bmap_align* for datasets of type FASTA, and will reformat GTF and BED files, etc. Then the user just will need
to put those files under the appropiate directory where barleymap has been configured to read datasets.

When there are datasets which the user wants to keep in the configuration file, but must not be processed
by *bmap_build_datasets*, the user can "comment" those datasets in the *datasets.conf* file with the prefix ">".
Note that if he uses "#" instead of ">" the dataset will be fully commented,
and will not be used at all by barleymap.

The parameters of *bmap_build_datasets* are:

```
Usage: bmap_build_datasets

Options:
  -h, --help            show this help message and exit
  --threads=N_THREADS   Number of threads to perform alignments (default 1).
  --dataset=DATASET_PARAM
                        A single dataset to process. By default all datasets
                        are processed.
  -v, --verbose         More information printed.
```

The *--threads* parameter will be used as input for datasets of type FASTA (to perform the alignments).

Also the user can run the *bmap_build_datasets* for a single dataset (*--dataset* parameter),
for example when a new dataset is to be added to a barleymap application for which the other datasets
had already been created previously.

***

The *bmap_datasets_index* is used to create an index file for the datasets.
Currently, the script can be run for only a single dataset. For example, to process
the *datasets.conf* file the user would need to loop over the file externally and run
*bmap_datasets_index* for each of the iteration steps with:

```
bmap_datasets_index current_dataset
```

Note that the *current_dataset* is the file which barleymap uses to read the dataset (i.e. the one which could
be generated with *bmap_build_datasets*).
As a result, *bmap_datasets_index* returns a file called "current_dataset.idx", which should be placed in the same
directory where the *current_dataset* file is located and read by barleymap.

Note that for large dataset files, using index files will make the retrieval of markers, genes, etc. faster,
whereas for small dataset files is likely better to not use index files.

README is part of Barleymap.
Copyright (C)  2013-2014  Carlos P Cantalapiedra.
(terms of use can be found within the distributed LICENSE file).
#!/usr/bin/perl

# modified by CPCantalapiedra for Barleymap web (20170302)
# modified by CPCantalapiedra for Barleymap web (20140321) from previous
# modifications (see below).
# This version adds features and simplifies the program so that just those functions
# used by Barleymap web (http://floresta.eead.csic.es/barleymap/) are implemented.

# modified by Bruno Contreras Moreira EEAD-CSIC based on:

# $Revision: 0.5 $
# $Date: 2013/11/06 $
# $Id: genetic_mapper.pl $
# $Author: Michael Bekaert $
#
# SVG Genetic Map Drawer
# Copyright 2012-2013 Bekaert M <mbekaert@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# POD documentation - main docs before the code

=head1 NAME

Genetic-mapper - SVG Genetic Map Drawer

=head1 DESCRIPTION

Perl script for creating a publication-ready genetic/linkage map in SVG format. The
resulting file can either be submitted for publication and edited with any vectorial
drawing software like Inkscape and Abobe Illustrator.

The input file must be a CSV file with at least the marker name (ID) [string], linkage
group (Chr) [numeric], and the position (Pos) [numeric]. Additionally a LOD score or
p-value can be provided. Any extra parameter will be ignore.

	ID,Chr,Pos,LOD
	13519,12,0,0.250840894
	2718,12,1.0,0.250840893
	11040,12,1.6,0.252843341
	...

=head1 FEEDBACK

User feedback is an integral part of the evolution of this modules. Send your
comments and suggestions preferably to author.

=head1 AUTHOR

B<Michael Bekaert> (mbekaert@gmail.com)

The latest version of genetic_mapper.pl is available at

  http://genetic-mapper.googlecode.com/

=head1 LICENSE

Copyright 2012-2013 - Michael Bekaert

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

=cut

use strict;
use warnings;
use Getopt::Long;

#----------------------------------------------------------
our ($VERSION) = 0.5;

#----------------------------------------------- CONSTANTS
my @font   = ('Helvetica', 4, 12, 8);

my $ADDCMTOEQUALLOCS = 0.1;
my $MAXGENESSAMESPOT = 3;
my $ANCHORCOLOR = '#000000';
my $RESTCOLOR   = '#FF0000';
my $div = 1;

my $PHYS_MAP_SCALE = 30;

my $MAX_PER_CHR = 30; # Maximum number of markers in chromosome to paint the text and all the lines

my $GEN_MAP_SEP = 120; # Initial separator for genetic maps
my $GEN_MAP_CHR_WIDTH = 200; # Fixed width for every chromosome in genetic maps
my $PHYS_MAP_SEP = 120; # Initial separator for physical maps
my $PHYS_MAP_CHR_WIDTH = 200; # Fixed width for every chromosome in physical maps

my $CHR_WIDTH = 20;
my $CHR_HEIGHT = 160;

#----------------------------------------------------------
my $verbose = 0;
my $shify = 30;
my $map;
my $chrom_order;
my $chrommax = 0;
my $map_as_physical;
my $finemapping; # whether show complete chromosomes or only the mapped region
my $pos_position = 2;

GetOptions('m|map=s' => \$map,
	   'o|chrom-order=s' => \$chrom_order,
	   'chrommax:f' => \$chrommax,
	   'pos_position:f' => \$pos_position,
	   'map_as_physical!' => \$map_as_physical,
	   'fine_mapping!' => \$finemapping,
	   'v|verbose!' => \$verbose);

# chrommax: position on chrom_order file of the maximum size of chromosomes

################################### Read chromosome name and order from provided file
### --> chrom_conf{chrom_name} = "order", "max"
### rev_chrom_conf{chrom_order} -> "name", "max"
my (%chrom_conf);
my (%rev_chrom_conf);
my ($maxmax); # maximum position of all chromosomes

print STDERR "Parsing map chromosomes configuration\n";

if (defined $chrom_order && -r $chrom_order && (open my $IN, '<', $chrom_order))
{
    while (<$IN>)
    {
	print {*STDERR} $_;
	chomp;
	my @data = split m/\t/;
	
	$chrom_conf{$data[0]}{"order"} = $data[1];
	
	if ($finemapping){
	    $chrom_conf{$data[0]}{"max"} = -1; # to be defined from map positions
	    $chrom_conf{$data[0]}{"min"} = -1;
	} else {
	    $chrom_conf{$data[0]}{"max"} = $data[$chrommax]; # as defined in the chromosomes file
	    $chrom_conf{$data[0]}{"min"} = 1;
	}
	
	$chrom_conf{$data[0]}{"num"} = 0; # num of markers on this chromosome
	
	$rev_chrom_conf{$data[1]}{"name"} = $data[0];
	
	if ($finemapping){
	    $rev_chrom_conf{$data[1]}{"max"} = -1; # to be defined from map positions
	    $rev_chrom_conf{$data[1]}{"min"} = -1; # to be defined from map positions
	} else {
	    $rev_chrom_conf{$data[1]}{"max"} = $data[$chrommax]; # as defined in the chromosomes file
	    $rev_chrom_conf{$data[1]}{"min"} = 1; # as defined in the chromosomes file
	}
	
	$rev_chrom_conf{$data[1]}{"num"} = 0; # num of markers on this chromosome
	
	# Maximum of all chromosomes
	if ($finemapping) {
	    $maxmax = -1; # to be defined from map positions
	} else {
	    $maxmax = $data[$chrommax] if (!defined $maxmax || $maxmax < $data[$chrommax]);
	}
    }
    close $IN;
}
#######################################################################################

########################################################################## Process maps
### --> chromosomes{chrom_id}{$location}
if (defined $map && -r $map && (open my $IN, '<', $map))
{
    my (@final);
    my (%chromosomes, %max, %anchor, %div_dict, %num_features, %max_locus_site);
    my (%previous_locations,%anchor_locations,$new_location,$extra);
    my ($maxlog,$chromosomeid,$location,$marker,$color,$maxlabel,$currchrom);
    
    # Variables used inside CHROMOSOME LOOP
    my ($chr_text_x,$chr_text_y);
    
    # Variables used inside LOCI LOOP
    my ($locus2,$size,$position,$shpos,$x_pos,$y_pos,$label,$legend_x,$legend_y);
    
    my $sep = $GEN_MAP_SEP; # this changes if map_as_physical
    my $chr_width = $GEN_MAP_CHR_WIDTH; # this changes if map_as_physical
    my $yshift = $sep; # x position for first chromosome
    
    ## Parse input file
    ##
    #<$IN>; # skip first line O.,o
    while (<$IN>)
    {
        chomp;
	next if (m/^#/);
	next if (m/^>/);
	#print {*STDERR} $_;
        my @data = split m/\t/;
	
        if (scalar @data > 2 && defined $data[1])
        {
	    $currchrom = $data[1];
	    $chromosomeid = int($chrom_conf{$currchrom}{"order"});
	    
	    $location = int($data[$pos_position]); # int($data[$pos_position] * 1000);
	    
	    $chrom_conf{$currchrom}{"num"} = $chrom_conf{$currchrom}{"num"} + 1;
	    $rev_chrom_conf{$chromosomeid}{"num"} = $rev_chrom_conf{$chromosomeid}{"num"} + 1;
	    
	    $marker = $data[0];
	    
	    # 1st read anchor marker
	    ## Needed for multiple position markers? CPC
	    if(!$anchor{$marker})
	    {
		$anchor{$marker}=1; 
	    }
	    
	    if($anchor_locations{$location})
	    {
		$anchor_locations{$location}++; 
		$location += ($ADDCMTOEQUALLOCS * $anchor_locations{$location});
	    } else {
		$anchor_locations{$location}++;
	    }	#print "a $marker $location\n";
	    
	    if (!exists $chromosomes{$chromosomeid}{$location})
	    {
		@{$chromosomes{$chromosomeid}{$location}} = ($data[0], 1, -1);
	    } else {
		$chromosomes{$chromosomeid}{$location}[0] .= q{,} . $marker;
		$chromosomes{$chromosomeid}{$location}[1] += 1;
		$chromosomes{$chromosomeid}{$location}[2] += 0;
	    }
	    
	    if (!exists $num_features{$chromosomeid}) {
		$num_features{$chromosomeid} = 1;
	    } else {
		$num_features{$chromosomeid} += 1;
	    }
	    
	    # If finemapping: update minimum and maximum chromosome positions
	    if ($finemapping) {
		if ($location <= $chrom_conf{$currchrom}{"min"} || $chrom_conf{$currchrom}{"min"} == -1) {
		    $chrom_conf{$currchrom}{"min"} = $location;
		    $rev_chrom_conf{$chromosomeid}{"min"} = $location;
		}
		
		if ($location >= $chrom_conf{$currchrom}{"max"} || $chrom_conf{$currchrom}{"max"} == -1) {
		    $chrom_conf{$currchrom}{"max"} = $location;
		    $rev_chrom_conf{$chromosomeid}{"max"} = $location;
		}
		
		$maxmax = $location if (!defined $maxmax || $maxmax < $location || $maxmax == -1);
	    }
	    
        }
    }
    close $IN;
    
    #print STDERR "Max chromosome size:".$maxmax."\n";
    
    if ($map_as_physical) {
	$sep = $PHYS_MAP_SEP;
	$chr_width = $PHYS_MAP_CHR_WIDTH;
    } else {
	$sep = $GEN_MAP_SEP;
	$chr_width = $GEN_MAP_CHR_WIDTH;
    }
    $yshift = $sep; # x position for first chromosome
    
    if (scalar keys %chromosomes > 0)
    {
	### CHROMOSOME LOOP
        my $i = 0;
        foreach my $chrnum (sort { $a <=> $b } keys %chromosomes)
        {
	    my $chromname = $rev_chrom_conf{$chrnum}{"name"};
	    my $chrom_max = $rev_chrom_conf{$chrnum}{"max"};
	    my $chrom_min = $rev_chrom_conf{$chrnum}{"min"};
	    my $chrom_num = $rev_chrom_conf{$chrnum}{"num"};
	    
	    print {*STDERR} "Chrom: ".$chromname." ".$chrnum." ".$chrom_max." ".$chrom_min." ".$maxmax."\n";
	    
            $yshift += ($sep + $chr_width) if ($i++ > 0); # x position for current chromosome
	    
            my (@legend);
            my $plast = -999;
	    
	    ############# Print the chromosome number
	    push @final, ' <g id="Layer_' . $chrnum . '">';
	    
	    $chr_text_x = $yshift + ($CHR_WIDTH / 2); # ($yshift + 22);
	    $chr_text_y = ((($shify + ((3 * $font[3]) / 2)) / 2) - $font[1]);
	    
            push @final, '  <text class="text" style="font-size:' . ((3 * $font[3]) / 2) . 'pt;" text-anchor="middle" \
			    x="' . $chr_text_x . '" y="' . $chr_text_y . '">' . $chromname . '</text>';
	    #########################################
	    
	    #### LOCI LOOP
            foreach my $locus (sort {$a<=>$b} keys %{$chromosomes{$chrnum}})
            {
		# position of this locus
		# note that $chrom_min + 1 will be 0 when not finemapping, and chrom min position when finemapping
		if ($finemapping) {
		    if ($chrom_max - $chrom_min <= 0) {
			$locus2 = $CHR_HEIGHT / 2; # If there is only one marker, show it in the middle of the chromosome track
		    } else {
			$locus2 = (($locus - $chrom_min) / ($chrom_max - $chrom_min)) * $CHR_HEIGHT;
		    }
		} else {
		    $locus2 = ($locus / $maxmax) * $CHR_HEIGHT;
		}
		
		#print {*STDERR} "Locus " . $locus . " - " . $locus2 . "\n";
		
		### This is the graphical position of the LABELS of the marker
		$position = ($locus2 >= $plast + $font[2] ? $locus2 : $plast + $font[2]);
		
		### This is the graphical position of the marker ON the chromosome
                $shpos = ($position - $locus2) * 1;
		
		### This is the position of labels plus the global vertical margin $shify
		$y_pos = ($shify + $position); #$locus2 + $shpos);
		
		#print {*STDERR} "\tPos: ".$position.", shpos: ".$shpos.", ypos: ".$y_pos."\n";
		
		### Plot the labels showing the numerical position of markers on the chromosomes
		###
		my $x_lab = ($yshift - 64);
		$legend_y = $y_pos + ($font[3] / 2);
		
		#$x_pos = ($yshift - 64);
		
		$label = "";
		if ($map_as_physical) {
		    $label = sprintf "%.0f", $locus;
		} else {
		    $label = sprintf "%.2f", $locus;
		}
		
		if ($MAX_PER_CHR >= $chrom_num) {
		    push @legend, '  <text class="text" text-anchor="end" x="' . $x_lab . '" y="' . $legend_y . '">' . $label . '</text>';
		}
		
		### Plot the paths which connect the labels and the marker ticks on the chromosomes
		###
		$x_lab = $x_lab + 8; #($yshift - 56); # leftmost position of the path
		my $tick = 6;
		my $leng = $chr_text_x - ($CHR_WIDTH / 2) - ($x_lab + $tick); #45;
		
		if ($MAX_PER_CHR >= $chrom_num) {
		    push @legend, '  <path class="line" d="M'
		    . $x_lab . q{ } . $y_pos
		    . 'h'.$tick.' l'.$leng.' -' . ($shpos) . ' l0 0'
		    . 'h' . $CHR_WIDTH . ' l'.$leng.' ' . ($shpos) . ' l0 0 h'.$tick.'"/>';
		    
		} else {
		    push @legend, '  <path class="line" d="M'. ($x_lab+$tick+$leng) . q{ } . ($y_pos-$shpos) . 'h' . $CHR_WIDTH . '"/>';
		}
		
		# if input are simply markers make sure they are treated as anchors
		if(!keys(%anchor)) {
		    $color = $ANCHORCOLOR
		} else {
		    if($anchor{$chromosomes{$chrnum}{$locus}[0]}){ $color = $ANCHORCOLOR }
		    else{ $color = $RESTCOLOR }
		}
		
		### Plot the marker name labels on the chromosomes
		###
		$legend_x = $x_lab + $tick + $leng + $CHR_WIDTH + $leng + $tick + 8; # + 105;
		
		if ($MAX_PER_CHR >= $chrom_num) {
		    push @legend, '  <text class="text" style="fill:'.$color.'" x="' . $legend_x . '" y="' . $legend_y . '">' .
				    $chromosomes{$chrnum}{$locus}[0] .
				    '</text>';
		}
		
		###
		
                $plast = $position; # previous label position (to shift the next one if necessary)
		
		if ($MAX_PER_CHR >= $chrom_num) {
		    $maxlabel = $y_pos if (!defined $maxlabel || $maxlabel < $y_pos);
		} else {
		    $maxlabel = ($y_pos-$shpos) if (!defined $maxlabel || $maxlabel < ($y_pos-$shpos));
		}
            }
	    # END OF LOCI LOOP
	    
	    if (!exists $max_locus_site{$chrnum}) {
		$max_locus_site{$chrnum} = $shify + $locus2;
	    }
	    
	    ##### Plot the graphical chromosomes
	    #####
	    my $bezier_height = 22.7;
	    my $rect_height = ($chrom_max / $maxmax) * $CHR_HEIGHT;
	    if ($finemapping) { # when finemapping, all chromosomes have the same length
		$rect_height = $CHR_HEIGHT;
	    }
	    
	    my $rect_start = $chr_text_x - ($CHR_WIDTH / 2);
	    my $rect_y_start = $chr_text_y + 2 + $rect_height;
	    my $rect_y_end = $rect_height - $bezier_height;
	    
	    push @final, '  <path class="chromosome" d="M '
	      . $rect_start . q{ } . $rect_y_start
	      . ' c 0 '.$bezier_height.' ' . $CHR_WIDTH . ' '.$bezier_height.' ' . $CHR_WIDTH . ' 0 ' # lower bezier
	      . ' v -' . $rect_y_end #$niidea_2
	      . " c 0 -".$bezier_height." -" . $CHR_WIDTH . ' -'.$bezier_height.' -' . $CHR_WIDTH . " 0 " # upper bezier
	      . " z\"/>\n  ";
	    
            push @final, '  </g>';
            push @final, @legend;
            push @final, ' </g>';
        }
	### END OF CHROMOSOME LOOP
	
	# maximum position for this karyotype
	# to adjust the svg height
	if ($maxlabel < $CHR_HEIGHT) {
	    $maxlabel = $CHR_HEIGHT;
	}
	
	my $svg_width = $yshift + $chr_width;
	my $svg_height = $maxlabel+60;#$font[3];
	
        print {*STDOUT} "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n\
	<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n";
	
        print {*STDOUT} '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="', $svg_width, '" height="', $svg_height, "\">\n";
        print {*STDOUT} " <defs>\n";
	
        print {*STDOUT} "  <style type=\"text/css\">\n   .text { font-size: ", $font[3], 'pt; fill: #000; font-family: ', $font[0], "; }\n   \
	.line { stroke:#000; stroke-width:", '1', "; fill:none; }\n";
        
	print {*STDOUT} "   .whiteline { stroke:#999; stroke-width:1.5; fill:none; }\n   \
		   .locus { fill:url(#lograd); }\n   \
		   .chromosome { fill:url(#bgrad); }\n";
	
        print {*STDOUT} "  </style>\n";
	
	print {*STDOUT}
	  "  <linearGradient id=\"bgrad\" x1=\"0%\" y1=\"0%\" x2=\"100%\" y2=\"0%\">\n   \
				<stop offset=\"0%\"   style=\"stop-color:#BBA\"/>\n   \
				<stop offset=\"50%\"  style=\"stop-color:#FFE\"/>\n   \
				<stop offset=\"100%\" style=\"stop-color:#BBA\"/>\n  \
	    </linearGradient>\n  \
	    <linearGradient id=\"lograd\" x1=\"0%\" y1=\"0%\" x2=\"100%\" y2=\"0%\">\n   \
				<stop offset=\"0%\"   style=\"stop-color:#000\"/>\n   \
				<stop offset=\"50%\"  style=\"stop-color:#666\"/>\n   \
				<stop offset=\"100%\" style=\"stop-color:#000\"/>\n  \
	    </linearGradient>\n";
	      
        print {*STDOUT} " </defs>\n";
        print {*STDOUT} join("\n", @final), "\n";
        print {*STDOUT} "</svg>\n";
    }
} else {
    print {*STDERR} "\n  ..:: SVG Genetic Map Drawer ::..\n  > Standalone program version $VERSION <\n\n  \
    Usage: $0 [-options] --map=<map.csv>\n\n   Options\n     --chr <string>\n           \
    Draw only the specified chromosome/linkage group.\n     \
    --bar\n           Use a coloured visualisation with a bark bar at the marker position.\n     \
    --plot\n           Rather than a list marker names, plots a circle. \
    If the LOD-score is\n provided a dark disk fill the circle proportionality to its value.\n     \
    --var\n           If specified with --bar or --plot the size of the bar/circle is\n  proportional to the number of markers.\n     \
    --square\n           Small squares are used rather than names (incompatible with --plot).\n     \
    --pos\n           The marker positions are indicated on the left site of the chromosome.\n     \
    --compact\n           A more compact/stylish chromosome is used (incompatible with --bar).\n     \
    --karyotype=<karyotype.file>\n           Specify a karytype to scale the physical chromosme. \
    Rather than using\n           genetic distances, expect nucleotide position in than map file.\n           \
    FORMAT: \"chr - ID LABEL START END COMMENT\"\n     \
    --scale= ]0,+oo[\n           Change the scale of the figure (default x10).\n     \
    --verbose\n           Become chatty.\n\n";
}

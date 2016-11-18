#!/usr/bin/perl

# modified by CPCantalapiedra for Barleymap web (20140321) from previous
# modifications (see below).
# This version adds features and simplifies the program so that just those functions
# used by Barleymap web (http://floresta.eead.csic.es/barleymap/) are implemented.

# --plot option is not supported.
# --square option is not supported.
# --compact option is not supported.

# Added:
# pos_position argument: to allow to specify in which position of the data resides the positional information
#			for example, if it is genetic/physical map, the position to show will depend
#			on the "sort" parameters chosen by the user...
# map_as_physical: it is required to specify whenever base pairs are used in the "pos_position"
#			field of the data.

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

=head1 SYNOPSIS

  # Command line help
  ..:: SVG Genetic Map Drawer ::..
  > Standalone program version 0.5 <

  Usage: genetic_mapper.pl [-options] --map=<map.csv>

   Options
     --chr=<name>
           Draw only the specified chromosome/linkage group.
     --bar
           Use a coloured visualisation with a dark bar at the marker position.
     --plot
           Rather than a list marker names, plots a circle. If the LOD-score is
           provided a dark disk fill the circle proportionality to its value.
     --var
           If specified with --bar or --plot the size of the bar/circle is
           proportional to the number of markers.
     --square
           Small squares are used rather than names (incompatible with --plot).
     --pos
           The marker positions are indicated on the left site of the chromosome.
     --compact
           A more compact/stylish chromosome is used (incompatible with --bar).
     --karyotype=<karyotype.file>
           Specify a karytype to scale the physical chromosme. Rather than using
           genetic distances, expect nucleotide position in than map file.
           FORMAT: "chr - ID LABEL START END COMMENT"
     --scale= ]0,+oo[
           Change the scale of the figure (default x10).
     --verbose
           Become chatty.

  # stylish
  ./genetic_mapper.pl --var --compact --plot --map=map.csv > lg13.svg

  # Classic publication style
  ./genetic_mapper.pl --pos --chr=13 --map=map.csv > lg13.svg

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

#----------------------------------------------------------
my ($verbose, $shify, $bar, $var, $pflag, $scale, $font, $karyotype, $map, $chr, $map_as_physical, $pos_position) = (0, 30, 0, 0, 10, 0, 0, 0, 2);
GetOptions('m|map=s' => \$map,
	   'scale:f' => \$scale,
	   'pos_position:f' => \$pos_position,
	   'map_as_physical!' => \$map_as_physical,
	   'bar!' => \$bar,
	   'var!' => \$var,
	   'p|pos|position!' => \$pflag,
	   'c|chr:s' => \$chr,
	   'v|verbose!' => \$verbose);

# 'k|karyotype:s' => \$karyotype,

my @font   = ('Helvetica', 4, 13, 10);
#my @font=('InaiMathi',4,13,11);
#my @font=('Optima',4,13,10);
#my @font=('Lucida Console',4,13,10);
#my @font=('Myriad Pro',4,13,10);

my $ADDCMTOEQUALLOCS = 0.1;
my $MAXGENESSAMESPOT = 3;
my $ANCHORCOLOR = '#000000';
my $RESTCOLOR   = '#FF0000';
my $div = 1;

my $PHYS_MAP_SCALE = 150;

my $GEN_MAP_SEP = 120; # Initial separator for genetic maps
my $GEN_MAP_CHR_WIDTH = 240; # Fixed width for every chromosome in genetic maps
my $PHYS_MAP_SEP = 140; # Initial separator for physical maps
my $PHYS_MAP_CHR_WIDTH = 250; # Fixed width for every chromosome in physical maps

my $CHR_WIDTH = 40; # NOTE: this is not a parameter that adapts the whole painting
# of chromosomes. It is only the background of the chromosome. Ticks for markers
# and other features wont adapt to this variable

if ($scale>0 && defined $map && -r $map && (open my $IN, '<', $map))
{
    my (@clips, @final);
    my (%chromosomes, %max, %anchor, %annot, %HC, %div_dict, %num_features, %max_locus_site);
    my (%previous_locations,%anchor_locations,$new_location,$extra);
    my ($maxmax,$maxlog,$chromosomeid,$location,$marker,$annot,$color,$maxlabel);
    
    # Variables used inside CHROMOSOME LOOP
    my ($niidea,$niidea_2,$chr_text_x,$chr_text_y);
    
    # Variables used inside LOCI LOOP
    my ($locus2,$size,$position,$shpos,$x_pos,$y_pos,$label,$legend_x,$legend_y);
    
    my $sep = $GEN_MAP_SEP; # this changes if map_as_physical
    my $chr_width = $GEN_MAP_CHR_WIDTH; # this changes if map_as_physical
    my $yshift = ($pflag ? $sep : 0); # x position for first chromosome
    my $laxtYlabels = 0;
    <$IN>;
    
    ## Reading input file
    while (<$IN>)
    {
        chomp;
	#print {*STDERR} $_;
        my @data = split m/\t/;
	
        if ((scalar @data > 2 && defined $data[1]) && (!defined $chr || $data[1] eq $chr))
        {
	    $chromosomeid = int($data[1]); # int($data[1] * 10) / 10;
	    if ($map_as_physical) {
		$location = int($data[$pos_position]); # int($data[$pos_position] * 1000);
	    } else {
		$location = int($data[$pos_position] * 100) / 100; # int($data[$pos_position] * 1000);
	    }
	    
	    $marker = $data[0];
	    $annot = '';

	    # 1st read anchor marker
	    if(!$anchor{$marker})
	    {
		$anchor{$marker}=1; 
	    }  ## Needed for multiple position markers? CPC
	    
	    if($anchor_locations{$location})
	    {
		$anchor_locations{$location}++; 
		$location += ($ADDCMTOEQUALLOCS * $anchor_locations{$location});
	    }
	    else{ $anchor_locations{$location}++; }	#print "a $marker $location\n";
	    
	    if (!exists $chromosomes{$chromosomeid}{$location})
	    {
		@{$chromosomes{$chromosomeid}{$location}} = ($data[0], 1, -1);
	    }
	    else
	    {
		$chromosomes{$chromosomeid}{$location}[0] .= q{,} . $marker;
		$chromosomes{$chromosomeid}{$location}[1] += 1;
		$chromosomes{$chromosomeid}{$location}[2] += 0;
	    }
	    
	    if (!exists $max{$chromosomeid} || $max{$chromosomeid} < $location) # $location / 1000)
	    {
		$max{$chromosomeid} = $location; # / $div;
		$maxmax = $max{$chromosomeid} if (!defined $maxmax || $maxmax < $max{$chromosomeid});
		if ($map_as_physical) {
		    $maxmax = $maxmax / $PHYS_MAP_SCALE;
		}
	    }
	    
	    if (!exists $num_features{$chromosomeid}) {
		$num_features{$chromosomeid} = 1;
	    } else {
		$num_features{$chromosomeid} += 1;
	    }
        }
    }
    close $IN;
    
    if ($map_as_physical) {
	$sep = $PHYS_MAP_SEP;
	$chr_width = $PHYS_MAP_CHR_WIDTH;
    } else {
	$sep = $GEN_MAP_SEP;
	$chr_width = $GEN_MAP_CHR_WIDTH;
    }
    $yshift = ($pflag ? $sep : 0); # x position for first chromosome
    
    if (scalar keys %chromosomes > 0)
    {
	### CHROMOSOME LOOP
        my $i = 0;
        foreach my $chrnum (sort { $a <=> $b } keys %chromosomes)
        {
            $yshift += (($pflag ? $sep : 0) + $chr_width) if ($i++ > 0); # x position for current chromosome
	    
            print {*STDERR} '***** Linkage Group ', $chrnum, " *****\n" if ($verbose);
            my (@locussite, @legend);
            my $plast = -999;
	    
	    #### LOCI LOOP
            foreach my $locus (sort {$a<=>$b} keys %{$chromosomes{$chrnum}})
            {
		#print {*STDERR} $locus . "\n";
		if ($map_as_physical) {
		    $locus2 = ($locus / $maxmax);
		    #print {*STDERR} "Locus " . $locus . " - " . $locus2 . "\n";
		} else {
		    $locus2 = $locus;
		}
		
                print {*STDERR} $locus2, "\t", $chromosomes{$chrnum}{$locus}[0], "\t", (defined $chromosomes{$chrnum}{$locus}[2] ? $chromosomes{$chrnum}{$locus}[2] : q{}), "\n" if ($verbose);
                $size = 5 + ($var ? ($chromosomes{$chrnum}{$locus}[1] * 0.05 * $scale) : 0);
                $position = ($locus2 >= ($plast + ($font[2] / $scale)) ? $locus2 : $plast + ($font[2] / $scale));
                $shpos = ($position - $locus2) * $scale;
		
                if ($bar)
                {
                    #push @locussite, '   <path class="locus" d="M' . ($yshift + 2) . q{ } . ($shify + ($locus2 * $scale) + ($size / 2)) . 'h40v-' . $size . 'h-40z"/>';
                    if ($pflag)
                    {
                        push @legend, '  <path class="line" d="M'
			. ($yshift - 5 - 12 - 39) . q{ } . ($shify + ($locus2 * $scale) + ($shpos))
			. 'h12 l45 -' . ($shpos) . ' l0 0'
			. 'h' . $CHR_WIDTH . ' l45 ' . ($shpos) . ' l0 0 h12"/>';
			
                        push @legend, '  <path class="whiteline" d="M'
			. ($yshift + 2) . q{ }
			. ($shify + ($locus2 * $scale))
			. 'h ' . $CHR_WIDTH . '"/>' if ($locus2 > 0 && $locus2 < $max{$chrnum});
                    }
                }
                if ($pflag) {
		    $x_pos = ($yshift - 105 + 41);
		    $y_pos = ($shify + ($locus2 * $scale) + $shpos + $font[1]);
		    
		    $label = "";
		    if ($map_as_physical) {
			$label = $locus;
		    } else {
			$label = sprintf "%.2f", $locus;
		    }
		    
		    push @legend, '  <text class="text" text-anchor="end" x="' . $x_pos . '" y="' . $y_pos . '">' . $label . '</text>';
		}
		
		# if input are simply markers make sure they are treated as anchors
		if(!keys(%anchor)){ $color = $ANCHORCOLOR }
		else
		{
		    if($anchor{$chromosomes{$chrnum}{$locus}[0]}){ $color = $ANCHORCOLOR }
		    else{ $color = $RESTCOLOR }
		}
		
		$legend_x = ($yshift + 105);
		$legend_y = ($shify + ($locus2 * $scale) + $shpos + $font[1]);
		
		push @legend, '  <text class="text" style="fill:'.$color.'" x="' . $legend_x . '" y="' . $legend_y . '">' . $chromosomes{$chrnum}{$locus}[0] . '</text>';
		
                $plast = $position;
		
		#print {*STDERR} "Last " . $laxtYlabels . "\n";
		$laxtYlabels = $shify + ($locus2 * $scale) + $shpos;  ############################## LAST LABEL #######################
		$maxlabel = $legend_y if (!defined $maxlabel || $maxlabel < $legend_y);
		#print {*STDERR} "Max " . $maxlabel . "\n";
            }
	    # END OF LOCI LOOP
	    
	    if (!exists $max_locus_site{$chrnum}) {
		$max_locus_site{$chrnum} = ($shify + ($locus2 * $scale) + ($size / 2));
	    }
	    
            if ($bar) {
		
		if ($map_as_physical) {
		    $niidea = ($shify + (($max{$chrnum} / $maxmax) * $scale) - 15.37);
		    $niidea_2 = ((($max{$chrnum} / $maxmax) * $scale) - 30.7);
		} else {
		    $niidea = ($shify + ($max{$chrnum} * $scale) - 15.37);
		    $niidea_2 = (($max{$chrnum} * $scale) - 30.7);
		}
		
		#### CLIPPING DOES NOT WORK PROPERLY WITH MOZILLA FIREFOX
#                push @clips,
#                  '  <clipPath id="clip_' . $chrnum
#                  . "\">\n   <path d=\"M "
#                  . ($yshift + 5) . q{ } . $niidea
#                  . ' c 0 22.7 ' . $CHR_WIDTH . ' 22.7 ' . $CHR_WIDTH . ' 0 ' # lower bezier
#		  . ' v -' . $niidea_2
#                  . " c 0 -22.7 -" . $CHR_WIDTH . ' -22.7 -' . $CHR_WIDTH . " 0 " # upper bezier
#		  . " z\"/>\n  "
#		  . "</clipPath>";
            }
	    
            push @final, ' <g id="Layer_' . $chrnum . '">';
	    
	    $chr_text_x = ($yshift + 22);
	    $chr_text_y = ((($shify + ((3 * $font[3]) / 2)) / 2) - $font[1]);
            push @final, '  <text class="text" style="font-size:' . ((3 * $font[3]) / 2) . 'pt;" text-anchor="middle" x="' . $chr_text_x . '" y="' . $chr_text_y . '">' . $chrnum . '</text>';
            if ($bar) {
		push @final, '   <g id="locii_' . $chrnum . '"';
		#### CLIPPING DOES NOT WORK PROPERLY WITH MOZILLA FIREFOX
		#push @final, ' clip-path="url(#clip_' . $chrnum . ")";
		push @final, "\">\n  ";
		
		my $rect_height = 0;
		if ($map_as_physical) {
		    $rect_height = $max_locus_site{$chrnum};
		    #$rect_height = ((2 * $shify) + (($max{$chrnum} / $maxmax) * $scale));
		} else {
		    $rect_height = $max_locus_site{$chrnum};
		    #$rect_height = ((2 * $shify) + ($max{$chrnum} * $scale));
		}
		
		#### CLIPPING DOES NOT WORK PROPERLY WITH MOZILLA FIREFOX
		#push @final, "<rect x=\"" . $yshift . '" y="20" width="40" height="' . $rect_height . '" fill="url(#bgrad)"/>';
		push @final, '  <path class="chromosome" d="M '
                  . ($yshift + 2) . q{ } . $niidea
                  . ' c 0 22.7 ' . $CHR_WIDTH . ' 22.7 ' . $CHR_WIDTH . ' 0 ' # lower bezier
		  . ' v -' . $niidea_2
                  . " c 0 -22.7 -" . $CHR_WIDTH . ' -22.7 -' . $CHR_WIDTH . " 0 " # upper bezier
		  . " z\"/>\n  ";
		
		#print {*STDERR} $yshift . " - " . "0" . " - " . "40" . " - " . $rect_height . " - " . $laxtYlabels . "\n";
		
	    } # ' . ((2 * $shify) + ($max{$chrnum} * $scale)) . '
	    
            push @final, @locussite;
            push @final, '  </g>';
            push @final, @legend;
            push @final, ' </g>';
        }
	### END OF CHROMOSOME LOOP
	
	if($laxtYlabels < ((2 * $shify) + ($maxmax * $scale)))
	{
	    if ($map_as_physical) {
		$laxtYlabels = ((2 * $shify) + ($PHYS_MAP_SCALE * $scale))
	    } else {
		$laxtYlabels = ((2 * $shify) + ($maxmax * $scale))
	    }
	}
	
	my $svg_width = (($yshift + $chr_width));
	my $svg_height = $maxlabel+40;#$font[3];
	
	#print {*STDERR} $maxmax . " - " . $laxtYlabels . " - " . $svg_height . "\n";
	
        print {*STDOUT} "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n";
        print {*STDOUT} '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="', $svg_width, '" height="', $svg_height, "\">\n";
        print {*STDOUT} " <defs>\n";
        if ($bar) { print {*STDOUT} join("\n", @clips), "\n"; }
        print {*STDOUT} "  <style type=\"text/css\">\n   .text { font-size: ", $font[3], 'pt; fill: #000; font-family: ', $font[0], "; }\n   .line { stroke:#000; stroke-width:", '1', "; fill:none; }\n";
        if ($bar) { print {*STDOUT} "   .whiteline { stroke:#999; stroke-width:1.5; fill:none; }\n   .locus { fill:url(#lograd); }\n   .chromosome { fill:url(#bgrad); }\n"; }
        print {*STDOUT} "  </style>\n";

        if ($bar)
        {
            print {*STDOUT}
              "  <linearGradient id=\"bgrad\" x1=\"0%\" y1=\"0%\" x2=\"100%\" y2=\"0%\">\n   <stop offset=\"0%\"   style=\"stop-color:#BBA\"/>\n   <stop offset=\"50%\"  style=\"stop-color:#FFE\"/>\n   <stop offset=\"100%\" style=\"stop-color:#BBA\"/>\n  </linearGradient>\n  <linearGradient id=\"lograd\" x1=\"0%\" y1=\"0%\" x2=\"100%\" y2=\"0%\">\n   <stop offset=\"0%\"   style=\"stop-color:#000\"/>\n   <stop offset=\"50%\"  style=\"stop-color:#666\"/>\n   <stop offset=\"100%\" style=\"stop-color:#000\"/>\n  </linearGradient>\n";
        }
        print {*STDOUT} " </defs>\n";
        print {*STDOUT} join("\n", @final), "\n";
        print {*STDOUT} "</svg>\n";
    }
} else {
    print {*STDERR} "\n  ..:: SVG Genetic Map Drawer ::..\n  > Standalone program version $VERSION <\n\n  Usage: $0 [-options] --map=<map.csv>\n\n   Options\n     --chr <string>\n           Draw only the specified chromosome/linkage group.\n     --bar\n           Use a coloured visualisation with a bark bar at the marker position.\n     --plot\n           Rather than a list marker names, plots a circle. If the LOD-score is\n           provided a dark disk fill the circle proportionality to its value.\n     --var\n           If specified with --bar or --plot the size of the bar/circle is\n           proportional to the number of markers.\n     --square\n           Small squares are used rather than names (incompatible with --plot).\n     --pos\n           The marker positions are indicated on the left site of the chromosome.\n     --compact\n           A more compact/stylish chromosome is used (incompatible with --bar).\n     --karyotype=<karyotype.file>\n           Specify a karytype to scale the physical chromosme. Rather than using\n           genetic distances, expect nucleotide position in than map file.\n           FORMAT: \"chr - ID LABEL START END COMMENT\"\n     --scale= ]0,+oo[\n           Change the scale of the figure (default x10).\n     --verbose\n           Become chatty.\n\n";
}

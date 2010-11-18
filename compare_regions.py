
'''



Copyright 2010 Wu Albert Cheng <albertwcheng@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

'''

import sys, glob, string



def read_chrom_regions( filename ):

	chrom_regions = {}
	
	infile = open( filename, 'r' )
	
	lines = infile.readlines()
	
	for line in lines[1:]:
		line = string.split( line, '\t' )
	
		try:
			chrom_regions[ line[0] ].append( [ int(line[1]), int(line[2]) ] )
		except KeyError:
			chrom_regions[ line[0] ] = [ [ int(line[1]), int(line[2]) ] ]
	
	infile.close
	
	for chrom in chrom_regions:
		chrom_regions[ chrom ].sort()

	return chrom_regions



def calculate_bp_length_chrom_regions( chrom_regions ):
	
	total_regions = 0
	total_bp = 0
	for chrom in chrom_regions:
		for region in chrom_regions[ chrom ]:
			total_regions += 1
			total_bp += region[1] - region[0]

	return total_regions, total_bp



def compare_two_chrom_regions( chrom_regions1, chrom_regions2 ):
	
	overlapped_bp = 0	
	for chrom1 in chrom_regions1:
		skip_count = 0
		for region1 in chrom_regions1[ chrom1 ]:
			if chrom_regions2.has_key( chrom1 ):
				for region2 in chrom_regions2[ chrom1 ][skip_count:]:
					if region1[0] <= region2[0] <= region1[1] or region2[0] <= region1[0] <= region2[1]:
						overlapped_bp += min( region1[1], region2[1] ) - max( region1[0], region2[0] )
					elif region2[0] > region1[1]:
						break
					elif region1[0] > region2[1]:
						skip_count += 1
	return overlapped_bp

genome_length = 2000000000

file_list = glob.glob( 'ENRICHED_REGIONS*' )
list_chrom_regions = []
for filename in file_list:
	list_chrom_regions.append( read_chrom_regions( filename ) )


outfile = open( 'comparison_matrix.txt', 'w' )
outfile.write( 'NAME' + '\t' + 'REGIONS' + '\t' + 'BP' + '\t' + string.join( file_list, '\t' ) + '\n' )

for filename_counter, chrom_regions1 in enumerate( list_chrom_regions ):
	total_regions1, total_bp1 = calculate_bp_length_chrom_regions( chrom_regions1 )
	print file_list[ filename_counter ]
	outfile.write( file_list[ filename_counter ] + '\t' + str( total_regions1 ) + '\t' + str( total_bp1 ) )
	for chrom_regions2 in list_chrom_regions:
		total_regions2, total_bp2 = calculate_bp_length_chrom_regions( chrom_regions2 )
		overlapped_bp = compare_two_chrom_regions( chrom_regions1, chrom_regions2 )
		score = ( float(overlapped_bp) / float(total_bp1)) / ( float(total_bp2) / float(genome_length) )
		mean1 = float( total_bp1 ) / genome_length
		mean2 = float( total_bp2 ) / genome_length
		stdev1 = pow( ( pow( 1 - mean1, 2) * float(total_bp1) + pow( mean1, 2) * float( genome_length - total_bp1 ) ) / float(genome_length), 0.5 )
		stdev2 = pow( ( pow( 1 - mean2, 2) * float(total_bp2) + pow( mean2, 2) * float( genome_length - total_bp2 ) ) / float(genome_length), 0.5 )
		correlation = ( float(overlapped_bp) - float(genome_length)* mean1 * mean2 ) / ( float(genome_length-1) * stdev1 * stdev2 )
		if correlation < 0:
			correlation = ( float(overlapped_bp+100) - float(genome_length)* mean1 * mean2 ) / ( float(genome_length-1) * stdev1 * stdev2 )
			if correlation < 0:
				min_correlation = ( float(0) - float(genome_length)* mean1 * mean2 ) / ( float(genome_length-1) * stdev1 * stdev2 )
				normalized_correlation = -pow( correlation / min_correlation, 0.85 )
			else:
				min_correlation = 0
				normalized_correlation = 0
			print total_bp1, total_bp2, overlapped_bp, score, correlation, min_correlation, normalized_correlation
		elif correlation > 0:
			max_correlation = ( float( min( total_bp1, total_bp2 ) ) - float(genome_length)* mean1 * mean2 ) / ( float(genome_length-1) * stdev1 * stdev2 )
			normalized_correlation = pow( correlation / max_correlation, 0.85 )
			print total_bp1, total_bp2, overlapped_bp, score, correlation, max_correlation, normalized_correlation
			


		outfile.write( '\t' + str( normalized_correlation ) )
	outfile.write( '\n' )\


outfile.close()
